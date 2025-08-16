import requests
import sys
import json
from datetime import datetime
import time

class BuildBidzAPITester:
    def __init__(self, base_url="https://conmarket.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.supplier_token = None
        self.buyer_user = None
        self.supplier_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.job_id = None
        self.bid_id = None

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
        print("✅ Profile Access")
        print("✅ Dashboard Stats")
        print("✅ Subscription System")
        print("✅ Job Posting (without subscription)")
        print("✅ Job Browsing")
        print("✅ Bidding System")
        print("✅ Role-based Access Controls")

def main():
    print("🚀 Starting BuildBidz API Testing...")
    print(f"Backend URL: https://conmarket.preview.emergentagent.com")
    
    tester = BuildBidzAPITester()
    
    # Run all tests
    tester.test_user_registration()
    tester.test_user_login()
    tester.test_profile_access()
    tester.test_dashboard_stats()
    tester.test_subscription_system()
    tester.test_job_posting_without_subscription()
    tester.test_job_browsing()
    tester.test_bidding_system()
    tester.test_role_based_access()
    
    # Print summary
    tester.print_summary()
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())