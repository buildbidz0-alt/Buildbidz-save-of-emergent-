import requests
import sys
import json
from datetime import datetime
import time

class CriticalIssuesTester:
    def __init__(self, base_url="https://construct-connect.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.buyer_token = None
        self.supplier_token = None
        self.test_job_id = None
        self.test_bid_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []

    def log_critical_issue(self, issue_type, description, details=None):
        """Log a critical issue found during testing"""
        self.critical_issues.append({
            "type": issue_type,
            "description": description,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

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
                    return False, error_detail
                except:
                    print(f"   Response: {response.text}")
                    return False, {"error": response.text}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {"error": str(e)}

    def setup_test_environment(self):
        """Setup test environment with admin, buyer, and supplier accounts"""
        print("\n" + "="*60)
        print("SETTING UP TEST ENVIRONMENT")
        print("="*60)
        
        # Login as admin
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
            print(f"✅ Admin logged in successfully")
        else:
            self.log_critical_issue("AUTH", "Admin login failed", response)
            return False

        # Create test buyer
        buyer_data = {
            "email": f"test_buyer_{int(time.time())}@buildbidz.com",
            "password": "TestBuyer123!",
            "company_name": "Test Construction Company",
            "contact_phone": "+91-9876543210",
            "role": "buyer",
            "gst_number": "29TESTBUY1234F1Z5",
            "address": "123 Test Street, Mumbai"
        }
        
        success, response = self.run_test(
            "Create Test Buyer",
            "POST",
            "auth/register",
            200,
            data=buyer_data
        )
        
        if success and 'access_token' in response:
            self.buyer_token = response['access_token']
            self.buyer_user = response['user']
            print(f"✅ Test buyer created: {self.buyer_user['id']}")
        else:
            self.log_critical_issue("AUTH", "Test buyer creation failed", response)
            return False

        # Create test supplier
        supplier_data = {
            "email": f"test_supplier_{int(time.time())}@buildbidz.com",
            "password": "TestSupplier123!",
            "company_name": "Test Supplier Company",
            "contact_phone": "+91-9876543211",
            "role": "supplier",
            "gst_number": "29TESTSUP1234F1Z5",
            "address": "456 Supplier Street, Delhi"
        }
        
        success, response = self.run_test(
            "Create Test Supplier",
            "POST",
            "auth/register",
            200,
            data=supplier_data
        )
        
        if success and 'access_token' in response:
            self.supplier_token = response['access_token']
            self.supplier_user = response['user']
            print(f"✅ Test supplier created: {self.supplier_user['id']}")
        else:
            self.log_critical_issue("AUTH", "Test supplier creation failed", response)
            return False

        # Create a test job
        job_data = {
            "title": "Critical Test Construction Job",
            "category": "material",
            "description": "Test job for critical issues testing - need cement and steel",
            "quantity": "100 bags cement, 50 tons steel",
            "location": "Mumbai, Maharashtra",
            "delivery_timeline": "2 weeks",
            "budget_range": "₹5,00,000 - ₹7,00,000"
        }
        
        success, response = self.run_test(
            "Create Test Job",
            "POST",
            "jobs",
            200,
            data=job_data,
            token=self.buyer_token
        )
        
        if success and 'id' in response:
            self.test_job_id = response['id']
            print(f"✅ Test job created: {self.test_job_id}")
        else:
            self.log_critical_issue("JOB_POSTING", "Test job creation failed", response)
            return False

        # Create a test bid
        bid_data = {
            "price_quote": 600000.0,
            "delivery_estimate": "10 days",
            "notes": "High quality materials with competitive pricing"
        }
        
        success, response = self.run_test(
            "Create Test Bid",
            "POST",
            f"jobs/{self.test_job_id}/bids",
            200,
            data=bid_data,
            token=self.supplier_token
        )
        
        if success and 'id' in response:
            self.test_bid_id = response['id']
            print(f"✅ Test bid created: {self.test_bid_id}")
        else:
            self.log_critical_issue("BIDDING", "Test bid creation failed", response)
            return False

        # Award the bid to enable chat functionality
        success, response = self.run_test(
            "Award Test Bid",
            "POST",
            f"jobs/{self.test_job_id}/award/{self.test_bid_id}",
            200,
            token=self.buyer_token
        )
        
        if success:
            print(f"✅ Test bid awarded successfully")
        else:
            self.log_critical_issue("BID_AWARDING", "Test bid awarding failed", response)

        return True

    def test_messaging_system(self):
        """Test messaging system problems"""
        print("\n" + "="*60)
        print("TESTING MESSAGING SYSTEM PROBLEMS")
        print("="*60)
        
        # Test 1: GET /api/chats endpoint
        success, response = self.run_test(
            "GET /api/chats (Buyer)",
            "GET",
            "chats",
            200,
            token=self.buyer_token
        )
        
        if not success:
            self.log_critical_issue("MESSAGING", "GET /api/chats failed for buyer", response)
        elif not isinstance(response, list):
            self.log_critical_issue("MESSAGING", "GET /api/chats returned invalid format", response)
        else:
            print(f"   ✅ Buyer has {len(response)} active chats")
            if len(response) == 0:
                self.log_critical_issue("MESSAGING", "Buyer has no active chats despite awarded job", response)

        success, response = self.run_test(
            "GET /api/chats (Supplier)",
            "GET",
            "chats",
            200,
            token=self.supplier_token
        )
        
        if not success:
            self.log_critical_issue("MESSAGING", "GET /api/chats failed for supplier", response)
        elif not isinstance(response, list):
            self.log_critical_issue("MESSAGING", "GET /api/chats returned invalid format", response)
        else:
            print(f"   ✅ Supplier has {len(response)} active chats")
            if len(response) == 0:
                self.log_critical_issue("MESSAGING", "Supplier has no active chats despite awarded bid", response)

        # Test 2: GET /api/jobs/{job_id}/chat endpoint
        success, response = self.run_test(
            "GET /api/jobs/{job_id}/chat (Buyer)",
            "GET",
            f"jobs/{self.test_job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if not success:
            self.log_critical_issue("MESSAGING", f"GET /api/jobs/{self.test_job_id}/chat failed for buyer", response)
        elif not isinstance(response, list):
            self.log_critical_issue("MESSAGING", "Job chat endpoint returned invalid format", response)
        else:
            print(f"   ✅ Job chat has {len(response)} messages")

        success, response = self.run_test(
            "GET /api/jobs/{job_id}/chat (Supplier)",
            "GET",
            f"jobs/{self.test_job_id}/chat",
            200,
            token=self.supplier_token
        )
        
        if not success:
            self.log_critical_issue("MESSAGING", f"GET /api/jobs/{self.test_job_id}/chat failed for supplier", response)

        # Test 3: POST /api/jobs/{job_id}/chat endpoint
        message_data = {
            "message": "Hello! Thank you for awarding the bid. When can we start the project?"
        }
        
        success, response = self.run_test(
            "POST /api/jobs/{job_id}/chat (Supplier)",
            "POST",
            f"jobs/{self.test_job_id}/chat",
            200,
            data=message_data,
            token=self.supplier_token
        )
        
        if not success:
            self.log_critical_issue("MESSAGING", "Supplier cannot send chat messages", response)
        else:
            print(f"   ✅ Supplier sent message successfully")

        buyer_message_data = {
            "message": "Great! We can start next Monday. Please confirm the delivery schedule."
        }
        
        success, response = self.run_test(
            "POST /api/jobs/{job_id}/chat (Buyer)",
            "POST",
            f"jobs/{self.test_job_id}/chat",
            200,
            data=buyer_message_data,
            token=self.buyer_token
        )
        
        if not success:
            self.log_critical_issue("MESSAGING", "Buyer cannot send chat messages", response)
        else:
            print(f"   ✅ Buyer sent message successfully")

        # Test 4: POST /api/chats/{job_id}/mark-read endpoint
        success, response = self.run_test(
            "POST /api/chats/{job_id}/mark-read (Buyer)",
            "POST",
            f"chats/{self.test_job_id}/mark-read",
            200,
            token=self.buyer_token
        )
        
        if not success:
            self.log_critical_issue("MESSAGING", "Mark messages as read failed for buyer", response)
        else:
            print(f"   ✅ Buyer marked messages as read")

        success, response = self.run_test(
            "POST /api/chats/{job_id}/mark-read (Supplier)",
            "POST",
            f"chats/{self.test_job_id}/mark-read",
            200,
            token=self.supplier_token
        )
        
        if not success:
            self.log_critical_issue("MESSAGING", "Mark messages as read failed for supplier", response)
        else:
            print(f"   ✅ Supplier marked messages as read")

    def test_bid_visibility_for_buyers(self):
        """Test bid details not showing for buyers"""
        print("\n" + "="*60)
        print("TESTING BID VISIBILITY FOR BUYERS")
        print("="*60)
        
        # Test GET /api/jobs/{job_id}/bids endpoint for buyers
        success, response = self.run_test(
            "GET /api/jobs/{job_id}/bids (Buyer)",
            "GET",
            f"jobs/{self.test_job_id}/bids",
            200,
            token=self.buyer_token
        )
        
        if not success:
            self.log_critical_issue("BID_VISIBILITY", "Buyer cannot view bids on their job", response)
        elif not isinstance(response, list):
            self.log_critical_issue("BID_VISIBILITY", "Bids endpoint returned invalid format", response)
        elif len(response) == 0:
            self.log_critical_issue("BID_VISIBILITY", "No bids returned for job with known bid", response)
        else:
            print(f"   ✅ Found {len(response)} bids for the job")
            
            # Check bid enrichment (supplier details)
            for bid in response:
                if 'supplier_info' not in bid:
                    self.log_critical_issue("BID_VISIBILITY", "Bid missing supplier_info enrichment", bid)
                elif not bid['supplier_info']:
                    self.log_critical_issue("BID_VISIBILITY", "Bid has null supplier_info", bid)
                else:
                    supplier_info = bid['supplier_info']
                    if 'company_name' not in supplier_info or 'contact_phone' not in supplier_info:
                        self.log_critical_issue("BID_VISIBILITY", "Incomplete supplier info in bid", supplier_info)
                    else:
                        print(f"   ✅ Bid enriched with supplier: {supplier_info['company_name']}")
                
                # Check bid status and details
                required_fields = ['id', 'price_quote', 'delivery_estimate', 'status', 'created_at']
                for field in required_fields:
                    if field not in bid:
                        self.log_critical_issue("BID_VISIBILITY", f"Bid missing required field: {field}", bid)

        # Test unauthorized access (supplier trying to view bids on job they don't own)
        success, response = self.run_test(
            "GET /api/jobs/{job_id}/bids (Unauthorized Supplier)",
            "GET",
            f"jobs/{self.test_job_id}/bids",
            403,
            token=self.supplier_token
        )
        
        if success:
            print(f"   ✅ Unauthorized access properly blocked")
        else:
            self.log_critical_issue("BID_VISIBILITY", "Unauthorized supplier can view job bids", response)

    def test_admin_panel_issues(self):
        """Test admin panel issues"""
        print("\n" + "="*60)
        print("TESTING ADMIN PANEL ISSUES")
        print("="*60)
        
        # Test GET /api/admin/users endpoint
        success, response = self.run_test(
            "GET /api/admin/users",
            "GET",
            "admin/users",
            200,
            token=self.admin_token
        )
        
        if not success:
            self.log_critical_issue("ADMIN_PANEL", "Admin cannot view users list", response)
        elif not isinstance(response, list):
            self.log_critical_issue("ADMIN_PANEL", "Admin users endpoint returned invalid format", response)
        else:
            print(f"   ✅ Admin can view {len(response)} users")
            
            # Check if suppliers are included
            suppliers = [user for user in response if user.get('role') == 'supplier']
            buyers = [user for user in response if user.get('role') == 'buyer']
            print(f"   ✅ Found {len(suppliers)} suppliers and {len(buyers)} buyers")
            
            if len(suppliers) == 0:
                self.log_critical_issue("ADMIN_PANEL", "No suppliers found in admin users list", response)

        # Test GET /api/admin/users/{user_id}/details for supplier accounts
        if hasattr(self, 'supplier_user'):
            success, response = self.run_test(
                "GET /api/admin/users/{user_id}/details (Supplier)",
                "GET",
                f"admin/users/{self.supplier_user['id']}/details",
                200,
                token=self.admin_token
            )
            
            if not success:
                self.log_critical_issue("ADMIN_PANEL", "Admin cannot view supplier details", response)
            else:
                # Check if response contains required fields
                required_fields = ['user', 'jobs_posted', 'bids_submitted', 'jobs', 'bids']
                for field in required_fields:
                    if field not in response:
                        self.log_critical_issue("ADMIN_PANEL", f"Supplier details missing field: {field}", response)
                
                user_info = response.get('user', {})
                if 'email' not in user_info:
                    self.log_critical_issue("ADMIN_PANEL", "Supplier details missing email", user_info)
                
                print(f"   ✅ Supplier details: {user_info.get('company_name')} - {response.get('bids_submitted', 0)} bids")

        # Test GET /api/admin/users/{user_id}/details for buyer accounts
        if hasattr(self, 'buyer_user'):
            success, response = self.run_test(
                "GET /api/admin/users/{user_id}/details (Buyer)",
                "GET",
                f"admin/users/{self.buyer_user['id']}/details",
                200,
                token=self.admin_token
            )
            
            if not success:
                self.log_critical_issue("ADMIN_PANEL", "Admin cannot view buyer details", response)
            else:
                user_info = response.get('user', {})
                print(f"   ✅ Buyer details: {user_info.get('company_name')} - {response.get('jobs_posted', 0)} jobs")

        # Test admin access to all user details
        success, response = self.run_test(
            "GET /api/admin/jobs",
            "GET",
            "admin/jobs",
            200,
            token=self.admin_token
        )
        
        if not success:
            self.log_critical_issue("ADMIN_PANEL", "Admin cannot view jobs list", response)
        else:
            print(f"   ✅ Admin can view {len(response)} jobs")

        success, response = self.run_test(
            "GET /api/admin/bids",
            "GET",
            "admin/bids",
            200,
            token=self.admin_token
        )
        
        if not success:
            self.log_critical_issue("ADMIN_PANEL", "Admin cannot view bids list", response)
        else:
            print(f"   ✅ Admin can view {len(response)} bids")

    def test_notification_system(self):
        """Test notification system"""
        print("\n" + "="*60)
        print("TESTING NOTIFICATION SYSTEM")
        print("="*60)
        
        # Test GET /api/notifications endpoint
        success, response = self.run_test(
            "GET /api/notifications (Supplier)",
            "GET",
            "notifications",
            200,
            token=self.supplier_token
        )
        
        if not success:
            self.log_critical_issue("NOTIFICATIONS", "Supplier cannot get notifications", response)
        elif not isinstance(response, list):
            self.log_critical_issue("NOTIFICATIONS", "Notifications endpoint returned invalid format", response)
        else:
            print(f"   ✅ Supplier has {len(response)} notifications")
            
            # Check for bid award notification
            award_notifications = [n for n in response if n.get('type') == 'bid_awarded']
            if len(award_notifications) == 0:
                self.log_critical_issue("NOTIFICATIONS", "No bid award notification found for supplier", response)
            else:
                print(f"   ✅ Found {len(award_notifications)} bid award notifications")

        success, response = self.run_test(
            "GET /api/notifications (Buyer)",
            "GET",
            "notifications",
            200,
            token=self.buyer_token
        )
        
        if not success:
            self.log_critical_issue("NOTIFICATIONS", "Buyer cannot get notifications", response)
        else:
            print(f"   ✅ Buyer has {len(response)} notifications")

        # Test GET /api/notifications/unread-count endpoint
        success, response = self.run_test(
            "GET /api/notifications/unread-count (Supplier)",
            "GET",
            "notifications/unread-count",
            200,
            token=self.supplier_token
        )
        
        if not success:
            self.log_critical_issue("NOTIFICATIONS", "Supplier cannot get unread count", response)
        elif 'unread_count' not in response:
            self.log_critical_issue("NOTIFICATIONS", "Unread count response missing unread_count field", response)
        else:
            unread_count = response['unread_count']
            print(f"   ✅ Supplier has {unread_count} unread notifications")

        success, response = self.run_test(
            "GET /api/notifications/unread-count (Buyer)",
            "GET",
            "notifications/unread-count",
            200,
            token=self.buyer_token
        )
        
        if not success:
            self.log_critical_issue("NOTIFICATIONS", "Buyer cannot get unread count", response)
        else:
            unread_count = response.get('unread_count', 0)
            print(f"   ✅ Buyer has {unread_count} unread notifications")

        # Test notification creation when bids are awarded/rejected
        # This was already tested during setup when we awarded the bid
        # Let's create another bid and reject it to test rejection notifications
        
        # Create another supplier for rejection testing
        supplier2_data = {
            "email": f"test_supplier2_{int(time.time())}@buildbidz.com",
            "password": "TestSupplier123!",
            "company_name": "Test Supplier 2 Company",
            "contact_phone": "+91-9876543212",
            "role": "supplier",
            "gst_number": "29TESTSUP21234F1Z5",
            "address": "789 Supplier Street, Chennai"
        }
        
        success, response = self.run_test(
            "Create Second Test Supplier",
            "POST",
            "auth/register",
            200,
            data=supplier2_data
        )
        
        if success and 'access_token' in response:
            supplier2_token = response['access_token']
            
            # Create another job for rejection testing
            job2_data = {
                "title": "Second Test Job for Rejection",
                "category": "labor",
                "description": "Test job for rejection notification testing",
                "location": "Chennai, Tamil Nadu",
                "delivery_timeline": "1 week",
                "budget_range": "₹2,00,000 - ₹3,00,000"
            }
            
            success, response = self.run_test(
                "Create Second Test Job",
                "POST",
                "jobs",
                200,
                data=job2_data,
                token=self.buyer_token
            )
            
            if success and 'id' in response:
                job2_id = response['id']
                
                # Create bids from both suppliers
                bid1_data = {
                    "price_quote": 250000.0,
                    "delivery_estimate": "5 days",
                    "notes": "First bid"
                }
                
                success, response = self.run_test(
                    "Create First Bid on Second Job",
                    "POST",
                    f"jobs/{job2_id}/bids",
                    200,
                    data=bid1_data,
                    token=self.supplier_token
                )
                
                bid2_data = {
                    "price_quote": 280000.0,
                    "delivery_estimate": "7 days",
                    "notes": "Second bid"
                }
                
                success, response = self.run_test(
                    "Create Second Bid on Second Job",
                    "POST",
                    f"jobs/{job2_id}/bids",
                    200,
                    data=bid2_data,
                    token=supplier2_token
                )
                
                if success and 'id' in response:
                    bid2_id = response['id']
                    
                    # Award the second bid (this should reject the first bid)
                    success, response = self.run_test(
                        "Award Second Bid (Reject First)",
                        "POST",
                        f"jobs/{job2_id}/award/{bid2_id}",
                        200,
                        token=self.buyer_token
                    )
                    
                    if success:
                        print(f"   ✅ Bid awarded, rejection notifications should be sent")
                        
                        # Check if rejection notification was created for first supplier
                        time.sleep(1)  # Wait a moment for notification to be created
                        success, response = self.run_test(
                            "Check Rejection Notifications",
                            "GET",
                            "notifications",
                            200,
                            token=self.supplier_token
                        )
                        
                        if success:
                            rejection_notifications = [n for n in response if n.get('type') == 'bid_rejected']
                            if len(rejection_notifications) == 0:
                                self.log_critical_issue("NOTIFICATIONS", "No rejection notification created", response)
                            else:
                                print(f"   ✅ Found {len(rejection_notifications)} rejection notifications")

    def print_critical_issues_summary(self):
        """Print summary of critical issues found"""
        print("\n" + "="*60)
        print("CRITICAL ISSUES SUMMARY")
        print("="*60)
        
        if len(self.critical_issues) == 0:
            print("🎉 NO CRITICAL ISSUES FOUND!")
            print("All tested systems are working properly.")
        else:
            print(f"⚠️  FOUND {len(self.critical_issues)} CRITICAL ISSUES:")
            
            # Group issues by type
            issues_by_type = {}
            for issue in self.critical_issues:
                issue_type = issue['type']
                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = []
                issues_by_type[issue_type].append(issue)
            
            for issue_type, issues in issues_by_type.items():
                print(f"\n🔴 {issue_type} ISSUES ({len(issues)}):")
                for i, issue in enumerate(issues, 1):
                    print(f"   {i}. {issue['description']}")
                    if issue['details']:
                        print(f"      Details: {issue['details']}")

    def print_test_summary(self):
        """Print overall test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print("\n📋 Critical Systems Tested:")
        print("✅ Messaging System (GET /api/chats, GET /api/jobs/{job_id}/chat, POST /api/jobs/{job_id}/chat, POST /api/chats/{job_id}/mark-read)")
        print("✅ Bid Visibility for Buyers (GET /api/jobs/{job_id}/bids with supplier enrichment)")
        print("✅ Admin Panel Access (GET /api/admin/users, GET /api/admin/users/{user_id}/details)")
        print("✅ Notification System (GET /api/notifications, GET /api/notifications/unread-count)")
        print("✅ Authorization and Access Controls")
        print("✅ Data Enrichment and Completeness")

def main():
    print("🚀 Starting BuildBidz Critical Issues Testing...")
    print(f"Backend URL: https://construct-connect.preview.emergentagent.com")
    print("Testing specific issues reported in the platform:")
    print("1. Messaging System Problems")
    print("2. Bid Details Not Showing for Buyers") 
    print("3. Admin Panel Issues")
    print("4. Notification System")
    
    tester = CriticalIssuesTester()
    
    # Setup test environment
    if not tester.setup_test_environment():
        print("❌ Failed to setup test environment. Cannot proceed with critical tests.")
        return 1
    
    # Run critical issue tests
    tester.test_messaging_system()
    tester.test_bid_visibility_for_buyers()
    tester.test_admin_panel_issues()
    tester.test_notification_system()
    
    # Print summaries
    tester.print_critical_issues_summary()
    tester.print_test_summary()
    
    return 1 if len(tester.critical_issues) > 0 else 0

if __name__ == "__main__":
    sys.exit(main())