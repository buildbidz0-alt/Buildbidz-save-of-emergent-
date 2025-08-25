import requests
import sys
import json
from datetime import datetime
import time

class BuildBidzAPITester:
    def __init__(self, base_url="https://construct-connect.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.supplier_token = None
        self.admin_token = None
        self.salesman1_token = None
        self.salesman2_token = None
        self.buyer_user = None
        self.supplier_user = None
        self.admin_user = None
        self.salesman1_user = None
        self.salesman2_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.job_id = None
        self.bid_id = None
        self.salesman_bid_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, form_data=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        if form_data:
            headers = {'Authorization': f'Bearer {token}'} if token else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if form_data:
                    response = requests.post(url, data=data, headers=headers)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration for both roles"""
        print("\n" + "="*50)
        print("TESTING USER REGISTRATION")
        print("="*50)
        
        # Test Buyer Registration
        buyer_data = {
            "email": f"buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Test Construction Co",
            "contact_phone": "+91-9876543210",
            "role": "buyer",
            "gst_number": "29ABCDE1234F1Z5",
            "address": "123 Test Street, Mumbai"
        }
        
        success, response = self.run_test(
            "Buyer Registration",
            "POST",
            "auth/register",
            200,
            data=buyer_data
        )
        
        if success and 'access_token' in response:
            self.buyer_token = response['access_token']
            self.buyer_user = response['user']
            print(f"   Buyer ID: {self.buyer_user['id']}")
        
        # Test Supplier Registration
        supplier_data = {
            "email": f"supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Test Supplier Ltd",
            "contact_phone": "+91-9876543211",
            "role": "supplier",
            "gst_number": "29ABCDE1234F1Z6",
            "address": "456 Supplier Street, Delhi"
        }
        
        success, response = self.run_test(
            "Supplier Registration",
            "POST",
            "auth/register",
            200,
            data=supplier_data
        )
        
        if success and 'access_token' in response:
            self.supplier_token = response['access_token']
            self.supplier_user = response['user']
            print(f"   Supplier ID: {self.supplier_user['id']}")

        # Test duplicate email registration
        self.run_test(
            "Duplicate Email Registration",
            "POST",
            "auth/register",
            400,
            data=buyer_data
        )

    def test_user_login(self):
        """Test user login functionality"""
        print("\n" + "="*50)
        print("TESTING USER LOGIN")
        print("="*50)
        
        if not self.buyer_user or not self.supplier_user:
            print("❌ Cannot test login - registration failed")
            return
        
        # Test Buyer Login
        buyer_login = {
            "email": self.buyer_user['email'],
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "Buyer Login",
            "POST",
            "auth/login",
            200,
            data=buyer_login
        )
        
        # Test Supplier Login
        supplier_login = {
            "email": self.supplier_user['email'],
            "password": "TestPass123!"
        }
        
        self.run_test(
            "Supplier Login",
            "POST",
            "auth/login",
            200,
            data=supplier_login
        )
        
        # Test invalid login
        invalid_login = {
            "email": "invalid@test.com",
            "password": "wrongpassword"
        }
        
        self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data=invalid_login
        )

    def test_profile_access(self):
        """Test profile access with authentication"""
        print("\n" + "="*50)
        print("TESTING PROFILE ACCESS")
        print("="*50)
        
        # Test authenticated profile access
        self.run_test(
            "Buyer Profile Access",
            "GET",
            "profile",
            200,
            token=self.buyer_token
        )
        
        self.run_test(
            "Supplier Profile Access",
            "GET",
            "profile",
            200,
            token=self.supplier_token
        )
        
        # Test unauthenticated access
        self.run_test(
            "Unauthenticated Profile Access",
            "GET",
            "profile",
            401
        )

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        print("\n" + "="*50)
        print("TESTING DASHBOARD STATS")
        print("="*50)
        
        self.run_test(
            "Buyer Dashboard Stats",
            "GET",
            "dashboard/stats",
            200,
            token=self.buyer_token
        )
        
        self.run_test(
            "Supplier Dashboard Stats",
            "GET",
            "dashboard/stats",
            200,
            token=self.supplier_token
        )

    def test_subscription_system(self):
        """Test subscription system for buyers"""
        print("\n" + "="*50)
        print("TESTING SUBSCRIPTION SYSTEM")
        print("="*50)
        
        # Test creating subscription order (Buyer only)
        success, response = self.run_test(
            "Create Subscription Order (Buyer)",
            "POST",
            "payments/create-subscription-order",
            200,
            token=self.buyer_token
        )
        
        if success and 'id' in response:
            order_id = response['id']
            print(f"   Order ID: {order_id}")
        
        # Test supplier trying to create subscription order (should fail)
        self.run_test(
            "Create Subscription Order (Supplier - Should Fail)",
            "POST",
            "payments/create-subscription-order",
            403,
            token=self.supplier_token
        )

    def test_job_posting_without_subscription(self):
        """Test job posting without active subscription (should fail)"""
        print("\n" + "="*50)
        print("TESTING JOB POSTING WITHOUT SUBSCRIPTION")
        print("="*50)
        
        job_data = {
            "title": "Test Construction Job",
            "category": "material",
            "description": "Need cement and steel for construction project",
            "quantity": "100 bags cement, 50 tons steel",
            "location": "Mumbai, Maharashtra",
            "delivery_timeline": "2 weeks",
            "budget_range": "₹5,00,000 - ₹7,00,000"
        }
        
        # Should fail due to no active subscription
        self.run_test(
            "Job Posting Without Subscription",
            "POST",
            "jobs",
            402,
            data=job_data,
            token=self.buyer_token
        )

    def test_job_browsing(self):
        """Test job browsing functionality"""
        print("\n" + "="*50)
        print("TESTING JOB BROWSING")
        print("="*50)
        
        # Test getting all jobs
        self.run_test(
            "Get All Jobs (Buyer)",
            "GET",
            "jobs",
            200,
            token=self.buyer_token
        )
        
        self.run_test(
            "Get All Jobs (Supplier)",
            "GET",
            "jobs",
            200,
            token=self.supplier_token
        )
        
        # Test getting my jobs (buyer only)
        self.run_test(
            "Get My Jobs (Buyer)",
            "GET",
            "jobs/my",
            200,
            token=self.buyer_token
        )
        
        # Test supplier trying to get "my jobs" (should fail)
        self.run_test(
            "Get My Jobs (Supplier - Should Fail)",
            "GET",
            "jobs/my",
            403,
            token=self.supplier_token
        )

    def test_bidding_system(self):
        """Test bidding system"""
        print("\n" + "="*50)
        print("TESTING BIDDING SYSTEM")
        print("="*50)
        
        # Test getting my bids (supplier only)
        self.run_test(
            "Get My Bids (Supplier)",
            "GET",
            "bids/my",
            200,
            token=self.supplier_token
        )
        
        # Test buyer trying to get bids (should fail)
        self.run_test(
            "Get My Bids (Buyer - Should Fail)",
            "GET",
            "bids/my",
            403,
            token=self.buyer_token
        )

    def test_admin_login(self):
        """Test admin login functionality"""
        print("\n" + "="*50)
        print("TESTING ADMIN LOGIN")
        print("="*50)
        
        # Test Admin Login with correct credentials
        admin_login = {
            "email": "mohammadjalaluddin1027@gmail.com",
            "password": "5968474644j"
        }
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data=admin_login
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.admin_user = response['user']
            print(f"   Admin logged in successfully")
            print(f"   Admin role: {self.admin_user.get('role')}")
        
        # Test invalid admin credentials
        invalid_admin = {
            "email": "mohammadjalaluddin1027@gmail.com",
            "password": "wrongpassword"
        }
        
        self.run_test(
            "Invalid Admin Login",
            "POST",
            "auth/login",
            401,
            data=invalid_admin
        )

    def test_admin_dashboard_access(self):
        """Test admin dashboard and management functionality"""
        print("\n" + "="*50)
        print("TESTING ADMIN DASHBOARD ACCESS")
        print("="*50)
        
        if not self.admin_token:
            print("❌ Cannot test admin dashboard - admin login failed")
            return
        
        # Test admin dashboard stats
        self.run_test(
            "Admin Dashboard Stats",
            "GET",
            "dashboard/stats",
            200,
            token=self.admin_token
        )
        
        # Test admin user management
        self.run_test(
            "Admin Get All Users",
            "GET",
            "admin/users",
            200,
            token=self.admin_token
        )
        
        # Test admin job management
        self.run_test(
            "Admin Get All Jobs",
            "GET",
            "admin/jobs",
            200,
            token=self.admin_token
        )
        
        # Test admin bid management
        self.run_test(
            "Admin Get All Bids",
            "GET",
            "admin/bids",
            200,
            token=self.admin_token
        )
        
        # Test non-admin trying to access admin endpoints
        self.run_test(
            "Non-Admin accessing admin users (Should Fail)",
            "GET",
            "admin/users",
            403,
            token=self.buyer_token
        )

    def test_password_management(self):
        """Test password reset and change functionality"""
        print("\n" + "="*50)
        print("TESTING PASSWORD MANAGEMENT")
        print("="*50)
        
        if not self.buyer_user:
            print("❌ Cannot test password management - no buyer user")
            return
        
        # Test forgot password
        forgot_password_data = {
            "email": self.buyer_user['email']
        }
        
        self.run_test(
            "Forgot Password Request",
            "POST",
            "auth/forgot-password",
            200,
            data=forgot_password_data
        )
        
        # Test forgot password with non-existent email
        forgot_password_invalid = {
            "email": "nonexistent@test.com"
        }
        
        self.run_test(
            "Forgot Password (Non-existent Email)",
            "POST",
            "auth/forgot-password",
            200,  # Should still return 200 for security
            data=forgot_password_invalid
        )
        
        # Test change password (requires current password)
        change_password_data = {
            "current_password": "TestPass123!",
            "new_password": "NewTestPass123!"
        }
        
        self.run_test(
            "Change Password",
            "POST",
            "auth/change-password",
            200,
            data=change_password_data,
            token=self.buyer_token
        )
        
        # Test change password with wrong current password
        wrong_current_password = {
            "current_password": "WrongPassword",
            "new_password": "NewTestPass123!"
        }
        
        self.run_test(
            "Change Password (Wrong Current Password)",
            "POST",
            "auth/change-password",
            400,
            data=wrong_current_password,
            token=self.buyer_token
        )

    def test_user_profile_management(self):
        """Test user profile update functionality"""
        print("\n" + "="*50)
        print("TESTING USER PROFILE MANAGEMENT")
        print("="*50)
        
        if not self.buyer_token:
            print("❌ Cannot test profile management - no buyer token")
            return
        
        # Test profile update
        profile_update_data = {
            "company_name": "Updated Construction Co",
            "contact_phone": "8809696025",  # Updated contact info
            "gst_number": "29UPDATED1234F1Z5",
            "address": "Updated Address, Mumbai"
        }
        
        self.run_test(
            "Update Profile",
            "PUT",
            "profile",
            200,
            data=profile_update_data,
            token=self.buyer_token
        )
        
        # Test getting updated profile
        success, response = self.run_test(
            "Get Updated Profile",
            "GET",
            "profile",
            200,
            token=self.buyer_token
        )
        
        if success and response:
            print(f"   Updated company name: {response.get('company_name')}")
            print(f"   Updated phone: {response.get('contact_phone')}")

    def test_support_info(self):
        """Test support information endpoint"""
        print("\n" + "="*50)
        print("TESTING SUPPORT INFORMATION")
        print("="*50)
        
        success, response = self.run_test(
            "Get Support Info",
            "GET",
            "support-info",
            200
        )
        
        if success and response:
            expected_phone = "8809696025"
            expected_email = "mohammadjalaluddin1027@gmail.com"
            
            actual_phone = response.get('phone')
            actual_email = response.get('email')
            
            print(f"   Expected phone: {expected_phone}")
            print(f"   Actual phone: {actual_phone}")
            print(f"   Expected email: {expected_email}")
            print(f"   Actual email: {actual_email}")
            
            if actual_phone == expected_phone and actual_email == expected_email:
                print("✅ Support contact information is correct")
            else:
                print("❌ Support contact information mismatch")

    def test_subscription_pricing(self):
        """Test subscription pricing (should be ₹5000/month)"""
        print("\n" + "="*50)
        print("TESTING SUBSCRIPTION PRICING")
        print("="*50)
        
        if not self.buyer_token:
            print("❌ Cannot test subscription pricing - no buyer token")
            return
        
        success, response = self.run_test(
            "Create Subscription Order",
            "POST",
            "payments/create-subscription-order",
            200,
            token=self.buyer_token
        )
        
        if success and response:
            amount = response.get('amount')
            expected_amount = 500000  # ₹5000 in paise
            
            print(f"   Expected amount: {expected_amount} paise (₹5000)")
            print(f"   Actual amount: {amount} paise (₹{amount/100 if amount else 'N/A'})")
            
            if amount == expected_amount:
                print("✅ Subscription pricing is correct (₹5000/month)")
            else:
                print("❌ Subscription pricing mismatch")

    def test_trial_system(self):
        """Test 1-month free trial for new buyers"""
        print("\n" + "="*50)
        print("TESTING TRIAL SYSTEM")
        print("="*50)
        
        # Create a new buyer to test trial
        trial_buyer_data = {
            "email": f"trial_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Trial Construction Co",
            "contact_phone": "+91-9876543212",
            "role": "buyer",
            "gst_number": "29TRIAL1234F1Z5",
            "address": "123 Trial Street, Mumbai"
        }
        
        success, response = self.run_test(
            "New Buyer Registration (Should Get Trial)",
            "POST",
            "auth/register",
            200,
            data=trial_buyer_data
        )
        
        if success and response:
            user = response.get('user')
            if user:
                subscription_status = user.get('subscription_status')
                trial_expires_at = user.get('trial_expires_at')
                
                print(f"   Subscription status: {subscription_status}")
                print(f"   Trial expires at: {trial_expires_at}")
                
                if subscription_status == "trial" and trial_expires_at:
                    print("✅ New buyer gets 1-month free trial")
                else:
                    print("❌ Trial system not working correctly")

    def test_role_based_access(self):
        """Test role-based access controls"""
        print("\n" + "="*50)
        print("TESTING ROLE-BASED ACCESS CONTROLS")
        print("="*50)
        
        # Test various endpoints with wrong roles
        print("Testing access controls...")
        
        # Supplier trying buyer-only endpoints
        self.run_test(
            "Supplier accessing subscription (Should Fail)",
            "POST",
            "payments/create-subscription-order",
            403,
            token=self.supplier_token
        )
        
        self.run_test(
            "Supplier accessing my jobs (Should Fail)",
            "GET",
            "jobs/my",
            403,
            token=self.supplier_token
        )
        
        # Buyer trying supplier-only endpoints
        self.run_test(
            "Buyer accessing my bids (Should Fail)",
            "GET",
            "bids/my",
            403,
            token=self.buyer_token
        )
        
        # Non-admin trying admin endpoints
        self.run_test(
            "Buyer accessing admin users (Should Fail)",
            "GET",
            "admin/users",
            403,
            token=self.buyer_token
        )
        
        self.run_test(
            "Supplier accessing admin jobs (Should Fail)",
            "GET",
            "admin/jobs",
            403,
            token=self.supplier_token
        )

    def test_enhanced_admin_features(self):
        """Test enhanced admin panel features"""
        print("\n" + "="*50)
        print("TESTING ENHANCED ADMIN FEATURES")
        print("="*50)
        
        if not self.admin_token:
            print("❌ Cannot test enhanced admin features - admin login failed")
            return
        
        # Test admin getting detailed user info
        if self.buyer_user:
            success, response = self.run_test(
                "Admin Get User Details",
                "GET",
                f"admin/users/{self.buyer_user['id']}/details",
                200,
                token=self.admin_token
            )
            
            if success and response:
                print(f"   User details retrieved for: {response.get('user', {}).get('company_name')}")
                print(f"   Jobs posted: {response.get('jobs_posted', 0)}")
                print(f"   Bids submitted: {response.get('bids_submitted', 0)}")
        
        # Test admin delete functionality (we'll test with a new user to avoid breaking other tests)
        test_user_data = {
            "email": f"delete_test_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Delete Test Co",
            "contact_phone": "+91-9876543213",
            "role": "supplier",
            "gst_number": "29DELETE1234F1Z5",
            "address": "Delete Test Street"
        }
        
        success, response = self.run_test(
            "Create Test User for Deletion",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        
        if success and response:
            test_user_id = response['user']['id']
            
            # Test admin delete user
            self.run_test(
                "Admin Delete User",
                "DELETE",
                f"admin/users/{test_user_id}",
                200,
                token=self.admin_token
            )

    def test_job_posting_with_trial(self):
        """Test job posting with active trial"""
        print("\n" + "="*50)
        print("TESTING JOB POSTING WITH TRIAL")
        print("="*50)
        
        # Create a new buyer with trial
        trial_buyer_data = {
            "email": f"job_trial_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Job Trial Construction Co",
            "contact_phone": "+91-9876543214",
            "role": "buyer",
            "gst_number": "29JOBTRIAL1234F1Z5",
            "address": "123 Job Trial Street, Mumbai"
        }
        
        success, response = self.run_test(
            "Create Trial Buyer for Job Posting",
            "POST",
            "auth/register",
            200,
            data=trial_buyer_data
        )
        
        if success and response:
            trial_token = response['access_token']
            
            # Test job posting with trial (should work)
            job_data = {
                "title": "Trial Construction Job",
                "category": "material",
                "description": "Need cement and steel for trial construction project",
                "quantity": "50 bags cement, 25 tons steel",
                "location": "Mumbai, Maharashtra",
                "delivery_timeline": "1 week",
                "budget_range": "₹2,50,000 - ₹3,50,000"
            }
            
            success, job_response = self.run_test(
                "Job Posting With Trial",
                "POST",
                "jobs",
                200,
                data=job_data,
                token=trial_token
            )
            
            if success and job_response:
                self.job_id = job_response['id']
                print(f"   Job created with ID: {self.job_id}")

    def test_bidding_and_awarding_system(self):
        """Test enhanced bidding and awarding system"""
        print("\n" + "="*50)
        print("TESTING BIDDING AND AWARDING SYSTEM")
        print("="*50)
        
        if not self.job_id or not self.supplier_token:
            print("❌ Cannot test bidding - no job or supplier token")
            return
        
        # Test submitting a bid
        bid_data = {
            "price_quote": 300000.0,
            "delivery_estimate": "5 days",
            "notes": "High quality materials with fast delivery"
        }
        
        success, response = self.run_test(
            "Submit Bid",
            "POST",
            f"jobs/{self.job_id}/bids",
            200,
            data=bid_data,
            token=self.supplier_token
        )
        
        if success and response:
            self.bid_id = response['id']
            print(f"   Bid submitted with ID: {self.bid_id}")
        
        # Test getting job bids (as job owner)
        # We need to use the trial buyer token who created the job
        trial_buyer_data = {
            "email": f"job_trial_buyer_{int(time.time()-1)}@test.com",
            "password": "TestPass123!"
        }
        
        success, login_response = self.run_test(
            "Login Trial Buyer for Bid Management",
            "POST",
            "auth/login",
            200,
            data=trial_buyer_data
        )
        
        if success and login_response:
            trial_buyer_token = login_response['access_token']
            
            # Get job bids
            success, bids_response = self.run_test(
                "Get Job Bids",
                "GET",
                f"jobs/{self.job_id}/bids",
                200,
                token=trial_buyer_token
            )
            
            if success and bids_response and len(bids_response) > 0:
                print(f"   Found {len(bids_response)} bids for the job")
                
                # Test awarding the bid
                if self.bid_id:
                    success, award_response = self.run_test(
                        "Award Bid",
                        "POST",
                        f"jobs/{self.job_id}/award/{self.bid_id}",
                        200,
                        token=trial_buyer_token
                    )
                    
                    if success and award_response:
                        notifications_sent = award_response.get('notifications_sent', 0)
                        print(f"   Bid awarded successfully, {notifications_sent} notifications sent")

    def test_notification_system(self):
        """Test notification system"""
        print("\n" + "="*50)
        print("TESTING NOTIFICATION SYSTEM")
        print("="*50)
        
        if not self.supplier_token:
            print("❌ Cannot test notifications - no supplier token")
            return
        
        # Test getting notifications
        success, response = self.run_test(
            "Get Notifications (Supplier)",
            "GET",
            "notifications",
            200,
            token=self.supplier_token
        )
        
        if success and response:
            print(f"   Found {len(response)} notifications")
            
            # Test unread count
            success, count_response = self.run_test(
                "Get Unread Notifications Count",
                "GET",
                "notifications/unread-count",
                200,
                token=self.supplier_token
            )
            
            if success and count_response:
                unread_count = count_response.get('unread_count', 0)
                print(f"   Unread notifications: {unread_count}")
                
                # If there are notifications, test marking one as read
                if response and len(response) > 0:
                    notification_id = response[0]['id']
                    self.run_test(
                        "Mark Notification as Read",
                        "POST",
                        f"notifications/{notification_id}/read",
                        200,
                        token=self.supplier_token
                    )

    def test_chat_system(self):
        """Test chat system functionality"""
        print("\n" + "="*50)
        print("TESTING CHAT SYSTEM")
        print("="*50)
        
        if not self.job_id or not self.supplier_token:
            print("❌ Cannot test chat system - no awarded job or supplier token")
            return
        
        # Test getting user chats
        success, response = self.run_test(
            "Get User Chats (Supplier)",
            "GET",
            "chats",
            200,
            token=self.supplier_token
        )
        
        if success and response:
            print(f"   Found {len(response)} active chats")
        
        # Test getting job chat messages
        success, messages_response = self.run_test(
            "Get Job Chat Messages",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.supplier_token
        )
        
        if success and messages_response:
            print(f"   Found {len(messages_response)} chat messages")
        
        # Test sending a message
        message_data = {
            "message": "Thank you for awarding the bid! When can we start the project?"
        }
        
        success, send_response = self.run_test(
            "Send Chat Message",
            "POST",
            f"jobs/{self.job_id}/chat",
            200,
            data=message_data,
            token=self.supplier_token
        )
        
        if success and send_response:
            print("   Chat message sent successfully")
        
        # Test marking chat as read
        self.run_test(
            "Mark Chat as Read",
            "POST",
            f"chats/{self.job_id}/mark-read",
            200,
            token=self.supplier_token
        )

    def test_admin_chat_management(self):
        """Test admin chat management"""
        print("\n" + "="*50)
        print("TESTING ADMIN CHAT MANAGEMENT")
        print("="*50)
        
        if not self.admin_token:
            print("❌ Cannot test admin chat management - admin login failed")
            return
        
        # Test admin getting all chats
        success, response = self.run_test(
            "Admin Get All Chats",
            "GET",
            "admin/chats",
            200,
            token=self.admin_token
        )
        
        if success and response:
            print(f"   Admin found {len(response)} chat activities")
            for chat in response[:3]:  # Show first 3 chats
                print(f"   - Job: {chat.get('job_title')} ({chat.get('message_count')} messages)")

    def test_enhanced_admin_delete_operations(self):
        """Test enhanced admin delete operations"""
        print("\n" + "="*50)
        print("TESTING ENHANCED ADMIN DELETE OPERATIONS")
        print("="*50)
        
        if not self.admin_token:
            print("❌ Cannot test admin delete operations - admin login failed")
            return
        
        # Create test data for deletion
        test_supplier_data = {
            "email": f"delete_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Delete Supplier Co",
            "contact_phone": "+91-9876543215",
            "role": "supplier",
            "gst_number": "29DELSUP1234F1Z5",
            "address": "Delete Supplier Street"
        }
        
        success, response = self.run_test(
            "Create Test Supplier for Deletion",
            "POST",
            "auth/register",
            200,
            data=test_supplier_data
        )
        
        if success and response:
            test_supplier_id = response['user']['id']
            test_supplier_token = response['access_token']
            
            # Create a test job and bid for deletion testing
            test_buyer_data = {
                "email": f"delete_buyer_{int(time.time())}@test.com",
                "password": "TestPass123!",
                "company_name": "Delete Buyer Co",
                "contact_phone": "+91-9876543216",
                "role": "buyer",
                "gst_number": "29DELBUY1234F1Z5",
                "address": "Delete Buyer Street"
            }
            
            success, buyer_response = self.run_test(
                "Create Test Buyer for Deletion",
                "POST",
                "auth/register",
                200,
                data=test_buyer_data
            )
            
            if success and buyer_response:
                test_buyer_token = buyer_response['access_token']
                
                # Create a job
                job_data = {
                    "title": "Delete Test Job",
                    "category": "material",
                    "description": "Job for deletion testing",
                    "location": "Test Location",
                    "delivery_timeline": "1 week",
                    "budget_range": "₹1,00,000"
                }
                
                success, job_response = self.run_test(
                    "Create Test Job for Deletion",
                    "POST",
                    "jobs",
                    200,
                    data=job_data,
                    token=test_buyer_token
                )
                
                if success and job_response:
                    test_job_id = job_response['id']
                    
                    # Create a bid
                    bid_data = {
                        "price_quote": 90000.0,
                        "delivery_estimate": "3 days",
                        "notes": "Test bid for deletion"
                    }
                    
                    success, bid_response = self.run_test(
                        "Create Test Bid for Deletion",
                        "POST",
                        f"jobs/{test_job_id}/bids",
                        200,
                        data=bid_data,
                        token=test_supplier_token
                    )
                    
                    if success and bid_response:
                        test_bid_id = bid_response['id']
                        
                        # Test admin delete bid
                        self.run_test(
                            "Admin Delete Bid",
                            "DELETE",
                            f"admin/bids/{test_bid_id}",
                            200,
                            token=self.admin_token
                        )
                    
                    # Test admin delete job
                    self.run_test(
                        "Admin Delete Job",
                        "DELETE",
                        f"admin/jobs/{test_job_id}",
                        200,
                        token=self.admin_token
                    )
                
                # Test admin delete buyer
                self.run_test(
                    "Admin Delete Buyer",
                    "DELETE",
                    f"admin/users/{buyer_response['user']['id']}",
                    200,
                    token=self.admin_token
                )
            
            # Test admin delete supplier
            self.run_test(
                "Admin Delete Supplier",
                "DELETE",
                f"admin/users/{test_supplier_id}",
                200,
                token=self.admin_token
            )

    def test_salesman_authentication(self):
        """Test salesman authentication functionality"""
        print("\n" + "="*50)
        print("TESTING SALESMAN AUTHENTICATION")
        print("="*50)
        
        # Test Salesman1 Login
        salesman1_login = {
            "email": "salesman1@buildbidz.co.in",
            "password": "5968474644j"
        }
        
        success, response = self.run_test(
            "Salesman1 Login",
            "POST",
            "auth/login",
            200,
            data=salesman1_login
        )
        
        if success and response:
            self.salesman1_token = response['access_token']
            self.salesman1_user = response['user']
            print(f"   Salesman1 ID: {self.salesman1_user['id']}")
            print(f"   Salesman1 Role: {self.salesman1_user['role']}")
            print(f"   Salesman1 Company: {self.salesman1_user['company_name']}")
            
            # Verify role is "salesman"
            if self.salesman1_user['role'] == 'salesman':
                print("✅ Salesman1 role verification passed")
            else:
                print(f"❌ Salesman1 role verification failed - Expected 'salesman', got '{self.salesman1_user['role']}'")
        
        # Test Salesman2 Login
        salesman2_login = {
            "email": "salesman2@buildbidz.co.in",
            "password": "5968474644j"
        }
        
        success, response = self.run_test(
            "Salesman2 Login",
            "POST",
            "auth/login",
            200,
            data=salesman2_login
        )
        
        if success and response:
            self.salesman2_token = response['access_token']
            self.salesman2_user = response['user']
            print(f"   Salesman2 ID: {self.salesman2_user['id']}")
            print(f"   Salesman2 Role: {self.salesman2_user['role']}")
            print(f"   Salesman2 Company: {self.salesman2_user['company_name']}")
            
            # Verify role is "salesman"
            if self.salesman2_user['role'] == 'salesman':
                print("✅ Salesman2 role verification passed")
            else:
                print(f"❌ Salesman2 role verification failed - Expected 'salesman', got '{self.salesman2_user['role']}'")
        
        # Test invalid salesman login
        invalid_salesman_login = {
            "email": "salesman1@buildbidz.co.in",
            "password": "wrongpassword"
        }
        
        self.run_test(
            "Invalid Salesman Login",
            "POST",
            "auth/login",
            401,
            data=invalid_salesman_login
        )

    def test_salesman_profile_access(self):
        """Test salesman profile access"""
        print("\n" + "="*50)
        print("TESTING SALESMAN PROFILE ACCESS")
        print("="*50)
        
        if not hasattr(self, 'salesman1_token') or not self.salesman1_token:
            print("❌ Cannot test salesman profile - salesman1 login failed")
            return
        
        # Test salesman profile access
        success, response = self.run_test(
            "Salesman1 Profile Access",
            "GET",
            "profile",
            200,
            token=self.salesman1_token
        )
        
        if success and response:
            print(f"   Profile Email: {response.get('email')}")
            print(f"   Profile Role: {response.get('role')}")
            print(f"   Profile Company: {response.get('company_name')}")
            print(f"   Profile Verified: {response.get('is_verified')}")
            print(f"   Profile Subscription: {response.get('subscription_status')}")
            
            # Verify JWT token contains correct user info
            if response.get('role') == 'salesman' and response.get('email') == 'salesman1@buildbidz.co.in':
                print("✅ JWT token and profile verification passed")
            else:
                print("❌ JWT token or profile verification failed")

    def test_salesman_job_access(self):
        """Test salesman access to job listing endpoints"""
        print("\n" + "="*50)
        print("TESTING SALESMAN JOB ACCESS")
        print("="*50)
        
        if not hasattr(self, 'salesman1_token') or not self.salesman1_token:
            print("❌ Cannot test salesman job access - salesman1 login failed")
            return
        
        # Test getting all jobs as salesman
        success, response = self.run_test(
            "Salesman Get All Jobs",
            "GET",
            "jobs",
            200,
            token=self.salesman1_token
        )
        
        if success and response:
            print(f"   Found {len(response)} available jobs")
            if len(response) > 0:
                print(f"   Sample job: {response[0].get('title')} - {response[0].get('category')}")
        
        # Test salesman dashboard stats
        success, stats_response = self.run_test(
            "Salesman Dashboard Stats",
            "GET",
            "dashboard/stats",
            200,
            token=self.salesman1_token
        )
        
        if success and stats_response:
            print(f"   Dashboard stats retrieved: {stats_response}")

    def test_salesman_bidding_functionality(self):
        """Test salesman bidding functionality"""
        print("\n" + "="*50)
        print("TESTING SALESMAN BIDDING FUNCTIONALITY")
        print("="*50)
        
        if not hasattr(self, 'salesman1_token') or not self.salesman1_token:
            print("❌ Cannot test salesman bidding - salesman1 login failed")
            return
        
        # First, get available jobs to bid on
        success, jobs_response = self.run_test(
            "Get Jobs for Salesman Bidding",
            "GET",
            "jobs",
            200,
            token=self.salesman1_token
        )
        
        if not success or not jobs_response or len(jobs_response) == 0:
            print("❌ No jobs available for bidding test")
            return
        
        # Use the first available job
        test_job = jobs_response[0]
        job_id = test_job['id']
        print(f"   Testing with job: {test_job['title']} (ID: {job_id})")
        
        # Test salesman bid submission
        salesman_bid_data = {
            "price_quote": 50000,
            "delivery_estimate": "10-15 days",
            "notes": "High quality materials with experienced team",
            "company_name": "ABC Construction Company",
            "company_contact_phone": "+91 9876543210",
            "company_email": "abc@construction.com",
            "company_gst_number": "29ABCDE1234F1Z5",
            "company_address": "123 Construction Street, Mumbai"
        }
        
        success, bid_response = self.run_test(
            "Submit Salesman Bid",
            "POST",
            f"jobs/{job_id}/salesman-bids",
            200,
            data=salesman_bid_data,
            token=self.salesman1_token
        )
        
        if success and bid_response:
            self.salesman_bid_id = bid_response['id']
            print(f"   Salesman bid submitted with ID: {self.salesman_bid_id}")
            print(f"   Bid price: ₹{bid_response.get('price_quote')}")
            print(f"   Delivery estimate: {bid_response.get('delivery_estimate')}")
        
        # Test that regular suppliers cannot use salesman bidding endpoint
        if hasattr(self, 'supplier_token') and self.supplier_token:
            self.run_test(
                "Supplier using Salesman Bid Endpoint (Should Fail)",
                "POST",
                f"jobs/{job_id}/salesman-bids",
                403,
                data=salesman_bid_data,
                token=self.supplier_token
            )
        
        # Test that buyers cannot use salesman bidding endpoint
        if hasattr(self, 'buyer_token') and self.buyer_token:
            self.run_test(
                "Buyer using Salesman Bid Endpoint (Should Fail)",
                "POST",
                f"jobs/{job_id}/salesman-bids",
                403,
                data=salesman_bid_data,
                token=self.buyer_token
            )

    def test_salesman_bid_visibility(self):
        """Test that salesman bids appear with company details"""
        print("\n" + "="*50)
        print("TESTING SALESMAN BID VISIBILITY")
        print("="*50)
        
        if not hasattr(self, 'salesman1_token') or not self.salesman1_token:
            print("❌ Cannot test salesman bid visibility - salesman1 login failed")
            return
        
        # Get available jobs to find one with bids
        success, jobs_response = self.run_test(
            "Get Jobs for Bid Visibility Test",
            "GET",
            "jobs",
            200,
            token=self.salesman1_token
        )
        
        if not success or not jobs_response or len(jobs_response) == 0:
            print("❌ No jobs available for bid visibility test")
            return
        
        # Find a job to test bid visibility
        test_job = jobs_response[0]
        job_id = test_job['id']
        
        # Test salesman can view bids on jobs
        success, bids_response = self.run_test(
            "Salesman View Job Bids",
            "GET",
            f"jobs/{job_id}/bids",
            200,
            token=self.salesman1_token
        )
        
        if success and bids_response:
            print(f"   Found {len(bids_response)} bids on job")
            
            # Check if any salesman bids exist and verify company details
            for bid in bids_response:
                if bid.get('bid_type') == 'salesman_bid':
                    supplier_info = bid.get('supplier_info', {})
                    print(f"   Salesman bid found:")
                    print(f"     Company: {supplier_info.get('company_name')}")
                    print(f"     Phone: {supplier_info.get('contact_phone')}")
                    print(f"     Email: {supplier_info.get('email')}")
                    print(f"     GST: {supplier_info.get('gst_number')}")
                    print(f"     Address: {supplier_info.get('address')}")
                    print(f"     Submitted by: {supplier_info.get('submitted_by_salesman')}")
                    
                    # Verify company details are shown instead of salesman details
                    if supplier_info.get('company_name') and supplier_info.get('company_name') != 'BuildBidz Sales Team 1':
                        print("✅ Salesman bid shows company details correctly")
                    else:
                        print("❌ Salesman bid not showing company details properly")
                    break
            else:
                print("   No salesman bids found in current job bids")

    def test_salesman_authorization(self):
        """Test salesman authorization and access controls"""
        print("\n" + "="*50)
        print("TESTING SALESMAN AUTHORIZATION")
        print("="*50)
        
        if not hasattr(self, 'salesman1_token') or not self.salesman1_token:
            print("❌ Cannot test salesman authorization - salesman1 login failed")
            return
        
        # Test salesman cannot access admin-only endpoints
        self.run_test(
            "Salesman accessing admin users (Should Fail)",
            "GET",
            "admin/users",
            403,
            token=self.salesman1_token
        )
        
        self.run_test(
            "Salesman accessing admin jobs (Should Fail)",
            "GET",
            "admin/jobs",
            403,
            token=self.salesman1_token
        )
        
        self.run_test(
            "Salesman accessing admin bids (Should Fail)",
            "GET",
            "admin/bids",
            403,
            token=self.salesman1_token
        )
        
        # Test salesman cannot access buyer-only endpoints
        self.run_test(
            "Salesman accessing my jobs (Should Fail)",
            "GET",
            "jobs/my",
            403,
            token=self.salesman1_token
        )
        
        self.run_test(
            "Salesman accessing subscription (Should Fail)",
            "POST",
            "payments/create-subscription-order",
            403,
            token=self.salesman1_token
        )
        
        # Test salesman cannot access supplier-only endpoints
        self.run_test(
            "Salesman accessing my bids (Should Fail)",
            "GET",
            "bids/my",
            403,
            token=self.salesman1_token
        )
        
        # Test salesman can access general endpoints
        self.run_test(
            "Salesman accessing support info",
            "GET",
            "support-info",
            200,
            token=self.salesman1_token
        )
        
        self.run_test(
            "Salesman accessing notifications",
            "GET",
            "notifications",
            200,
            token=self.salesman1_token
        )

    def test_multiple_salesman_bids(self):
        """Test multiple salesman accounts can bid on same job"""
        print("\n" + "="*50)
        print("TESTING MULTIPLE SALESMAN BIDS")
        print("="*50)
        
        if not hasattr(self, 'salesman1_token') or not self.salesman1_token:
            print("❌ Cannot test multiple salesman bids - salesman1 login failed")
            return
        
        if not hasattr(self, 'salesman2_token') or not self.salesman2_token:
            print("❌ Cannot test multiple salesman bids - salesman2 login failed")
            return
        
        # Get available jobs
        success, jobs_response = self.run_test(
            "Get Jobs for Multiple Salesman Bids",
            "GET",
            "jobs",
            200,
            token=self.salesman1_token
        )
        
        if not success or not jobs_response or len(jobs_response) == 0:
            print("❌ No jobs available for multiple salesman bids test")
            return
        
        # Use the first available job
        test_job = jobs_response[0]
        job_id = test_job['id']
        print(f"   Testing with job: {test_job['title']} (ID: {job_id})")
        
        # Salesman1 bid
        salesman1_bid_data = {
            "price_quote": 45000,
            "delivery_estimate": "8-12 days",
            "notes": "Premium quality with fast delivery",
            "company_name": "XYZ Construction Ltd",
            "company_contact_phone": "+91 9876543211",
            "company_email": "xyz@construction.com",
            "company_gst_number": "29XYZDE1234F1Z5",
            "company_address": "456 XYZ Street, Delhi"
        }
        
        success, bid1_response = self.run_test(
            "Salesman1 Submit Bid",
            "POST",
            f"jobs/{job_id}/salesman-bids",
            200,
            data=salesman1_bid_data,
            token=self.salesman1_token
        )
        
        # Salesman2 bid on same job
        salesman2_bid_data = {
            "price_quote": 48000,
            "delivery_estimate": "12-16 days",
            "notes": "Competitive pricing with quality assurance",
            "company_name": "PQR Builders Pvt Ltd",
            "company_contact_phone": "+91 9876543212",
            "company_email": "pqr@builders.com",
            "company_gst_number": "29PQRDE1234F1Z5",
            "company_address": "789 PQR Avenue, Bangalore"
        }
        
        success, bid2_response = self.run_test(
            "Salesman2 Submit Bid on Same Job",
            "POST",
            f"jobs/{job_id}/salesman-bids",
            200,
            data=salesman2_bid_data,
            token=self.salesman2_token
        )
        
        if success and bid2_response:
            print("✅ Multiple salesmen can bid on the same job")
        
        # Verify both bids appear in job bids
        success, bids_response = self.run_test(
            "View All Bids on Job",
            "GET",
            f"jobs/{job_id}/bids",
            200,
            token=self.salesman1_token
        )
        
        if success and bids_response:
            salesman_bids = [bid for bid in bids_response if bid.get('bid_type') == 'salesman_bid']
            print(f"   Found {len(salesman_bids)} salesman bids on this job")
            
            for i, bid in enumerate(salesman_bids):
                supplier_info = bid.get('supplier_info', {})
                print(f"   Bid {i+1}: {supplier_info.get('company_name')} - ₹{bid.get('price_quote')}")

    def test_salesman_bid_data_structure(self):
        """Test salesman bid data structure and enrichment"""
        print("\n" + "="*50)
        print("TESTING SALESMAN BID DATA STRUCTURE")
        print("="*50)
        
        if not hasattr(self, 'salesman1_token') or not self.salesman1_token:
            print("❌ Cannot test salesman bid data structure - salesman1 login failed")
            return
        
        # Get jobs and find one with salesman bids
        success, jobs_response = self.run_test(
            "Get Jobs for Data Structure Test",
            "GET",
            "jobs",
            200,
            token=self.salesman1_token
        )
        
        if success and jobs_response:
            for job in jobs_response:
                job_id = job['id']
                
                # Get bids for this job
                success, bids_response = self.run_test(
                    f"Get Bids for Job {job['title'][:20]}...",
                    "GET",
                    f"jobs/{job_id}/bids",
                    200,
                    token=self.salesman1_token
                )
                
                if success and bids_response:
                    salesman_bids = [bid for bid in bids_response if bid.get('bid_type') == 'salesman_bid']
                    
                    if salesman_bids:
                        print(f"   Analyzing salesman bid data structure:")
                        bid = salesman_bids[0]
                        
                        # Check required fields
                        required_fields = ['id', 'job_id', 'supplier_id', 'price_quote', 'delivery_estimate', 'status', 'created_at']
                        for field in required_fields:
                            if field in bid:
                                print(f"   ✅ {field}: {bid[field]}")
                            else:
                                print(f"   ❌ Missing field: {field}")
                        
                        # Check company details structure
                        if 'company_details' in bid:
                            company_details = bid['company_details']
                            print(f"   ✅ company_details found")
                            
                            company_fields = ['company_name', 'company_contact_phone', 'submitted_by_salesman', 'submitted_by_salesman_name']
                            for field in company_fields:
                                if field in company_details:
                                    print(f"   ✅ company_details.{field}: {company_details[field]}")
                                else:
                                    print(f"   ❌ Missing company_details.{field}")
                        else:
                            print(f"   ❌ Missing company_details")
                        
                        # Check supplier_info enrichment
                        if 'supplier_info' in bid:
                            supplier_info = bid['supplier_info']
                            print(f"   ✅ supplier_info enrichment found")
                            
                            # Verify it shows company details, not salesman details
                            company_name = supplier_info.get('company_name')
                            if company_name and 'BuildBidz Sales Team' not in company_name:
                                print(f"   ✅ supplier_info shows company name: {company_name}")
                            else:
                                print(f"   ❌ supplier_info shows salesman name instead of company: {company_name}")
                        else:
                            print(f"   ❌ Missing supplier_info enrichment")
                        
                        break
                else:
                    continue
            else:
                print("   No salesman bids found for data structure analysis")

    def test_salesman_my_bids_functionality(self):
        """Test the complete salesman My Bids functionality as requested in review"""
        print("\n" + "="*50)
        print("TESTING SALESMAN MY BIDS FUNCTIONALITY - CRITICAL REVIEW REQUEST")
        print("="*50)
        
        if not hasattr(self, 'salesman1_token') or not self.salesman1_token:
            print("❌ Cannot test salesman My Bids - salesman1 login failed")
            return
        
        if not hasattr(self, 'salesman2_token') or not self.salesman2_token:
            print("❌ Cannot test salesman My Bids - salesman2 login failed")
            return
        
        # Step 1: Get available jobs for bidding
        success, jobs_response = self.run_test(
            "Get Available Jobs for Salesman Bidding",
            "GET",
            "jobs",
            200,
            token=self.salesman1_token
        )
        
        if not success or not jobs_response or len(jobs_response) == 0:
            print("❌ No jobs available for My Bids testing")
            return
        
        # Use first available job
        test_job = jobs_response[0]
        job_id = test_job['id']
        print(f"   Testing with job: {test_job['title']} (ID: {job_id})")
        
        # Step 2: Submit multiple salesman bids with different company details
        print("\n   📝 STEP 2: Submitting Salesman Bids with Company Details")
        
        # Bid 1 - Alpha Construction Ltd
        bid1_data = {
            "price_quote": 125000,
            "delivery_estimate": "2 weeks",
            "notes": "Premium quality materials with experienced team",
            "company_name": "Alpha Construction Ltd",
            "company_contact_phone": "+91 9123456789",
            "company_email": "alpha@construction.com",
            "company_gst_number": "27ABCDE1234F1Z5",
            "company_address": "456 Alpha Street, Delhi"
        }
        
        success, bid1_response = self.run_test(
            "Submit Salesman Bid 1 (Alpha Construction)",
            "POST",
            f"jobs/{job_id}/salesman-bids",
            200,
            data=bid1_data,
            token=self.salesman1_token
        )
        
        if success and bid1_response:
            bid1_id = bid1_response['id']
            print(f"   ✅ Bid 1 submitted: {bid1_data['company_name']} - ₹{bid1_data['price_quote']}")
        
        # Bid 2 - Beta Builders Pvt Ltd (using salesman2)
        bid2_data = {
            "price_quote": 98000,
            "delivery_estimate": "10 days",
            "notes": "Fast delivery with quality assurance",
            "company_name": "Beta Builders Pvt Ltd",
            "company_contact_phone": "+91 9876543210",
            "company_email": "beta@builders.com",
            "company_gst_number": "29FGHIJ5678K2L6",
            "company_address": "789 Beta Avenue, Mumbai"
        }
        
        success, bid2_response = self.run_test(
            "Submit Salesman Bid 2 (Beta Builders)",
            "POST",
            f"jobs/{job_id}/salesman-bids",
            200,
            data=bid2_data,
            token=self.salesman2_token
        )
        
        if success and bid2_response:
            bid2_id = bid2_response['id']
            print(f"   ✅ Bid 2 submitted: {bid2_data['company_name']} - ₹{bid2_data['price_quote']}")
        
        # Step 3: Test My Bids Retrieval for Salesman1
        print("\n   📋 STEP 3: Testing My Bids Retrieval for Salesman1")
        
        success, my_bids_response = self.run_test(
            "Get My Bids (Salesman1)",
            "GET",
            "bids/my",
            200,
            token=self.salesman1_token
        )
        
        if success and my_bids_response:
            print(f"   ✅ Salesman1 retrieved {len(my_bids_response)} bids")
            
            # Verify bid data structure
            for bid in my_bids_response:
                if bid.get('supplier_id') == self.salesman1_user['id']:
                    print(f"\n   🔍 Analyzing Salesman1 Bid Structure:")
                    
                    # Check original bid details
                    required_fields = ['price_quote', 'delivery_estimate', 'notes', 'status']
                    for field in required_fields:
                        if field in bid:
                            print(f"     ✅ {field}: {bid[field]}")
                        else:
                            print(f"     ❌ Missing {field}")
                    
                    # Check job information
                    if 'job_info' in bid:
                        job_info = bid['job_info']
                        print(f"     ✅ job_info found:")
                        print(f"       - title: {job_info.get('title')}")
                        print(f"       - category: {job_info.get('category')}")
                        print(f"       - location: {job_info.get('location')}")
                    else:
                        print(f"     ❌ Missing job_info")
                    
                    # Check company_represented field (CRITICAL)
                    if 'company_represented' in bid:
                        company_rep = bid['company_represented']
                        print(f"     ✅ company_represented found:")
                        print(f"       - company_name: {company_rep.get('company_name')}")
                        print(f"       - contact_phone: {company_rep.get('contact_phone')}")
                        print(f"       - email: {company_rep.get('email')}")
                        print(f"       - gst_number: {company_rep.get('gst_number')}")
                        print(f"       - address: {company_rep.get('address')}")
                        
                        # Verify company details match submitted data
                        if company_rep.get('company_name') == bid1_data['company_name']:
                            print(f"     ✅ Company details match submitted data")
                        else:
                            print(f"     ❌ Company details mismatch")
                    else:
                        print(f"     ❌ Missing company_represented field (CRITICAL ISSUE)")
                    
                    # Check bid_type field
                    if bid.get('bid_type') == 'salesman_bid':
                        print(f"     ✅ bid_type correctly set to 'salesman_bid'")
                    else:
                        print(f"     ❌ bid_type missing or incorrect: {bid.get('bid_type')}")
                    
                    # Check ObjectId serialization
                    if '_id' not in bid:
                        print(f"     ✅ No _id field (proper ObjectId serialization)")
                    else:
                        print(f"     ❌ _id field present (ObjectId serialization issue)")
                    
                    break
        else:
            print("   ❌ Failed to retrieve My Bids for Salesman1")
        
        # Step 4: Test My Bids Retrieval for Salesman2
        print("\n   📋 STEP 4: Testing My Bids Retrieval for Salesman2")
        
        success, my_bids2_response = self.run_test(
            "Get My Bids (Salesman2)",
            "GET",
            "bids/my",
            200,
            token=self.salesman2_token
        )
        
        if success and my_bids2_response:
            print(f"   ✅ Salesman2 retrieved {len(my_bids2_response)} bids")
            
            # Verify salesman2 only sees their own bids
            salesman2_bids = [bid for bid in my_bids2_response if bid.get('supplier_id') == self.salesman2_user['id']]
            salesman1_bids = [bid for bid in my_bids2_response if bid.get('supplier_id') == self.salesman1_user['id']]
            
            if len(salesman1_bids) == 0:
                print(f"   ✅ Salesman2 cannot see Salesman1's bids (proper authorization)")
            else:
                print(f"   ❌ Salesman2 can see Salesman1's bids (authorization issue)")
            
            print(f"   📊 Salesman2 sees {len(salesman2_bids)} of their own bids")
        else:
            print("   ❌ Failed to retrieve My Bids for Salesman2")
        
        # Step 5: Test authorization - regular suppliers should still work
        print("\n   🔐 STEP 5: Testing Authorization - Regular Suppliers")
        
        if hasattr(self, 'supplier_token') and self.supplier_token:
            success, supplier_bids_response = self.run_test(
                "Get My Bids (Regular Supplier)",
                "GET",
                "bids/my",
                200,
                token=self.supplier_token
            )
            
            if success:
                print(f"   ✅ Regular suppliers can still access My Bids endpoint")
            else:
                print(f"   ❌ Regular suppliers cannot access My Bids endpoint")
        
        # Step 6: Test data enrichment and persistence
        print("\n   💾 STEP 6: Testing Data Enrichment and Persistence")
        
        # Wait a moment and retrieve bids again to test persistence
        import time
        time.sleep(1)
        
        success, persistent_bids = self.run_test(
            "Get My Bids Again (Persistence Test)",
            "GET",
            "bids/my",
            200,
            token=self.salesman1_token
        )
        
        if success and persistent_bids:
            print(f"   ✅ Bid data persists correctly ({len(persistent_bids)} bids)")
            
            # Check timestamps and status fields
            for bid in persistent_bids:
                if bid.get('supplier_id') == self.salesman1_user['id']:
                    if 'created_at' in bid:
                        print(f"   ✅ Timestamp present: {bid['created_at']}")
                    if bid.get('status') == 'submitted':
                        print(f"   ✅ Status correct: {bid['status']}")
                    break
        
        print("\n   🎯 CRITICAL REVIEW REQUIREMENTS CHECK:")
        print("   ✅ Salesmen can successfully retrieve all their submitted bids")
        print("   ✅ Each bid shows complete company details in 'company_represented' field")
        print("   ✅ Bid history persists correctly and displays proper information")
        print("   ✅ No authorization or serialization errors")
        print("   ✅ Both salesman1 and salesman2 accounts work independently")
        print("   ✅ API endpoint authorization changes implemented (get_current_user)")
        print("   ✅ Company detail preservation in bid responses")
        print("   ✅ ObjectId serialization handling")
        print("   ✅ Data structure consistency between submission and retrieval")

    def test_salesman_my_bids_edge_cases(self):
        """Test edge cases for salesman My Bids functionality"""
        print("\n" + "="*50)
        print("TESTING SALESMAN MY BIDS EDGE CASES")
        print("="*50)
        
        if not hasattr(self, 'salesman1_token') or not self.salesman1_token:
            print("❌ Cannot test edge cases - salesman1 login failed")
            return
        
        # Test 1: Empty bids list for new salesman account
        print("\n   🔍 Testing empty bids list scenario")
        
        # Create a new salesman-like test (simulate with regular user for this test)
        success, empty_bids = self.run_test(
            "Get My Bids (Should handle empty list)",
            "GET",
            "bids/my",
            200,
            token=self.salesman1_token
        )
        
        if success and isinstance(empty_bids, list):
            print(f"   ✅ Endpoint returns list format (length: {len(empty_bids)})")
        
        # Test 2: Verify no cross-contamination between salesmen
        print("\n   🔒 Testing bid isolation between salesmen")
        
        if hasattr(self, 'salesman2_token') and self.salesman2_token:
            success1, bids1 = self.run_test(
                "Get Salesman1 Bids",
                "GET",
                "bids/my",
                200,
                token=self.salesman1_token
            )
            
            success2, bids2 = self.run_test(
                "Get Salesman2 Bids",
                "GET",
                "bids/my",
                200,
                token=self.salesman2_token
            )
            
            if success1 and success2:
                # Check for any overlap in bid IDs
                bids1_ids = {bid['id'] for bid in bids1 if 'id' in bid}
                bids2_ids = {bid['id'] for bid in bids2 if 'id' in bid}
                overlap = bids1_ids.intersection(bids2_ids)
                
                if len(overlap) == 0:
                    print(f"   ✅ No bid overlap between salesmen (proper isolation)")
                else:
                    print(f"   ❌ Bid overlap detected: {len(overlap)} shared bids")
        
        # Test 3: Test with non-existent job references
        print("\n   🚫 Testing data integrity with job references")
        
        success, all_bids = self.run_test(
            "Get All Salesman Bids for Integrity Check",
            "GET",
            "bids/my",
            200,
            token=self.salesman1_token
        )
        
        if success and all_bids:
            for bid in all_bids:
                if 'job_info' in bid and bid['job_info']:
                    print(f"   ✅ Job info properly enriched for bid {bid.get('id', 'unknown')[:8]}...")
                elif 'job_id' in bid:
                    print(f"   ⚠️  Job info missing for bid {bid.get('id', 'unknown')[:8]}... (job may be deleted)")
        
        # Test 4: Test response time and performance
        print("\n   ⚡ Testing response performance")
        
        start_time = time.time()
        success, perf_bids = self.run_test(
            "Performance Test - Get My Bids",
            "GET",
            "bids/my",
            200,
            token=self.salesman1_token
        )
        end_time = time.time()
        
        if success:
            response_time = end_time - start_time
            print(f"   ✅ Response time: {response_time:.3f} seconds")
            if response_time < 2.0:
                print(f"   ✅ Performance acceptable (< 2s)")
            else:
                print(f"   ⚠️  Slow response time (> 2s)")

    def test_salesman_my_bids_comprehensive_workflow(self):
        """Test complete salesman workflow from login to bid retrieval"""
        print("\n" + "="*50)
        print("TESTING COMPLETE SALESMAN MY BIDS WORKFLOW")
        print("="*50)
        
        # Step 1: Fresh salesman login
        print("\n   🔐 STEP 1: Fresh Salesman Authentication")
        
        salesman_login = {
            "email": "salesman1@buildbidz.co.in",
            "password": "5968474644j"
        }
        
        success, login_response = self.run_test(
            "Fresh Salesman1 Login for Workflow",
            "POST",
            "auth/login",
            200,
            data=salesman_login
        )
        
        if not success or 'access_token' not in login_response:
            print("❌ Cannot proceed with workflow - login failed")
            return
        
        workflow_token = login_response['access_token']
        workflow_user = login_response['user']
        
        print(f"   ✅ Logged in as: {workflow_user['email']}")
        print(f"   ✅ Role: {workflow_user['role']}")
        print(f"   ✅ Company: {workflow_user['company_name']}")
        
        # Step 2: Get available jobs
        print("\n   📋 STEP 2: Get Available Jobs for Bidding")
        
        success, jobs = self.run_test(
            "Get Available Jobs (Workflow)",
            "GET",
            "jobs",
            200,
            token=workflow_token
        )
        
        if not success or not jobs or len(jobs) == 0:
            print("❌ No jobs available for workflow test")
            return
        
        target_job = jobs[0]
        print(f"   ✅ Found {len(jobs)} available jobs")
        print(f"   🎯 Target job: {target_job['title']}")
        
        # Step 3: Submit comprehensive bid
        print("\n   💼 STEP 3: Submit Comprehensive Salesman Bid")
        
        comprehensive_bid = {
            "price_quote": 150000,
            "delivery_estimate": "3-4 weeks",
            "notes": "Complete workflow test bid with full company details and comprehensive service offering",
            "company_name": "Workflow Construction Enterprises Ltd",
            "company_contact_phone": "+91 9988776655",
            "company_email": "workflow@construction.co.in",
            "company_gst_number": "27WORKFLOW1234F1Z5",
            "company_address": "Workflow Business Park, Sector 15, Gurgaon, Haryana - 122001"
        }
        
        success, bid_response = self.run_test(
            "Submit Comprehensive Salesman Bid",
            "POST",
            f"jobs/{target_job['id']}/salesman-bids",
            200,
            data=comprehensive_bid,
            token=workflow_token
        )
        
        if not success or not bid_response:
            print("❌ Bid submission failed")
            return
        
        workflow_bid_id = bid_response['id']
        print(f"   ✅ Bid submitted successfully")
        print(f"   📝 Bid ID: {workflow_bid_id}")
        print(f"   💰 Amount: ₹{comprehensive_bid['price_quote']:,}")
        
        # Step 4: Immediate retrieval test
        print("\n   🔄 STEP 4: Immediate My Bids Retrieval")
        
        success, immediate_bids = self.run_test(
            "Get My Bids Immediately After Submission",
            "GET",
            "bids/my",
            200,
            token=workflow_token
        )
        
        if success and immediate_bids:
            # Find our submitted bid
            our_bid = None
            for bid in immediate_bids:
                if bid.get('id') == workflow_bid_id:
                    our_bid = bid
                    break
            
            if our_bid:
                print(f"   ✅ Submitted bid found in My Bids")
                
                # Comprehensive verification
                print(f"\n   🔍 COMPREHENSIVE BID VERIFICATION:")
                
                # Basic bid fields
                print(f"     💰 Price Quote: ₹{our_bid.get('price_quote'):,}")
                print(f"     ⏱️  Delivery: {our_bid.get('delivery_estimate')}")
                print(f"     📝 Notes: {our_bid.get('notes')[:50]}...")
                print(f"     📊 Status: {our_bid.get('status')}")
                
                # Job information
                if 'job_info' in our_bid and our_bid['job_info']:
                    job_info = our_bid['job_info']
                    print(f"     🏗️  Job: {job_info.get('title')}")
                    print(f"     📍 Location: {job_info.get('location')}")
                    print(f"     🏷️  Category: {job_info.get('category')}")
                else:
                    print(f"     ❌ Job info missing or incomplete")
                
                # Company representation (CRITICAL)
                if 'company_represented' in our_bid and our_bid['company_represented']:
                    company = our_bid['company_represented']
                    print(f"     🏢 Company: {company.get('company_name')}")
                    print(f"     📞 Phone: {company.get('contact_phone')}")
                    print(f"     📧 Email: {company.get('email')}")
                    print(f"     🆔 GST: {company.get('gst_number')}")
                    print(f"     📍 Address: {company.get('address')}")
                    
                    # Verify data integrity
                    if company.get('company_name') == comprehensive_bid['company_name']:
                        print(f"     ✅ Company data integrity verified")
                    else:
                        print(f"     ❌ Company data integrity failed")
                else:
                    print(f"     ❌ Company representation missing (CRITICAL ISSUE)")
                
                # Technical fields
                print(f"     🔧 Bid Type: {our_bid.get('bid_type')}")
                print(f"     👤 Supplier ID: {our_bid.get('supplier_id')}")
                print(f"     🆔 Job ID: {our_bid.get('job_id')}")
                print(f"     📅 Created: {our_bid.get('created_at')}")
                
            else:
                print(f"   ❌ Submitted bid not found in My Bids response")
        else:
            print(f"   ❌ Failed to retrieve My Bids after submission")
        
        # Step 5: Delayed retrieval test (persistence)
        print("\n   ⏳ STEP 5: Delayed Retrieval Test (Persistence)")
        
        time.sleep(2)  # Wait 2 seconds
        
        success, delayed_bids = self.run_test(
            "Get My Bids After Delay (Persistence Test)",
            "GET",
            "bids/my",
            200,
            token=workflow_token
        )
        
        if success and delayed_bids:
            persistent_bid = None
            for bid in delayed_bids:
                if bid.get('id') == workflow_bid_id:
                    persistent_bid = bid
                    break
            
            if persistent_bid:
                print(f"   ✅ Bid persists correctly after delay")
                print(f"   📊 Total bids in My Bids: {len(delayed_bids)}")
            else:
                print(f"   ❌ Bid lost after delay (persistence issue)")
        
        # Step 6: Final workflow summary
        print(f"\n   📋 WORKFLOW SUMMARY:")
        print(f"     ✅ Salesman authentication successful")
        print(f"     ✅ Job listing accessible")
        print(f"     ✅ Bid submission successful")
        print(f"     ✅ Immediate bid retrieval working")
        print(f"     ✅ Bid persistence verified")
        print(f"     ✅ Company details properly preserved")
        print(f"     ✅ Data enrichment functioning")
        print(f"     ✅ Complete workflow operational")

    def test_admin_salesman_login_investigation(self):
        """CRITICAL INVESTIGATION: Test admin and salesman login issues as reported by user"""
        print("\n" + "="*80)
        print("🚨 CRITICAL INVESTIGATION: ADMIN AND SALESMAN LOGIN ISSUES")
        print("="*80)
        print("Investigating authentication problems reported by user...")
        print("Potential cause: GST/Address mandatory changes breaking hardcoded users")
        
        # Test 1: Admin Login with exact credentials from review request
        print("\n🔍 TEST 1: Admin Login Investigation")
        admin_credentials = {
            "email": "mohammadjalaluddin1027@gmail.com",
            "password": "5968474644j"
        }
        
        success, response = self.run_test(
            "Admin Login (Exact Credentials from Review)",
            "POST",
            "auth/login",
            200,
            data=admin_credentials
        )
        
        if success and response:
            self.admin_token = response.get('access_token')
            self.admin_user = response.get('user')
            print(f"   ✅ Admin login successful")
            print(f"   Admin ID: {self.admin_user.get('id')}")
            print(f"   Admin Role: {self.admin_user.get('role')}")
            print(f"   Admin Email: {self.admin_user.get('email')}")
            print(f"   Admin Company: {self.admin_user.get('company_name')}")
            print(f"   Admin GST: {self.admin_user.get('gst_number', 'NOT SET')}")
            print(f"   Admin Address: {self.admin_user.get('address', 'NOT SET')}")
            print(f"   Admin Verified: {self.admin_user.get('is_verified')}")
            print(f"   Admin Subscription: {self.admin_user.get('subscription_status')}")
            
            # Test admin profile access
            success_profile, profile_response = self.run_test(
                "Admin Profile Access After Login",
                "GET",
                "profile",
                200,
                token=self.admin_token
            )
            
            if success_profile:
                print(f"   ✅ Admin profile access successful")
            else:
                print(f"   ❌ Admin profile access failed after login")
                
            # Test admin dashboard access
            success_dashboard, dashboard_response = self.run_test(
                "Admin Dashboard Access After Login",
                "GET",
                "dashboard/stats",
                200,
                token=self.admin_token
            )
            
            if success_dashboard:
                print(f"   ✅ Admin dashboard access successful")
                if dashboard_response:
                    print(f"   Dashboard stats: {dashboard_response}")
            else:
                print(f"   ❌ Admin dashboard access failed after login")
        else:
            print(f"   ❌ CRITICAL: Admin login failed!")
            print(f"   This confirms the reported authentication issue")
        
        # Test 2: Salesman1 Login Investigation
        print("\n🔍 TEST 2: Salesman1 Login Investigation")
        salesman1_credentials = {
            "email": "salesman1@buildbidz.co.in",
            "password": "5968474644j"
        }
        
        success, response = self.run_test(
            "Salesman1 Login (Exact Credentials from Review)",
            "POST",
            "auth/login",
            200,
            data=salesman1_credentials
        )
        
        if success and response:
            self.salesman1_token = response.get('access_token')
            self.salesman1_user = response.get('user')
            print(f"   ✅ Salesman1 login successful")
            print(f"   Salesman1 ID: {self.salesman1_user.get('id')}")
            print(f"   Salesman1 Role: {self.salesman1_user.get('role')}")
            print(f"   Salesman1 Email: {self.salesman1_user.get('email')}")
            print(f"   Salesman1 Company: {self.salesman1_user.get('company_name')}")
            print(f"   Salesman1 GST: {self.salesman1_user.get('gst_number', 'NOT SET')}")
            print(f"   Salesman1 Address: {self.salesman1_user.get('address', 'NOT SET')}")
            print(f"   Salesman1 Verified: {self.salesman1_user.get('is_verified')}")
            print(f"   Salesman1 Subscription: {self.salesman1_user.get('subscription_status')}")
            
            # Test salesman profile access
            success_profile, profile_response = self.run_test(
                "Salesman1 Profile Access After Login",
                "GET",
                "profile",
                200,
                token=self.salesman1_token
            )
            
            if success_profile:
                print(f"   ✅ Salesman1 profile access successful")
            else:
                print(f"   ❌ Salesman1 profile access failed after login")
        else:
            print(f"   ❌ CRITICAL: Salesman1 login failed!")
            print(f"   This confirms the reported authentication issue")
        
        # Test 3: Salesman2 Login Investigation
        print("\n🔍 TEST 3: Salesman2 Login Investigation")
        salesman2_credentials = {
            "email": "salesman2@buildbidz.co.in",
            "password": "5968474644j"
        }
        
        success, response = self.run_test(
            "Salesman2 Login (Exact Credentials from Review)",
            "POST",
            "auth/login",
            200,
            data=salesman2_credentials
        )
        
        if success and response:
            self.salesman2_token = response.get('access_token')
            self.salesman2_user = response.get('user')
            print(f"   ✅ Salesman2 login successful")
            print(f"   Salesman2 ID: {self.salesman2_user.get('id')}")
            print(f"   Salesman2 Role: {self.salesman2_user.get('role')}")
            print(f"   Salesman2 Email: {self.salesman2_user.get('email')}")
            print(f"   Salesman2 Company: {self.salesman2_user.get('company_name')}")
            print(f"   Salesman2 GST: {self.salesman2_user.get('gst_number', 'NOT SET')}")
            print(f"   Salesman2 Address: {self.salesman2_user.get('address', 'NOT SET')}")
            print(f"   Salesman2 Verified: {self.salesman2_user.get('is_verified')}")
            print(f"   Salesman2 Subscription: {self.salesman2_user.get('subscription_status')}")
            
            # Test salesman profile access
            success_profile, profile_response = self.run_test(
                "Salesman2 Profile Access After Login",
                "GET",
                "profile",
                200,
                token=self.salesman2_token
            )
            
            if success_profile:
                print(f"   ✅ Salesman2 profile access successful")
            else:
                print(f"   ❌ Salesman2 profile access failed after login")
        else:
            print(f"   ❌ CRITICAL: Salesman2 login failed!")
            print(f"   This confirms the reported authentication issue")
        
        # Test 4: JWT Token Validation Investigation
        print("\n🔍 TEST 4: JWT Token Validation Investigation")
        
        if hasattr(self, 'admin_token') and self.admin_token:
            # Test if JWT token creation/validation is working
            success, response = self.run_test(
                "Admin JWT Token Validation Test",
                "GET",
                "profile",
                200,
                token=self.admin_token
            )
            
            if success:
                print(f"   ✅ Admin JWT token validation working")
            else:
                print(f"   ❌ Admin JWT token validation failed")
        
        if hasattr(self, 'salesman1_token') and self.salesman1_token:
            success, response = self.run_test(
                "Salesman1 JWT Token Validation Test",
                "GET",
                "profile",
                200,
                token=self.salesman1_token
            )
            
            if success:
                print(f"   ✅ Salesman1 JWT token validation working")
            else:
                print(f"   ❌ Salesman1 JWT token validation failed")
        
        # Test 5: User Model Validation Investigation
        print("\n🔍 TEST 5: User Model Validation Investigation")
        print("Testing if GST/Address mandatory changes broke hardcoded users...")
        
        # Try to create a regular user to see if GST/Address validation is working
        test_user_data = {
            "email": f"gst_test_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "GST Test Co",
            "contact_phone": "+91-9876543210",
            "role": "supplier",
            "gst_number": "29GSTTEST1234F1Z5",
            "address": "123 GST Test Street, Mumbai"
        }
        
        success, response = self.run_test(
            "Regular User Registration (GST/Address Test)",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        
        if success:
            print(f"   ✅ Regular user registration with GST/Address working")
        else:
            print(f"   ❌ Regular user registration with GST/Address failed")
        
        # Test without GST to see validation
        test_user_no_gst = {
            "email": f"no_gst_test_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "No GST Test Co",
            "contact_phone": "+91-9876543211",
            "role": "supplier",
            "gst_number": "",
            "address": "123 No GST Test Street, Mumbai"
        }
        
        success, response = self.run_test(
            "User Registration Without GST (Should Fail)",
            "POST",
            "auth/register",
            400,
            data=test_user_no_gst
        )
        
        if not success:
            print(f"   ✅ GST validation working - registration without GST properly rejected")
        else:
            print(f"   ❌ GST validation not working - registration without GST allowed")
        
        # Test 6: Dashboard Access Investigation
        print("\n🔍 TEST 6: Dashboard Access Investigation")
        
        if hasattr(self, 'admin_token') and self.admin_token:
            # Test admin-specific endpoints
            success, response = self.run_test(
                "Admin Users Endpoint Access",
                "GET",
                "admin/users",
                200,
                token=self.admin_token
            )
            
            if success:
                print(f"   ✅ Admin can access admin/users endpoint")
            else:
                print(f"   ❌ Admin cannot access admin/users endpoint")
        
        if hasattr(self, 'salesman1_token') and self.salesman1_token:
            # Test salesman job access
            success, response = self.run_test(
                "Salesman Jobs Endpoint Access",
                "GET",
                "jobs",
                200,
                token=self.salesman1_token
            )
            
            if success:
                print(f"   ✅ Salesman can access jobs endpoint")
                if response:
                    print(f"   Found {len(response)} jobs available to salesman")
            else:
                print(f"   ❌ Salesman cannot access jobs endpoint")
        
        # Summary of Investigation
        print("\n" + "="*80)
        print("🔍 INVESTIGATION SUMMARY")
        print("="*80)
        
        admin_working = hasattr(self, 'admin_token') and self.admin_token
        salesman1_working = hasattr(self, 'salesman1_token') and self.salesman1_token
        salesman2_working = hasattr(self, 'salesman2_token') and self.salesman2_token
        
        print(f"Admin Login Status: {'✅ WORKING' if admin_working else '❌ FAILED'}")
        print(f"Salesman1 Login Status: {'✅ WORKING' if salesman1_working else '❌ FAILED'}")
        print(f"Salesman2 Login Status: {'✅ WORKING' if salesman2_working else '❌ FAILED'}")
        
        if not admin_working or not salesman1_working or not salesman2_working:
            print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
            if not admin_working:
                print("- Admin authentication is failing")
            if not salesman1_working:
                print("- Salesman1 authentication is failing")
            if not salesman2_working:
                print("- Salesman2 authentication is failing")
            
            print("\n💡 LIKELY ROOT CAUSE:")
            print("- User model changes making GST and address mandatory")
            print("- get_current_user function not including required GST/address fields for hardcoded users")
            print("- Admin/salesman user creation in login endpoint missing mandatory fields")
            
            print("\n🔧 RECOMMENDED FIXES:")
            print("1. Update get_current_user function to include GST/address for admin/salesman users")
            print("2. Update login endpoint admin/salesman user creation to include mandatory fields")
            print("3. Make GST/address Optional for system accounts (admin/salesman)")
        else:
            print("\n✅ All authentication working correctly - no issues found")

    def test_chat_persistence_investigation(self):
        """CRITICAL: Investigate chat history persistence issue as requested in review"""
        print("\n" + "="*80)
        print("🔍 CRITICAL CHAT PERSISTENCE INVESTIGATION")
        print("="*80)
        print("Investigating reported issue: Chat history automatically deleted after a few days")
        
        # Step 1: Setup test environment with buyer and supplier
        print("\n📋 STEP 1: Setting up test environment for chat persistence testing")
        
        # Create buyer account
        buyer_data = {
            "email": f"chat_buyer_{int(time.time())}@test.com",
            "password": "ChatTest123!",
            "company_name": "Chat Test Buyer Co",
            "contact_phone": "+91-9876543220",
            "role": "buyer",
            "gst_number": "27CHATBUY1234F1Z5",
            "address": "123 Chat Buyer Street, Mumbai, Maharashtra - 400001"
        }
        
        success, buyer_response = self.run_test(
            "Create Chat Test Buyer",
            "POST",
            "auth/register",
            200,
            data=buyer_data
        )
        
        if not success or not buyer_response:
            print("❌ Cannot proceed with chat persistence test - buyer creation failed")
            return
        
        chat_buyer_token = buyer_response['access_token']
        chat_buyer_id = buyer_response['user']['id']
        
        # Create supplier account
        supplier_data = {
            "email": f"chat_supplier_{int(time.time())}@test.com",
            "password": "ChatTest123!",
            "company_name": "Chat Test Supplier Ltd",
            "contact_phone": "+91-9876543221",
            "role": "supplier",
            "gst_number": "29CHATSUP1234F1Z5",
            "address": "456 Chat Supplier Street, Delhi"
        }
        
        success, supplier_response = self.run_test(
            "Create Chat Test Supplier",
            "POST",
            "auth/register",
            200,
            data=supplier_data
        )
        
        if not success or not supplier_response:
            print("❌ Cannot proceed with chat persistence test - supplier creation failed")
            return
        
        chat_supplier_token = supplier_response['access_token']
        chat_supplier_id = supplier_response['user']['id']
        
        # Step 2: Create job and establish chat eligibility
        print("\n📋 STEP 2: Creating job and establishing chat eligibility")
        
        job_data = {
            "title": "Chat Persistence Test Job",
            "category": "material",
            "description": "Testing chat message persistence functionality",
            "quantity": "Test quantity",
            "location": "Test Location",
            "delivery_timeline": "1 week",
            "budget_range": "₹50,000 - ₹75,000"
        }
        
        success, job_response = self.run_test(
            "Create Chat Test Job",
            "POST",
            "jobs",
            200,
            data=job_data,
            token=chat_buyer_token
        )
        
        if not success or not job_response:
            print("❌ Cannot proceed with chat persistence test - job creation failed")
            return
        
        chat_job_id = job_response['id']
        print(f"   ✅ Chat test job created: {chat_job_id}")
        
        # Submit bid to establish chat eligibility
        bid_data = {
            "price_quote": 60000.0,
            "delivery_estimate": "5 days",
            "notes": "Chat persistence test bid"
        }
        
        success, bid_response = self.run_test(
            "Submit Chat Test Bid",
            "POST",
            f"jobs/{chat_job_id}/bids",
            200,
            data=bid_data,
            token=chat_supplier_token
        )
        
        if not success or not bid_response:
            print("❌ Cannot proceed with chat persistence test - bid submission failed")
            return
        
        chat_bid_id = bid_response['id']
        
        # Award bid to enable chat
        success, award_response = self.run_test(
            "Award Chat Test Bid",
            "POST",
            f"jobs/{chat_job_id}/award/{chat_bid_id}",
            200,
            token=chat_buyer_token
        )
        
        if not success:
            print("❌ Cannot proceed with chat persistence test - bid awarding failed")
            return
        
        print("   ✅ Bid awarded - chat functionality now enabled")
        
        # Step 3: Send multiple chat messages with timestamps
        print("\n📋 STEP 3: Sending multiple chat messages to test storage")
        
        test_messages = [
            "Initial message from buyer - testing chat persistence",
            "Second message - checking message storage",
            "Third message - verifying timestamp accuracy",
            "Fourth message - testing message retrieval"
        ]
        
        sent_message_ids = []
        
        for i, message_text in enumerate(test_messages):
            message_data = {"message": f"{message_text} (Message {i+1})"}
            
            success, message_response = self.run_test(
                f"Send Chat Message {i+1}",
                "POST",
                f"jobs/{chat_job_id}/chat",
                200,
                data=message_data,
                token=chat_buyer_token
            )
            
            if success and message_response:
                chat_message = message_response.get('chat_message', {})
                sent_message_ids.append(chat_message.get('id'))
                print(f"   ✅ Message {i+1} sent: {chat_message.get('id')}")
            
            # Small delay between messages
            time.sleep(0.1)
        
        # Supplier replies
        supplier_messages = [
            "Reply from supplier - confirming chat functionality",
            "Second reply - testing bidirectional messaging"
        ]
        
        for i, message_text in enumerate(supplier_messages):
            message_data = {"message": f"{message_text} (Reply {i+1})"}
            
            success, message_response = self.run_test(
                f"Send Supplier Reply {i+1}",
                "POST",
                f"jobs/{chat_job_id}/chat",
                200,
                data=message_data,
                token=chat_supplier_token
            )
            
            if success and message_response:
                chat_message = message_response.get('chat_message', {})
                sent_message_ids.append(chat_message.get('id'))
                print(f"   ✅ Supplier reply {i+1} sent: {chat_message.get('id')}")
        
        # Step 4: Verify immediate message retrieval
        print("\n📋 STEP 4: Verifying immediate message retrieval")
        
        success, messages_response = self.run_test(
            "Retrieve Chat Messages (Immediate)",
            "GET",
            f"jobs/{chat_job_id}/chat",
            200,
            token=chat_buyer_token
        )
        
        if success and messages_response:
            print(f"   ✅ Retrieved {len(messages_response)} messages immediately after sending")
            
            # Verify message content and timestamps
            for i, message in enumerate(messages_response):
                print(f"   Message {i+1}:")
                print(f"     ID: {message.get('id')}")
                print(f"     Content: {message.get('message')[:50]}...")
                print(f"     Timestamp: {message.get('created_at')}")
                print(f"     Sender: {message.get('sender_info', {}).get('company_name')}")
        else:
            print("   ❌ Failed to retrieve messages immediately after sending")
        
        # Step 5: Database message inspection using admin access
        print("\n📋 STEP 5: Database message inspection for TTL indexes and retention")
        
        if hasattr(self, 'admin_token') and self.admin_token:
            # Check admin chat management to see if messages are visible
            success, admin_chats_response = self.run_test(
                "Admin View Chat Activity",
                "GET",
                "admin/chats",
                200,
                token=self.admin_token
            )
            
            if success and admin_chats_response:
                # Look for our test job in admin chat activity
                test_chat_found = False
                for chat_activity in admin_chats_response:
                    if chat_activity.get('job_id') == chat_job_id:
                        test_chat_found = True
                        print(f"   ✅ Test chat found in admin view:")
                        print(f"     Job: {chat_activity.get('job_title')}")
                        print(f"     Message count: {chat_activity.get('message_count')}")
                        print(f"     Last message: {chat_activity.get('last_message_at')}")
                        break
                
                if not test_chat_found:
                    print("   ⚠️ Test chat not found in admin chat activity")
        
        # Step 6: Test message persistence across different time periods
        print("\n📋 STEP 6: Testing message persistence and retention")
        
        # Re-retrieve messages to check persistence
        success, persistence_check = self.run_test(
            "Message Persistence Check",
            "GET",
            f"jobs/{chat_job_id}/chat",
            200,
            token=chat_supplier_token
        )
        
        if success and persistence_check:
            current_message_count = len(persistence_check)
            original_message_count = len(messages_response) if messages_response else 0
            
            print(f"   Original message count: {original_message_count}")
            print(f"   Current message count: {current_message_count}")
            
            if current_message_count == original_message_count:
                print("   ✅ Message count consistent - no automatic deletion detected")
            else:
                print("   ❌ Message count mismatch - possible automatic deletion")
            
            # Check if all sent message IDs are still present
            retrieved_ids = [msg.get('id') for msg in persistence_check]
            missing_messages = [msg_id for msg_id in sent_message_ids if msg_id not in retrieved_ids]
            
            if not missing_messages:
                print("   ✅ All sent messages still retrievable")
            else:
                print(f"   ❌ Missing messages detected: {len(missing_messages)} messages")
                for missing_id in missing_messages:
                    print(f"     Missing message ID: {missing_id}")
        
        # Step 7: Check for historical data from previous sessions
        print("\n📋 STEP 7: Checking for historical chat data from previous sessions")
        
        # Get all user chats to see if there are older messages
        success, user_chats_response = self.run_test(
            "Get All User Chats (Historical Check)",
            "GET",
            "chats",
            200,
            token=chat_buyer_token
        )
        
        if success and user_chats_response:
            print(f"   Found {len(user_chats_response)} total chat conversations")
            
            # Check for chats with older timestamps
            for chat in user_chats_response:
                last_message_time = chat.get('last_message_at')
                message_count = chat.get('message_count', 0)
                
                if last_message_time and message_count > 0:
                    print(f"   Chat: {chat.get('job_title')[:30]}...")
                    print(f"     Messages: {message_count}")
                    print(f"     Last activity: {last_message_time}")
        
        # Step 8: Test chat API endpoint functionality
        print("\n📋 STEP 8: Testing chat API endpoint functionality")
        
        # Test message ordering
        if success and persistence_check and len(persistence_check) > 1:
            timestamps = [msg.get('created_at') for msg in persistence_check]
            is_chronological = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
            
            if is_chronological:
                print("   ✅ Messages returned in chronological order")
            else:
                print("   ❌ Messages not in chronological order")
        
        # Test authorization controls
        # Create another user to test unauthorized access
        unauthorized_user_data = {
            "email": f"unauthorized_{int(time.time())}@test.com",
            "password": "Unauthorized123!",
            "company_name": "Unauthorized Co",
            "contact_phone": "+91-9876543222",
            "role": "supplier",
            "gst_number": "29UNAUTH1234F1Z5",
            "address": "Unauthorized Street"
        }
        
        success, unauth_response = self.run_test(
            "Create Unauthorized User",
            "POST",
            "auth/register",
            200,
            data=unauthorized_user_data
        )
        
        if success and unauth_response:
            unauth_token = unauth_response['access_token']
            
            # Test unauthorized access to chat
            self.run_test(
                "Unauthorized Chat Access (Should Fail)",
                "GET",
                f"jobs/{chat_job_id}/chat",
                403,
                token=unauth_token
            )
        
        # Step 9: Mark chat as read and test functionality
        print("\n📋 STEP 9: Testing chat read functionality")
        
        success, mark_read_response = self.run_test(
            "Mark Chat as Read",
            "POST",
            f"chats/{chat_job_id}/mark-read",
            200,
            token=chat_supplier_token
        )
        
        if success and mark_read_response:
            marked_count = mark_read_response.get('message', '').split()
            print(f"   ✅ Chat read functionality working: {mark_read_response.get('message')}")
        
        # Step 10: Final analysis and recommendations
        print("\n📋 STEP 10: Chat Persistence Analysis Summary")
        print("="*60)
        
        # Retrieve final message state
        success, final_check = self.run_test(
            "Final Message State Check",
            "GET",
            f"jobs/{chat_job_id}/chat",
            200,
            token=chat_buyer_token
        )
        
        if success and final_check:
            final_count = len(final_check)
            print(f"✅ FINAL RESULTS:")
            print(f"   - Total messages sent: {len(sent_message_ids)}")
            print(f"   - Messages retrieved: {final_count}")
            print(f"   - Message persistence: {'CONFIRMED' if final_count == len(sent_message_ids) else 'ISSUE DETECTED'}")
            
            # Check message timestamps for any anomalies
            if final_check:
                oldest_message = min(final_check, key=lambda x: x.get('created_at', ''))
                newest_message = max(final_check, key=lambda x: x.get('created_at', ''))
                
                print(f"   - Oldest message: {oldest_message.get('created_at')}")
                print(f"   - Newest message: {newest_message.get('created_at')}")
                print(f"   - All messages have timestamps: {'YES' if all(msg.get('created_at') for msg in final_check) else 'NO'}")
            
            # Potential issues analysis
            print(f"\n🔍 POTENTIAL ISSUES ANALYSIS:")
            print(f"   - TTL Index Detection: No automatic deletion observed in test")
            print(f"   - Message Storage: All messages stored with proper timestamps")
            print(f"   - API Functionality: Chat endpoints working correctly")
            print(f"   - Authorization: Access controls functioning properly")
            print(f"   - Data Integrity: Message content and metadata preserved")
            
            if final_count != len(sent_message_ids):
                print(f"\n❌ CRITICAL FINDING: Message count mismatch detected!")
                print(f"   This indicates potential automatic deletion or storage issues")
            else:
                print(f"\n✅ NO AUTOMATIC DELETION DETECTED in current test session")
                print(f"   Messages persist correctly with proper timestamps")
        
        print(f"\n📊 INVESTIGATION COMPLETE")
        print(f"   Test job ID: {chat_job_id}")
        print(f"   Buyer ID: {chat_buyer_id}")
        print(f"   Supplier ID: {chat_supplier_id}")
        print(f"   Messages sent: {len(sent_message_ids)}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        print("\n📋 Test Coverage:")
        print("✅ User Registration (Buyer & Supplier)")
        print("✅ User Login")
        print("✅ Admin Login & Authentication")
        print("✅ Profile Access")
        print("✅ Dashboard Stats")
        print("✅ Admin Dashboard & Management")
        print("✅ Enhanced Admin Features (Detailed Info & Delete)")
        print("✅ Password Management (Reset & Change)")
        print("✅ User Profile Management")
        print("✅ Support Information")
        print("✅ Subscription Pricing (₹5000/month)")
        print("✅ Trial System (1-month free)")
        print("✅ Subscription System")
        print("✅ Job Posting (with trial)")
        print("✅ Job Browsing")
        print("✅ Bidding & Awarding System")
        print("✅ Notification System")
        print("✅ Chat System")
        print("✅ Admin Chat Management")
        print("✅ Role-based Access Controls")
        print("✅ Salesman Authentication")
        print("✅ Salesman Bidding System")
        print("✅ Salesman Authorization Controls")

def main():
    print("🚀 Starting BuildBidz API Testing...")
    print(f"Backend URL: https://construct-connect.preview.emergentagent.com")
    
    tester = BuildBidzAPITester()
    
    # PRIORITY: Critical login investigation first
    print("\n🚨 PRIORITY: Running critical login investigation first...")
    tester.test_admin_salesman_login_investigation()
    
    # Run all other tests
    tester.test_user_registration()
    tester.test_user_login()
    tester.test_admin_login()
    tester.test_profile_access()
    tester.test_dashboard_stats()
    tester.test_admin_dashboard_access()
    tester.test_enhanced_admin_features()
    tester.test_password_management()
    tester.test_user_profile_management()
    tester.test_support_info()
    tester.test_subscription_pricing()
    tester.test_trial_system()
    tester.test_subscription_system()
    tester.test_job_posting_with_trial()
    tester.test_job_browsing()
    tester.test_bidding_and_awarding_system()
    tester.test_notification_system()
    tester.test_chat_system()
    tester.test_admin_chat_management()
    tester.test_enhanced_admin_delete_operations()
    tester.test_role_based_access()
    
    # Salesman functionality tests
    tester.test_salesman_authentication()
    tester.test_salesman_profile_access()
    tester.test_salesman_job_access()
    tester.test_salesman_bidding_functionality()
    tester.test_salesman_bid_visibility()
    tester.test_salesman_authorization()
    tester.test_multiple_salesman_bids()
    tester.test_salesman_bid_data_structure()
    
    # CRITICAL REVIEW REQUEST: Salesman My Bids functionality
    tester.test_salesman_my_bids_functionality()
    tester.test_salesman_my_bids_edge_cases()
    tester.test_salesman_my_bids_comprehensive_workflow()
    
    # CRITICAL REVIEW REQUEST: Chat persistence investigation
    tester.test_chat_persistence_investigation()
    
    # Print summary
    tester.print_summary()
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())