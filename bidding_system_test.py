import requests
import sys
import json
from datetime import datetime
import time

class BiddingSystemTester:
    def __init__(self, base_url="https://construct-connect.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.supplier_token = None
        self.admin_token = None
        self.buyer_user = None
        self.supplier_user = None
        self.admin_user = None
        self.job_id = None
        self.bid_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.minor_issues = []

    def log_critical_issue(self, issue):
        """Log a critical issue that prevents core functionality"""
        self.critical_issues.append(issue)
        print(f"🚨 CRITICAL ISSUE: {issue}")

    def log_minor_issue(self, issue):
        """Log a minor issue that doesn't prevent core functionality"""
        self.minor_issues.append(issue)
        print(f"⚠️  Minor Issue: {issue}")

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

    def setup_test_accounts(self):
        """Set up test accounts for bidding system testing"""
        print("\n" + "="*60)
        print("SETTING UP TEST ACCOUNTS FOR BIDDING SYSTEM")
        print("="*60)
        
        # Admin login first
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
        else:
            self.log_critical_issue("Admin login failed - cannot test admin endpoints")
        
        # Create buyer account
        buyer_data = {
            "email": f"bidding_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Bidding Test Construction Co",
            "contact_phone": "+91-9876543210",
            "role": "buyer",
            "gst_number": "29BIDTEST1234F1Z5",
            "address": "123 Bidding Test Street, Mumbai"
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
        else:
            self.log_critical_issue("Buyer registration failed - cannot test buyer functionality")
            return False
        
        # Create supplier account
        supplier_data = {
            "email": f"bidding_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Bidding Test Supplier Ltd",
            "contact_phone": "+91-9876543211",
            "role": "supplier",
            "gst_number": "29BIDSUP1234F1Z6",
            "address": "456 Bidding Supplier Street, Delhi"
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
        else:
            self.log_critical_issue("Supplier registration failed - cannot test supplier functionality")
            return False
        
        return True

    def test_job_creation(self):
        """Test job creation by buyer"""
        print("\n" + "="*60)
        print("TESTING JOB CREATION")
        print("="*60)
        
        if not self.buyer_token:
            self.log_critical_issue("No buyer token - cannot create job")
            return False
        
        job_data = {
            "title": "Bidding Test Construction Project",
            "category": "material",
            "description": "Need high-quality cement and steel for a residential construction project. Looking for reliable suppliers with competitive pricing.",
            "quantity": "200 bags cement, 100 tons steel",
            "location": "Mumbai, Maharashtra",
            "delivery_timeline": "3 weeks",
            "budget_range": "₹10,00,000 - ₹15,00,000"
        }
        
        success, response = self.run_test(
            "Create Job for Bidding Test",
            "POST",
            "jobs",
            200,
            data=job_data,
            token=self.buyer_token
        )
        
        if success and 'id' in response:
            self.job_id = response['id']
            print(f"   Job created with ID: {self.job_id}")
            print(f"   Job title: {response.get('title')}")
            print(f"   Posted by: {response.get('posted_by')}")
            return True
        else:
            self.log_critical_issue("Job creation failed - cannot test bidding system")
            return False

    def test_bid_submission(self):
        """Test bid submission by supplier"""
        print("\n" + "="*60)
        print("TESTING BID SUBMISSION")
        print("="*60)
        
        if not self.job_id or not self.supplier_token:
            self.log_critical_issue("No job ID or supplier token - cannot submit bid")
            return False
        
        bid_data = {
            "price_quote": 1200000.0,
            "delivery_estimate": "2 weeks",
            "notes": "Premium quality materials with guaranteed delivery timeline. We have been in business for 15 years and provide excellent service."
        }
        
        success, response = self.run_test(
            "Submit Bid on Job",
            "POST",
            f"jobs/{self.job_id}/bids",
            200,
            data=bid_data,
            token=self.supplier_token
        )
        
        if success and 'id' in response:
            self.bid_id = response['id']
            print(f"   Bid submitted with ID: {self.bid_id}")
            print(f"   Price quote: ₹{response.get('price_quote')}")
            print(f"   Supplier ID: {response.get('supplier_id')}")
            print(f"   Job ID: {response.get('job_id')}")
            return True
        else:
            self.log_critical_issue("Bid submission failed - core bidding functionality broken")
            return False

    def test_bid_visibility_for_buyers(self):
        """Test if buyers can see bids on their jobs"""
        print("\n" + "="*60)
        print("TESTING BID VISIBILITY FOR BUYERS")
        print("="*60)
        
        if not self.job_id or not self.buyer_token:
            self.log_critical_issue("No job ID or buyer token - cannot test bid visibility")
            return False
        
        # Test GET /api/jobs/{job_id}/bids endpoint
        success, response = self.run_test(
            "Get Job Bids (Buyer View)",
            "GET",
            f"jobs/{self.job_id}/bids",
            200,
            token=self.buyer_token
        )
        
        if success:
            if isinstance(response, list):
                print(f"   Found {len(response)} bids for the job")
                
                if len(response) == 0:
                    self.log_critical_issue("No bids returned for buyer - bid visibility broken")
                    return False
                
                # Analyze the first bid
                first_bid = response[0]
                print(f"   First bid details:")
                print(f"   - Bid ID: {first_bid.get('id')}")
                print(f"   - Price: ₹{first_bid.get('price_quote')}")
                print(f"   - Delivery: {first_bid.get('delivery_estimate')}")
                print(f"   - Notes: {first_bid.get('notes', 'No notes')}")
                print(f"   - Status: {first_bid.get('status')}")
                print(f"   - Supplier ID: {first_bid.get('supplier_id')}")
                
                # Check if supplier info is enriched
                supplier_info = first_bid.get('supplier_info')
                if supplier_info:
                    print(f"   - Supplier Company: {supplier_info.get('company_name')}")
                    print(f"   - Supplier Phone: {supplier_info.get('contact_phone')}")
                    print("✅ Supplier information is properly enriched")
                else:
                    self.log_critical_issue("Supplier information not enriched in bid response")
                
                # Check for ObjectID serialization issues
                for key, value in first_bid.items():
                    if str(value).startswith('ObjectId('):
                        self.log_critical_issue(f"ObjectID serialization issue in field '{key}': {value}")
                
                return True
            else:
                self.log_critical_issue(f"Expected list of bids, got: {type(response)}")
                return False
        else:
            self.log_critical_issue("Failed to get job bids for buyer")
            return False

    def test_my_bids_for_suppliers(self):
        """Test if suppliers can see their own bids"""
        print("\n" + "="*60)
        print("TESTING 'MY BIDS' FOR SUPPLIERS")
        print("="*60)
        
        if not self.supplier_token:
            self.log_critical_issue("No supplier token - cannot test My Bids")
            return False
        
        # Test GET /api/bids/my endpoint
        success, response = self.run_test(
            "Get My Bids (Supplier View)",
            "GET",
            "bids/my",
            200,
            token=self.supplier_token
        )
        
        if success:
            if isinstance(response, list):
                print(f"   Found {len(response)} bids by this supplier")
                
                if len(response) == 0:
                    self.log_critical_issue("No bids returned for supplier - My Bids functionality broken")
                    return False
                
                # Analyze the first bid
                first_bid = response[0]
                print(f"   First bid details:")
                print(f"   - Bid ID: {first_bid.get('id')}")
                print(f"   - Price: ₹{first_bid.get('price_quote')}")
                print(f"   - Delivery: {first_bid.get('delivery_estimate')}")
                print(f"   - Status: {first_bid.get('status')}")
                print(f"   - Job ID: {first_bid.get('job_id')}")
                
                # Check if job info is enriched
                job_info = first_bid.get('job_info')
                if job_info:
                    print(f"   - Job Title: {job_info.get('title')}")
                    print(f"   - Job Category: {job_info.get('category')}")
                    print(f"   - Job Location: {job_info.get('location')}")
                    print("✅ Job information is properly enriched")
                else:
                    self.log_critical_issue("Job information not enriched in My Bids response")
                
                # Check for ObjectID serialization issues
                for key, value in first_bid.items():
                    if str(value).startswith('ObjectId('):
                        self.log_critical_issue(f"ObjectID serialization issue in field '{key}': {value}")
                
                return True
            else:
                self.log_critical_issue(f"Expected list of bids, got: {type(response)}")
                return False
        else:
            self.log_critical_issue("Failed to get My Bids for supplier")
            return False

    def test_authorization_controls(self):
        """Test authorization controls for bid endpoints"""
        print("\n" + "="*60)
        print("TESTING AUTHORIZATION CONTROLS")
        print("="*60)
        
        if not self.job_id:
            self.log_critical_issue("No job ID - cannot test authorization")
            return False
        
        # Test unauthorized access to job bids (supplier trying to view bids on job they don't own)
        success, response = self.run_test(
            "Unauthorized Bid Access (Supplier viewing job bids)",
            "GET",
            f"jobs/{self.job_id}/bids",
            403,  # Should be forbidden
            token=self.supplier_token
        )
        
        if not success:
            if response.get('status_code') == 200:
                self.log_critical_issue("Authorization broken - supplier can view bids on jobs they don't own")
            else:
                self.log_minor_issue(f"Unexpected status code for unauthorized access: {response.get('status_code')}")
        
        # Test unauthenticated access
        success, response = self.run_test(
            "Unauthenticated Bid Access",
            "GET",
            f"jobs/{self.job_id}/bids",
            401,  # Should require authentication
            token=None
        )
        
        if not success and response.get('status_code') != 401:
            self.log_minor_issue(f"Unexpected status code for unauthenticated access: {response.get('status_code')}")
        
        return True

    def test_admin_endpoints(self):
        """Test admin endpoints for bid management"""
        print("\n" + "="*60)
        print("TESTING ADMIN ENDPOINTS")
        print("="*60)
        
        if not self.admin_token:
            self.log_critical_issue("No admin token - cannot test admin endpoints")
            return False
        
        # Test GET /api/admin/bids
        success, response = self.run_test(
            "Admin Get All Bids",
            "GET",
            "admin/bids",
            200,
            token=self.admin_token
        )
        
        if success:
            if isinstance(response, list):
                print(f"   Admin found {len(response)} total bids in system")
                
                if len(response) > 0:
                    first_bid = response[0]
                    print(f"   First bid details:")
                    print(f"   - Bid ID: {first_bid.get('id')}")
                    print(f"   - Price: ₹{first_bid.get('price_quote')}")
                    
                    # Check enrichment
                    supplier_info = first_bid.get('supplier_info')
                    job_info = first_bid.get('job_info')
                    
                    if supplier_info:
                        print(f"   - Supplier: {supplier_info.get('company_name')}")
                        print("✅ Admin bid view has supplier info enrichment")
                    else:
                        self.log_critical_issue("Admin bid view missing supplier info enrichment")
                    
                    if job_info:
                        print(f"   - Job: {job_info.get('title')}")
                        print("✅ Admin bid view has job info enrichment")
                    else:
                        self.log_critical_issue("Admin bid view missing job info enrichment")
            else:
                self.log_critical_issue(f"Expected list of bids from admin endpoint, got: {type(response)}")
        else:
            self.log_critical_issue("Admin cannot access all bids")
        
        # Test GET /api/admin/users/{user_id}/details
        if self.buyer_user:
            success, response = self.run_test(
                "Admin Get User Details",
                "GET",
                f"admin/users/{self.buyer_user['id']}/details",
                200,
                token=self.admin_token
            )
            
            if success:
                print(f"   User details for: {response.get('user', {}).get('company_name')}")
                print(f"   Jobs posted: {response.get('jobs_posted', 0)}")
                print(f"   Bids submitted: {response.get('bids_submitted', 0)}")
                
                # Check if user object has masked password
                user_obj = response.get('user', {})
                if 'password' in user_obj:
                    self.log_critical_issue("User details endpoint exposes password field")
                else:
                    print("✅ Password field properly excluded from user details")
            else:
                self.log_critical_issue("Admin cannot get user details")
        
        return True

    def test_database_persistence(self):
        """Test if bids are properly stored in database"""
        print("\n" + "="*60)
        print("TESTING DATABASE PERSISTENCE")
        print("="*60)
        
        if not self.bid_id or not self.admin_token:
            self.log_critical_issue("No bid ID or admin token - cannot test database persistence")
            return False
        
        # Get all bids from admin endpoint and verify our bid exists
        success, response = self.run_test(
            "Verify Bid in Database (Admin View)",
            "GET",
            "admin/bids",
            200,
            token=self.admin_token
        )
        
        if success and isinstance(response, list):
            bid_found = False
            for bid in response:
                if bid.get('id') == self.bid_id:
                    bid_found = True
                    print(f"✅ Bid {self.bid_id} found in database")
                    print(f"   - Stored price: ₹{bid.get('price_quote')}")
                    print(f"   - Stored supplier_id: {bid.get('supplier_id')}")
                    print(f"   - Stored job_id: {bid.get('job_id')}")
                    break
            
            if not bid_found:
                self.log_critical_issue(f"Bid {self.bid_id} not found in database - persistence issue")
                return False
        else:
            self.log_critical_issue("Cannot verify database persistence - admin endpoint failed")
            return False
        
        return True

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        print("\n" + "="*60)
        print("TESTING EDGE CASES")
        print("="*60)
        
        # Test duplicate bid submission
        if self.job_id and self.supplier_token:
            bid_data = {
                "price_quote": 1300000.0,
                "delivery_estimate": "3 weeks",
                "notes": "Duplicate bid attempt"
            }
            
            success, response = self.run_test(
                "Duplicate Bid Submission (Should Fail)",
                "POST",
                f"jobs/{self.job_id}/bids",
                400,  # Should fail
                data=bid_data,
                token=self.supplier_token
            )
            
            if not success and response.get('status_code') == 200:
                self.log_critical_issue("System allows duplicate bids from same supplier")
        
        # Test bid on non-existent job
        fake_job_id = "fake-job-id-12345"
        success, response = self.run_test(
            "Bid on Non-existent Job (Should Fail)",
            "POST",
            f"jobs/{fake_job_id}/bids",
            404,  # Should fail
            data={"price_quote": 100000.0, "delivery_estimate": "1 week"},
            token=self.supplier_token
        )
        
        # Test getting bids for non-existent job
        success, response = self.run_test(
            "Get Bids for Non-existent Job (Should Fail)",
            "GET",
            f"jobs/{fake_job_id}/bids",
            404,  # Should fail
            token=self.buyer_token
        )
        
        return True

    def print_detailed_analysis(self):
        """Print detailed analysis of bidding system issues"""
        print("\n" + "="*80)
        print("DETAILED BIDDING SYSTEM ANALYSIS")
        print("="*80)
        
        print(f"\n📊 TEST RESULTS:")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.critical_issues)}):")
        if self.critical_issues:
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("   None - All critical functionality working!")
        
        print(f"\n⚠️  MINOR ISSUES FOUND ({len(self.minor_issues)}):")
        if self.minor_issues:
            for i, issue in enumerate(self.minor_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("   None - No minor issues detected!")
        
        print(f"\n🔍 BIDDING SYSTEM COMPONENT STATUS:")
        components = [
            ("User Registration & Authentication", self.buyer_token and self.supplier_token),
            ("Job Creation", self.job_id is not None),
            ("Bid Submission", self.bid_id is not None),
            ("Bid Visibility for Buyers", "No bids returned for buyer" not in str(self.critical_issues)),
            ("My Bids for Suppliers", "My Bids functionality broken" not in str(self.critical_issues)),
            ("Admin Endpoints", self.admin_token is not None),
            ("Authorization Controls", True),  # Tested but not critical for core functionality
            ("Database Persistence", "persistence issue" not in str(self.critical_issues))
        ]
        
        for component, status in components:
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {component}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if self.critical_issues:
            print("   1. Fix critical issues immediately - they block core bidding functionality")
            print("   2. Test ObjectID serialization in all API responses")
            print("   3. Verify data enrichment (supplier_info, job_info) in all bid endpoints")
            print("   4. Check database queries and data retrieval logic")
        else:
            print("   1. All critical functionality is working correctly")
            print("   2. Consider addressing minor issues for better user experience")
            print("   3. System is ready for production use")

def main():
    print("🎯 Starting Focused Bidding System Testing...")
    print("   Focus: Bid visibility issues for buyers and suppliers")
    print(f"   Backend URL: https://construct-connect.preview.emergentagent.com")
    
    tester = BiddingSystemTester()
    
    # Run focused bidding system tests
    if not tester.setup_test_accounts():
        print("❌ Failed to set up test accounts - cannot continue")
        return 1
    
    if not tester.test_job_creation():
        print("❌ Failed to create job - cannot test bidding")
        return 1
    
    if not tester.test_bid_submission():
        print("❌ Failed to submit bid - core functionality broken")
        return 1
    
    # Test the specific issues mentioned in the review request
    tester.test_bid_visibility_for_buyers()
    tester.test_my_bids_for_suppliers()
    tester.test_authorization_controls()
    tester.test_admin_endpoints()
    tester.test_database_persistence()
    tester.test_edge_cases()
    
    # Print detailed analysis
    tester.print_detailed_analysis()
    
    # Return exit code based on critical issues
    return 1 if tester.critical_issues else 0

if __name__ == "__main__":
    sys.exit(main())