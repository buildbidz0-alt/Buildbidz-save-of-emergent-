from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import uuid
import jwt
import razorpay
import json
import logging
from pathlib import Path
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"

# Razorpay client
razorpay_client = razorpay.Client(auth=(os.environ['RAZORPAY_KEY_ID'], os.environ['RAZORPAY_KEY_SECRET']))
SUBSCRIPTION_AMOUNT = int(os.environ['SUBSCRIPTION_AMOUNT'])  # ₹5000 per month in paise

# Admin credentials
ADMIN_EMAIL = os.environ['ADMIN_EMAIL']
ADMIN_PASSWORD = os.environ['ADMIN_PASSWORD']

# Support contact
SUPPORT_PHONE = os.environ['SUPPORT_PHONE']
SUPPORT_EMAIL = os.environ['SUPPORT_EMAIL']

# Create the main app
app = FastAPI(title="BuildBidz API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Models
class UserRole(str):
    BUYER = "buyer"
    SUPPLIER = "supplier" 
    ADMIN = "admin"
    SALESMAN = "salesman"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    contact_phone: str
    role: str
    gst_number: Optional[str] = None
    address: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    company_name: str
    contact_phone: str
    role: str
    gst_number: Optional[str] = None
    address: Optional[str] = None
    is_verified: bool = False
    subscription_status: str = "trial"  # trial, active, expired, inactive
    subscription_expires_at: Optional[datetime] = None
    trial_expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_phone: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str

class JobCategory(str):
    MATERIAL = "material"
    LABOR = "labor"
    MACHINERY = "machinery"

class JobPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    category: str
    description: str
    quantity: Optional[str] = None
    location: str
    delivery_timeline: str
    budget_range: Optional[str] = None
    posted_by: str  # user_id
    status: str = "open"  # open, awarded, closed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    file_urls: List[str] = []

class JobPostCreate(BaseModel):
    title: str
    category: str
    description: str
    quantity: Optional[str] = None
    location: str
    delivery_timeline: str
    budget_range: Optional[str] = None

class Bid(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    supplier_id: str
    price_quote: float
    delivery_estimate: str
    notes: Optional[str] = None
    status: str = "submitted"  # submitted, awarded, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BidCreate(BaseModel):
    price_quote: float
    delivery_estimate: str
    notes: Optional[str] = None

class SalesmanBidCreate(BaseModel):
    price_quote: float
    delivery_estimate: str
    notes: Optional[str] = None
    # Company details for unregistered companies
    company_name: str
    company_contact_phone: str
    company_email: Optional[str] = None
    company_gst_number: Optional[str] = None
    company_address: Optional[str] = None

class PaymentOrder(BaseModel):
    amount: int = SUBSCRIPTION_AMOUNT
    currency: str = "INR"

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    sender_id: str
    receiver_id: str
    message: str
    file_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False

class ChatMessageCreate(BaseModel):
    message: str
    file_url: Optional[str] = None

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Handle admin user separately
        if user_id == "admin":
            admin_user = User(
                id="admin",
                email=ADMIN_EMAIL,
                company_name="BuildBidz Admin",
                contact_phone=SUPPORT_PHONE,
                role=UserRole.ADMIN,
                is_verified=True,
                subscription_status="active"
            )
            return admin_user
        
        # Handle salesman users
        if user_id in ["salesman1", "salesman2"]:
            salesman_emails = {
                "salesman1": "salesman1@buildbidz.co.in",
                "salesman2": "salesman2@buildbidz.co.in"
            }
            salesman_names = {
                "salesman1": "BuildBidz Sales Team 1",
                "salesman2": "BuildBidz Sales Team 2"
            }
            
            salesman_user = User(
                id=user_id,
                email=salesman_emails[user_id],
                company_name=salesman_names[user_id],
                contact_phone=SUPPORT_PHONE,
                role=UserRole.SALESMAN,
                is_verified=True,
                subscription_status="active"
            )
            return salesman_user
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def require_buyer(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.BUYER:
        raise HTTPException(status_code=403, detail="Only buyers can access this resource")
    return current_user

async def require_supplier(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPPLIER:
        raise HTTPException(status_code=403, detail="Only suppliers can access this resource")
    return current_user

async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def require_salesman(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SALESMAN:
        raise HTTPException(status_code=403, detail="Salesman access required")
    return current_user

async def require_admin_or_salesman(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.SALESMAN]:
        raise HTTPException(status_code=403, detail="Admin or Salesman access required")
    return current_user

async def require_active_subscription_or_trial(current_user: User = Depends(require_buyer)):
    # Check if user is in trial period
    if current_user.subscription_status == "trial":
        if not current_user.trial_expires_at or current_user.trial_expires_at > datetime.utcnow():
            return current_user
    
    # Check if user has active subscription
    if current_user.subscription_status == "active":
        if not current_user.subscription_expires_at or current_user.subscription_expires_at > datetime.utcnow():
            return current_user
    
    raise HTTPException(status_code=402, detail="Active subscription or trial required")

def generate_reset_code():
    return str(secrets.randbelow(1000000)).zfill(6)

# Auth endpoints
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user with 1-month free trial for buyers
    hashed_password = hash_password(user_data.password)
    trial_expires = datetime.utcnow() + timedelta(days=30) if user_data.role == UserRole.BUYER else None
    
    user = User(
        email=user_data.email,
        company_name=user_data.company_name,
        contact_phone=user_data.contact_phone,
        role=user_data.role,
        gst_number=user_data.gst_number,
        address=user_data.address,
        is_verified=user_data.role == UserRole.SUPPLIER,
        subscription_status="trial" if user_data.role == UserRole.BUYER else "active",
        trial_expires_at=trial_expires
    )
    
    await db.users.insert_one({**user.dict(), "password": hashed_password})
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "message": "Registration successful"
    }

@api_router.post("/auth/login")
async def login(login_data: UserLogin):
    # Check for admin login
    if login_data.email == ADMIN_EMAIL and login_data.password == ADMIN_PASSWORD:
        admin_user = User(
            id="admin",
            email=ADMIN_EMAIL,
            company_name="BuildBidz Admin",
            contact_phone=SUPPORT_PHONE,
            role=UserRole.ADMIN,
            is_verified=True,
            subscription_status="active"
        )
        access_token = create_access_token(data={"sub": "admin"})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": admin_user
        }
    
    # Check for salesman logins
    salesman_accounts = {
        "salesman1@buildbidz.co.in": {
            "id": "salesman1",
            "company_name": "BuildBidz Sales Team 1",
            "password": "5968474644j"
        },
        "salesman2@buildbidz.co.in": {
            "id": "salesman2", 
            "company_name": "BuildBidz Sales Team 2",
            "password": "5968474644j"
        }
    }
    
    if login_data.email in salesman_accounts:
        salesman_data = salesman_accounts[login_data.email]
        if login_data.password == salesman_data["password"]:
            salesman_user = User(
                id=salesman_data["id"],
                email=login_data.email,
                company_name=salesman_data["company_name"],
                contact_phone=SUPPORT_PHONE,
                role=UserRole.SALESMAN,
                is_verified=True,
                subscription_status="active"
            )
            access_token = create_access_token(data={"sub": salesman_data["id"]})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": salesman_user
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = await db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user["id"]})
    user_obj = User(**user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_obj
    }

# Password reset endpoints
@api_router.post("/auth/forgot-password")
async def forgot_password(reset_data: PasswordReset):
    user = await db.users.find_one({"email": reset_data.email})
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset code has been sent"}
    
    reset_code = generate_reset_code()
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Store reset code in database
    await db.password_resets.update_one(
        {"email": reset_data.email},
        {
            "$set": {
                "reset_code": reset_code,
                "expires_at": expires_at,
                "used": False
            }
        },
        upsert=True
    )
    
    # In a real app, send email with reset code
    # For now, we'll just return success (code will be in database)
    return {"message": "If the email exists, a reset code has been sent"}

@api_router.post("/auth/reset-password")
async def reset_password(reset_data: PasswordResetConfirm):
    # Check reset code
    reset_record = await db.password_resets.find_one({
        "email": reset_data.email,
        "reset_code": reset_data.reset_code,
        "used": False
    })
    
    if not reset_record or reset_record["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
    
    # Update user password
    hashed_password = hash_password(reset_data.new_password)
    result = await db.users.update_one(
        {"email": reset_data.email},
        {"$set": {"password": hashed_password}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mark reset code as used
    await db.password_resets.update_one(
        {"email": reset_data.email, "reset_code": reset_data.reset_code},
        {"$set": {"used": True}}
    )
    
    return {"message": "Password reset successfully"}

# User profile and settings
@api_router.get("/profile", response_model=User)
async def get_profile(current_user: User = Depends(get_current_user)):
    if current_user.id == "admin":
        return current_user
    
    # Refresh user data from database
    user_data = await db.users.find_one({"id": current_user.id})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**user_data)

@api_router.put("/profile")
async def update_profile(profile_data: UserUpdate, current_user: User = Depends(get_current_user)):
    if current_user.id == "admin":
        raise HTTPException(status_code=403, detail="Admin profile cannot be updated")
    
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    
    if update_data:
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
    
    return {"message": "Profile updated successfully"}

@api_router.post("/auth/change-password")
async def change_password(password_data: PasswordChange, current_user: User = Depends(get_current_user)):
    if current_user.id == "admin":
        raise HTTPException(status_code=403, detail="Admin password cannot be changed")
    
    # Get current user from database
    user = await db.users.find_one({"id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(password_data.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    hashed_password = hash_password(password_data.new_password)
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"password": hashed_password}}
    )
    
    return {"message": "Password changed successfully"}

# Admin endpoints
@api_router.get("/admin/users")
async def get_all_users(current_user: User = Depends(require_admin)):
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]

@api_router.get("/admin/users/{user_id}/details")
async def get_user_details(user_id: str, current_user: User = Depends(require_admin)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's jobs and bids
    jobs = await db.jobs.find({"posted_by": user_id}).to_list(100)
    bids = await db.bids.find({"supplier_id": user_id}).to_list(100)
    
    return {
        "user": User(**user),
        "jobs_posted": len(jobs),
        "bids_submitted": len(bids),
        "jobs": [JobPost(**job) for job in jobs],
        "bids": [{k: v for k, v in bid.items() if k != '_id'} for bid in bids]
    }

@api_router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, current_user: User = Depends(require_admin)):
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Also delete user's jobs and bids
    await db.jobs.delete_many({"posted_by": user_id})
    await db.bids.delete_many({"supplier_id": user_id})
    
    return {"message": "User deleted successfully"}

@api_router.get("/admin/jobs")
async def get_all_jobs(current_user: User = Depends(require_admin)):
    jobs = await db.jobs.find().sort("created_at", -1).to_list(1000)
    
    # Enrich with user info and convert ObjectIds
    enriched_jobs = []
    for job in jobs:
        # Remove MongoDB ObjectId if present
        job_dict = {k: v for k, v in job.items() if k != '_id'}
        
        user = await db.users.find_one({"id": job_dict["posted_by"]})
        job_dict["posted_by_info"] = {
            "company_name": user["company_name"],
            "email": user["email"],
            "contact_phone": user["contact_phone"]
        } if user else None
        enriched_jobs.append(job_dict)
    
    return enriched_jobs

@api_router.delete("/admin/jobs/{job_id}")
async def delete_job(job_id: str, current_user: User = Depends(require_admin)):
    result = await db.jobs.delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Also delete related bids
    await db.bids.delete_many({"job_id": job_id})
    
    return {"message": "Job deleted successfully"}

@api_router.get("/admin/bids")
async def get_all_bids(current_user: User = Depends(require_admin)):
    bids = await db.bids.find().sort("created_at", -1).to_list(1000)
    
    # Enrich with user and job info and convert ObjectIds
    enriched_bids = []
    for bid in bids:
        # Remove MongoDB ObjectId if present
        bid_dict = {k: v for k, v in bid.items() if k != '_id'}
        
        supplier = await db.users.find_one({"id": bid_dict["supplier_id"]})
        job = await db.jobs.find_one({"id": bid_dict["job_id"]})
        
        bid_dict["supplier_info"] = {
            "company_name": supplier["company_name"],
            "email": supplier["email"],
            "contact_phone": supplier["contact_phone"]
        } if supplier else None
        bid_dict["job_info"] = {
            "title": job["title"],
            "category": job["category"],
            "location": job["location"]
        } if job else None
        
        enriched_bids.append(bid_dict)
    
    return enriched_bids

@api_router.delete("/admin/bids/{bid_id}")
async def delete_bid(bid_id: str, current_user: User = Depends(require_admin)):
    result = await db.bids.delete_one({"id": bid_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    return {"message": "Bid deleted successfully"}

# Payment endpoints - Updated for monthly billing
@api_router.post("/payments/create-subscription-order")
async def create_subscription_order(current_user: User = Depends(require_buyer)):
    try:
        order = razorpay_client.order.create({
            "amount": SUBSCRIPTION_AMOUNT,
            "currency": "INR",
            "payment_capture": 1
        })
        
        # Store order in database
        await db.payment_orders.insert_one({
            "order_id": order["id"],
            "user_id": current_user.id,
            "amount": SUBSCRIPTION_AMOUNT,
            "status": "created",
            "created_at": datetime.utcnow()
        })
        
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment order: {str(e)}")

@api_router.post("/payments/verify-subscription")
async def verify_subscription_payment(
    order_id: str = Form(...),
    payment_id: str = Form(...),
    signature: str = Form(...),
    current_user: User = Depends(require_buyer)
):
    try:
        # Verify payment signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        
        # Update user subscription - monthly billing
        expires_at = datetime.utcnow() + timedelta(days=30)  # 1 month subscription
        await db.users.update_one(
            {"id": current_user.id},
            {
                "$set": {
                    "subscription_status": "active",
                    "subscription_expires_at": expires_at,
                    "trial_expires_at": None  # Clear trial
                }
            }
        )
        
        # Update payment order status
        await db.payment_orders.update_one(
            {"order_id": order_id},
            {"$set": {"status": "completed", "payment_id": payment_id}}
        )
        
        return {"message": "Subscription activated successfully", "expires_at": expires_at}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Payment verification failed: {str(e)}")

# Job posting endpoints - Updated for trial support
@api_router.post("/jobs", response_model=JobPost)
async def create_job(job_data: JobPostCreate, current_user: User = Depends(require_active_subscription_or_trial)):
    job = JobPost(**job_data.dict(), posted_by=current_user.id)
    await db.jobs.insert_one(job.dict())
    return job

@api_router.get("/jobs", response_model=List[JobPost])
async def get_jobs(current_user: User = Depends(get_current_user)):
    jobs = await db.jobs.find({"status": "open"}).sort("created_at", -1).to_list(100)
    return [JobPost(**job) for job in jobs]

@api_router.get("/jobs/my", response_model=List[JobPost])
async def get_my_jobs(current_user: User = Depends(require_buyer)):
    jobs = await db.jobs.find({"posted_by": current_user.id}).sort("created_at", -1).to_list(100)
    return [JobPost(**job) for job in jobs]

# Bidding endpoints
@api_router.post("/jobs/{job_id}/bids")
async def submit_bid(job_id: str, bid_data: BidCreate, current_user: User = Depends(require_supplier)):
    # Check if job exists
    job = await db.jobs.find_one({"id": job_id, "status": "open"})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or closed")
    
    # Check if user already bid
    existing_bid = await db.bids.find_one({"job_id": job_id, "supplier_id": current_user.id})
    if existing_bid:
        raise HTTPException(status_code=400, detail="You have already submitted a bid for this job")
    
    bid = Bid(**bid_data.dict(), job_id=job_id, supplier_id=current_user.id)
    await db.bids.insert_one(bid.dict())
    return bid

# Salesman bidding endpoint for unregistered companies
@api_router.post("/jobs/{job_id}/salesman-bids")
async def submit_salesman_bid(job_id: str, bid_data: SalesmanBidCreate, current_user: User = Depends(require_admin_or_salesman)):
    # Check if job exists
    job = await db.jobs.find_one({"id": job_id, "status": "open"})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or closed")
    
    # Create enhanced bid with company details
    salesman_bid = Bid(
        job_id=job_id,
        supplier_id=current_user.id,  # Use salesman ID as supplier
        price_quote=bid_data.price_quote,
        delivery_estimate=bid_data.delivery_estimate,
        notes=bid_data.notes,
        status="submitted"
    )
    
    # Store company details separately for this bid
    company_details = {
        "company_name": bid_data.company_name,
        "company_contact_phone": bid_data.company_contact_phone,
        "company_email": bid_data.company_email,
        "company_gst_number": bid_data.company_gst_number,
        "company_address": bid_data.company_address,
        "submitted_by_salesman": current_user.id,
        "submitted_by_salesman_name": current_user.company_name
    }
    
    # Create bid document with company details embedded
    bid_document = {
        **salesman_bid.dict(),
        "company_details": company_details,
        "bid_type": "salesman_bid"
    }
    
    await db.bids.insert_one(bid_document)
    return salesman_bid

@api_router.get("/jobs/{job_id}/bids", response_model=List[Dict])
async def get_job_bids(job_id: str, current_user: User = Depends(get_current_user)):
    # Check if user owns the job or is admin
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["posted_by"] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view bids")
    
    bids = await db.bids.find({"job_id": job_id}).sort("created_at", -1).to_list(100)
    
    # Enrich with supplier info and convert ObjectIds
    enriched_bids = []
    for bid in bids:
        # Remove MongoDB ObjectId if present
        bid_dict = {k: v for k, v in bid.items() if k != '_id'}
        
        supplier = await db.users.find_one({"id": bid_dict["supplier_id"]})
        bid_with_supplier = {
            **bid_dict,
            "supplier_info": {
                "company_name": supplier["company_name"],
                "contact_phone": supplier["contact_phone"]
            } if supplier else None
        }
        enriched_bids.append(bid_with_supplier)
    
    return enriched_bids

@api_router.get("/bids/my", response_model=List[Dict])
async def get_my_bids(current_user: User = Depends(require_supplier)):
    bids = await db.bids.find({"supplier_id": current_user.id}).sort("created_at", -1).to_list(100)
    
    # Enrich with job info and convert ObjectIds
    enriched_bids = []
    for bid in bids:
        # Remove MongoDB ObjectId if present
        bid_dict = {k: v for k, v in bid.items() if k != '_id'}
        
        job = await db.jobs.find_one({"id": bid_dict["job_id"]})
        bid_with_job = {
            **bid_dict,
            "job_info": {
                "title": job["title"],
                "category": job["category"],
                "location": job["location"]
            } if job else None
        }
        enriched_bids.append(bid_with_job)
    
    return enriched_bids

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    message: str
    type: str  # bid_awarded, bid_rejected, job_posted, etc.
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    related_job_id: Optional[str] = None
    related_bid_id: Optional[str] = None

# Award bid endpoint - Enhanced
@api_router.post("/jobs/{job_id}/award/{bid_id}")
async def award_bid(job_id: str, bid_id: str, current_user: User = Depends(require_buyer)):
    # Check if user owns the job
    job = await db.jobs.find_one({"id": job_id, "posted_by": current_user.id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if bid exists
    bid = await db.bids.find_one({"id": bid_id, "job_id": job_id})
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    # Award the bid
    await db.bids.update_one({"id": bid_id}, {"$set": {"status": "awarded"}})
    await db.jobs.update_one({"id": job_id}, {"$set": {"status": "awarded"}})
    
    # Create notification for awarded supplier
    winning_notification = Notification(
        user_id=bid["supplier_id"],
        title="🎉 Congratulations! Your bid was awarded",
        message=f"Your bid for '{job['title']}' has been accepted. The buyer will contact you soon.",
        type="bid_awarded",
        related_job_id=job_id,
        related_bid_id=bid_id
    )
    await db.notifications.insert_one(winning_notification.dict())
    
    # Reject other bids and notify suppliers
    other_bids = await db.bids.find({"job_id": job_id, "id": {"$ne": bid_id}}).to_list(100)
    for other_bid in other_bids:
        await db.bids.update_one({"id": other_bid["id"]}, {"$set": {"status": "rejected"}})
        
        # Create notification for rejected suppliers
        rejection_notification = Notification(
            user_id=other_bid["supplier_id"],
            title="Bid Update",
            message=f"Your bid for '{job['title']}' was not selected this time. Keep bidding on other projects!",
            type="bid_rejected",
            related_job_id=job_id,
            related_bid_id=other_bid["id"]
        )
        await db.notifications.insert_one(rejection_notification.dict())
    
    return {"message": "Bid awarded successfully", "notifications_sent": len(other_bids) + 1}

# Notification endpoints
@api_router.get("/notifications")
async def get_notifications(current_user: User = Depends(get_current_user)):
    notifications = await db.notifications.find({"user_id": current_user.id}).sort("created_at", -1).to_list(50)
    return [Notification(**notification) for notification in notifications]

@api_router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: User = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user.id},
        {"$set": {"read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}

@api_router.get("/notifications/unread-count")
async def get_unread_notifications_count(current_user: User = Depends(get_current_user)):
    count = await db.notifications.count_documents({"user_id": current_user.id, "read": False})
    return {"unread_count": count}

# Chat endpoints
@api_router.get("/jobs/{job_id}/chat")
async def get_job_chat(job_id: str, current_user: User = Depends(get_current_user)):
    # Check if user is involved in this job (either buyer, awarded supplier, or admin)
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    is_authorized = False
    
    # Check if user is the job poster
    if job["posted_by"] == current_user.id:
        is_authorized = True
    
    # Check if user is the awarded supplier
    awarded_bid = await db.bids.find_one({"job_id": job_id, "status": "awarded"})
    if awarded_bid and awarded_bid["supplier_id"] == current_user.id:
        is_authorized = True
    
    # Admin can access all chats
    if current_user.role == UserRole.ADMIN:
        is_authorized = True
    
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")
    
    # Get chat messages
    messages = await db.chat_messages.find({"job_id": job_id}).sort("created_at", 1).to_list(1000)
    
    # Enrich with sender info
    enriched_messages = []
    for message in messages:
        sender = await db.users.find_one({"id": message["sender_id"]})
        message_with_sender = {
            **message,
            "sender_info": {
                "company_name": sender["company_name"],
                "role": sender["role"]
            } if sender else None
        }
        enriched_messages.append(message_with_sender)
    
    return enriched_messages

@api_router.post("/jobs/{job_id}/chat")
async def send_message(job_id: str, message_data: ChatMessageCreate, current_user: User = Depends(get_current_user)):
    # Check if user is involved in this job
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    is_authorized = False
    receiver_id = None
    
    # Determine receiver based on sender
    if job["posted_by"] == current_user.id:
        # Buyer is sending message - send to awarded supplier
        awarded_bid = await db.bids.find_one({"job_id": job_id, "status": "awarded"})
        if awarded_bid:
            receiver_id = awarded_bid["supplier_id"]
            is_authorized = True
    else:
        # Check if current user is awarded supplier
        awarded_bid = await db.bids.find_one({"job_id": job_id, "supplier_id": current_user.id, "status": "awarded"})
        if awarded_bid:
            receiver_id = job["posted_by"]
            is_authorized = True
    
    # Admin can send messages to anyone
    if current_user.role == UserRole.ADMIN:
        is_authorized = True
        # For admin, send to job poster by default
        if not receiver_id:
            receiver_id = job["posted_by"]
    
    if not is_authorized or not receiver_id:
        raise HTTPException(status_code=403, detail="Not authorized to send messages in this chat")
    
    # Create message
    message = ChatMessage(
        job_id=job_id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        message=message_data.message,
        file_url=message_data.file_url
    )
    
    await db.chat_messages.insert_one(message.dict())
    
    # Create notification for receiver
    notification = Notification(
        user_id=receiver_id,
        title="New Message",
        message=f"You have a new message regarding '{job['title']}'",
        type="chat_message",
        related_job_id=job_id
    )
    await db.notifications.insert_one(notification.dict())
    
    return {"message": "Message sent successfully", "chat_message": message}

@api_router.get("/admin/chats")
async def get_all_chats(current_user: User = Depends(require_admin)):
    # Get all jobs with their chat activity
    jobs = await db.jobs.find({"status": "awarded"}).to_list(1000)
    
    chat_activity = []
    for job in jobs:
        message_count = await db.chat_messages.count_documents({"job_id": job["id"]})
        if message_count > 0:
            last_message = await db.chat_messages.find_one(
                {"job_id": job["id"]}, 
                sort=[("created_at", -1)]
            )
            
            # Get participants
            buyer = await db.users.find_one({"id": job["posted_by"]})
            awarded_bid = await db.bids.find_one({"job_id": job["id"], "status": "awarded"})
            supplier = await db.users.find_one({"id": awarded_bid["supplier_id"]}) if awarded_bid else None
            
            chat_activity.append({
                "job_id": job["id"],
                "job_title": job["title"],
                "message_count": message_count,
                "last_message_at": last_message["created_at"] if last_message else None,
                "participants": {
                    "buyer": {"company_name": buyer["company_name"], "email": buyer["email"]} if buyer else None,
                    "supplier": {"company_name": supplier["company_name"], "email": supplier["email"]} if supplier else None
                }
            })
    
    return sorted(chat_activity, key=lambda x: x["last_message_at"] or x["job_id"], reverse=True)

# Get user's active chats
@api_router.get("/chats")
async def get_user_chats(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.ADMIN:
        return await get_all_chats(current_user)
    
    # Get jobs where user is involved and job is awarded
    user_chats = []
    
    if current_user.role == UserRole.BUYER:
        # Get jobs posted by this buyer that are awarded
        jobs = await db.jobs.find({"posted_by": current_user.id, "status": "awarded"}).to_list(100)
    else:
        # Get jobs where this supplier has winning bids
        awarded_bids = await db.bids.find({"supplier_id": current_user.id, "status": "awarded"}).to_list(100)
        job_ids = [bid["job_id"] for bid in awarded_bids]
        jobs = await db.jobs.find({"id": {"$in": job_ids}}).to_list(100)
    
    for job in jobs:
        message_count = await db.chat_messages.count_documents({"job_id": job["id"]})
        unread_count = await db.chat_messages.count_documents({
            "job_id": job["id"], 
            "receiver_id": current_user.id, 
            "read": False
        })
        
        last_message = await db.chat_messages.find_one(
            {"job_id": job["id"]}, 
            sort=[("created_at", -1)]
        )
        
        user_chats.append({
            "job_id": job["id"],
            "job_title": job["title"],
            "message_count": message_count,
            "unread_count": unread_count,
            "last_message_at": last_message["created_at"] if last_message else None,
            "last_message": last_message["message"] if last_message else None
        })
    
    return sorted(user_chats, key=lambda x: x["last_message_at"] or x["job_id"], reverse=True)

@api_router.post("/chats/{job_id}/mark-read")
async def mark_chat_read(job_id: str, current_user: User = Depends(get_current_user)):
    result = await db.chat_messages.update_many(
        {"job_id": job_id, "receiver_id": current_user.id, "read": False},
        {"$set": {"read": True}}
    )
    
    return {"message": f"Marked {result.modified_count} messages as read"}

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.ADMIN:
        total_users = await db.users.count_documents({})
        total_jobs = await db.jobs.count_documents({})
        total_bids = await db.bids.count_documents({})
        active_jobs = await db.jobs.count_documents({"status": "open"})
        
        return {
            "total_users": total_users,
            "total_jobs": total_jobs,
            "total_bids": total_bids,
            "active_jobs": active_jobs
        }
    elif current_user.role == UserRole.BUYER:
        total_jobs = await db.jobs.count_documents({"posted_by": current_user.id})
        active_jobs = await db.jobs.count_documents({"posted_by": current_user.id, "status": "open"})
        total_bids = await db.bids.count_documents({"job_id": {"$in": [job["id"] async for job in db.jobs.find({"posted_by": current_user.id})]}})
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_bids_received": total_bids,
            "subscription_status": current_user.subscription_status,
            "trial_expires_at": current_user.trial_expires_at
        }
    else:  # Supplier
        total_bids = await db.bids.count_documents({"supplier_id": current_user.id})
        won_bids = await db.bids.count_documents({"supplier_id": current_user.id, "status": "awarded"})
        
        return {
            "total_bids": total_bids,
            "won_bids": won_bids,
            "win_rate": f"{(won_bids/total_bids*100):.1f}%" if total_bids > 0 else "0%"
        }

# Support info endpoint
@api_router.get("/support-info")
async def get_support_info():
    return {
        "phone": SUPPORT_PHONE,
        "email": SUPPORT_EMAIL
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()