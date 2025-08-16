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
SUBSCRIPTION_AMOUNT = int(os.environ['SUBSCRIPTION_AMOUNT'])  # ₹5000 in paise

# Create the main app
app = FastAPI(title="BuildBidz API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Models
class UserRole(str):
    BUYER = "buyer"
    SUPPLIER = "supplier" 
    ADMIN = "admin"

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
    subscription_status: str = "inactive"  # inactive, active, expired
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

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

class PaymentOrder(BaseModel):
    amount: int = SUBSCRIPTION_AMOUNT
    currency: str = "INR"

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    sender_id: str
    receiver_id: str
    message: str
    file_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

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

async def require_active_subscription(current_user: User = Depends(require_buyer)):
    if current_user.subscription_status != "active" or (
        current_user.subscription_expires_at and current_user.subscription_expires_at < datetime.utcnow()
    ):
        raise HTTPException(status_code=402, detail="Active subscription required")
    return current_user

# Auth endpoints
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        company_name=user_data.company_name,
        contact_phone=user_data.contact_phone,
        role=user_data.role,
        gst_number=user_data.gst_number,
        address=user_data.address,
        is_verified=user_data.role == UserRole.SUPPLIER  # Auto-verify suppliers for MVP
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

# Payment endpoints
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
        
        # Update user subscription
        expires_at = datetime.utcnow() + timedelta(days=365)  # 1 year subscription
        await db.users.update_one(
            {"id": current_user.id},
            {
                "$set": {
                    "subscription_status": "active",
                    "subscription_expires_at": expires_at
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

# Job posting endpoints
@api_router.post("/jobs", response_model=JobPost)
async def create_job(job_data: JobPostCreate, current_user: User = Depends(require_active_subscription)):
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

@api_router.get("/jobs/{job_id}/bids", response_model=List[Dict])
async def get_job_bids(job_id: str, current_user: User = Depends(get_current_user)):
    # Check if user owns the job or is admin
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["posted_by"] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view bids")
    
    bids = await db.bids.find({"job_id": job_id}).sort("created_at", -1).to_list(100)
    
    # Enrich with supplier info
    enriched_bids = []
    for bid in bids:
        supplier = await db.users.find_one({"id": bid["supplier_id"]})
        bid_with_supplier = {
            **bid,
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
    
    # Enrich with job info
    enriched_bids = []
    for bid in bids:
        job = await db.jobs.find_one({"id": bid["job_id"]})
        bid_with_job = {
            **bid,
            "job_info": {
                "title": job["title"],
                "category": job["category"],
                "location": job["location"]
            } if job else None
        }
        enriched_bids.append(bid_with_job)
    
    return enriched_bids

# Award bid endpoint
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
    
    # Reject other bids
    await db.bids.update_many(
        {"job_id": job_id, "id": {"$ne": bid_id}},
        {"$set": {"status": "rejected"}}
    )
    
    return {"message": "Bid awarded successfully"}

# User profile endpoint
@api_router.get("/profile", response_model=User)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.BUYER:
        total_jobs = await db.jobs.count_documents({"posted_by": current_user.id})
        active_jobs = await db.jobs.count_documents({"posted_by": current_user.id, "status": "open"})
        total_bids = await db.bids.count_documents({"job_id": {"$in": [job["id"] async for job in db.jobs.find({"posted_by": current_user.id})]}})
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_bids_received": total_bids,
            "subscription_status": current_user.subscription_status
        }
    else:  # Supplier
        total_bids = await db.bids.count_documents({"supplier_id": current_user.id})
        won_bids = await db.bids.count_documents({"supplier_id": current_user.id, "status": "awarded"})
        
        return {
            "total_bids": total_bids,
            "won_bids": won_bids,
            "win_rate": f"{(won_bids/total_bids*100):.1f}%" if total_bids > 0 else "0%"
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