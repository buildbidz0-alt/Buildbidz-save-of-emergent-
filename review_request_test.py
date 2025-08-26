import requests
import sys
import json
from datetime import datetime
import time

class SpecificIssuesTester:
    def __init__(self, base_url="https://bb-visibilityfix.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.supplier_token = None
        self.buyer_user = None
        self.supplier_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.job_id = None
        self.bid_ids = []
        self.issues_found = []

    def log_issue(self, issue_type, description, details=None):
        """Log an issue found during testing"""
        self.issues_found.append({
            "type": issue_type,
            "description": description,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"🚨 ISSUE FOUND: {issue_type} - {description}")
        if details:
            print(f"   Details: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
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

    def specific_test_flow(self):
        """Execute the specific test flow mentioned in the review request"""
        print("\n" + "="*80)
        print("EXECUTING SPECIFIC TEST FLOW FROM REVIEW REQUEST")
        print("="*80)
        
        # Step 1: Setup Test Data - Login as buyer, create a job
        print("\n📋 STEP 1: Setup Test Data")
        print("-" * 40)
        
        # Create buyer account
        buyer_data = {
            "email": f"review_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Review Test Construction Co",
            "contact_phone": "+91-9876543210",
            "role": "buyer",
            "gst_number": "29REVIEW1234F1Z5",
            "address": "123 Review Test Street, Mumbai"
        }
        
        success, response = self.run_test(
            "Create Buyer Account",
            "POST",
            "auth/register",
            200,
            data=buyer_data
        )
        
        if success and 'access_token' in response:
            self.buyer_token = response['access_token']
            self.buyer_user = response['user']
            print(f"   ✅ Buyer created: {self.buyer_user['id']}")
        else:
            self.log_issue("SETUP_FAILURE", "Failed to create buyer account")
            return False
        
        # Create job
        job_data = {
            "title": "Review Test Construction Project - Chat & Bid Testing",
            "category": "material",
            "description": "This is a test job specifically created to investigate chat history and bid visibility issues reported in the review request.",
            "quantity": "500 bags cement, 200 tons steel",
            "location": "Mumbai, Maharashtra",
            "delivery_timeline": "4 weeks",
            "budget_range": "₹20,00,000 - ₹25,00,000"
        }
        
        success, job_response = self.run_test(
            "Create Test Job",
            "POST",
            "jobs",
            200,
            data=job_data,
            token=self.buyer_token
        )
        
        if success and job_response:
            self.job_id = job_response['id']
            print(f"   ✅ Job created: {self.job_id}")
            print(f"   Job title: {job_response['title']}")
        else:
            self.log_issue("SETUP_FAILURE", "Failed to create test job")
            return False
        
        # Step 2: Login as supplier, submit multiple bids on the job
        print("\n📋 STEP 2: Create Suppliers and Submit Bids")
        print("-" * 40)
        
        # Create multiple suppliers
        suppliers = []
        for i in range(3):
            supplier_data = {
                "email": f"review_supplier_{i}_{int(time.time())}@test.com",
                "password": "TestPass123!",
                "company_name": f"Review Test Supplier {i+1} Ltd",
                "contact_phone": f"+91-987654321{i}",
                "role": "supplier",
                "gst_number": f"29REVSUP{i}1234F1Z{i}",
                "address": f"45{i} Review Supplier Street, Delhi"
            }
            
            success, response = self.run_test(
                f"Create Supplier {i+1}",
                "POST",
                "auth/register",
                200,
                data=supplier_data
            )
            
            if success and 'access_token' in response:
                supplier_token = response['access_token']
                supplier_user = response['user']
                suppliers.append({
                    'token': supplier_token,
                    'user': supplier_user,
                    'index': i
                })
                print(f"   ✅ Supplier {i+1} created: {supplier_user['id']}")
                
                # Submit bid from this supplier
                bid_data = {
                    "price_quote": 2000000.0 + (i * 100000),  # Different prices
                    "delivery_estimate": f"{3 + i} weeks",
                    "notes": f"High quality materials from Supplier {i+1}. We have {10+i} years experience in construction supply."
                }
                
                success, bid_response = self.run_test(
                    f"Submit Bid from Supplier {i+1}",
                    "POST",
                    f"jobs/{self.job_id}/bids",
                    200,
                    data=bid_data,
                    token=supplier_token
                )
                
                if success and bid_response:
                    self.bid_ids.append(bid_response['id'])
                    print(f"   ✅ Bid {i+1} submitted: {bid_response['id']} (₹{bid_response['price_quote']:,.0f})")
                else:
                    self.log_issue("BID_SUBMISSION_FAILURE", f"Failed to submit bid from supplier {i+1}")
            else:
                self.log_issue("SETUP_FAILURE", f"Failed to create supplier {i+1}")
        
        # Store first supplier for later use
        if suppliers:
            self.supplier_token = suppliers[0]['token']
            self.supplier_user = suppliers[0]['user']
        
        # Step 3: Login as buyer again, attempt to retrieve bids
        print("\n📋 STEP 3: Test Bid Retrieval as Buyer")
        print("-" * 40)
        
        # Test GET /api/jobs/{job_id}/bids as the buyer
        success, buyer_bids = self.run_test(
            "Buyer Retrieve Job Bids",
            "GET",
            f"jobs/{self.job_id}/bids",
            200,
            token=self.buyer_token
        )
        
        if success:
            print(f"   ✅ Buyer can retrieve bids: {len(buyer_bids)} bids found")
            
            # Verify bid data completeness
            for i, bid in enumerate(buyer_bids):
                print(f"\n   📊 Analyzing Bid {i+1}:")
                
                # Check required fields
                required_fields = ['id', 'job_id', 'supplier_id', 'price_quote', 'delivery_estimate', 'status', 'created_at']
                missing_fields = []
                for field in required_fields:
                    if field not in bid:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_issue("BID_DATA_INCOMPLETE", f"Bid {i+1} missing fields: {missing_fields}")
                else:
                    print(f"     ✅ All required fields present")
                
                # Check supplier info enrichment
                if 'supplier_info' in bid:
                    supplier_info = bid['supplier_info']
                    required_supplier_fields = ['company_name', 'contact_phone']
                    missing_supplier_fields = []
                    
                    for field in required_supplier_fields:
                        if field not in supplier_info:
                            missing_supplier_fields.append(field)
                    
                    if missing_supplier_fields:
                        self.log_issue("SUPPLIER_INFO_INCOMPLETE", f"Bid {i+1} missing supplier fields: {missing_supplier_fields}")
                    else:
                        print(f"     ✅ Supplier info: {supplier_info['company_name']} - {supplier_info['contact_phone']}")
                else:
                    self.log_issue("SUPPLIER_INFO_MISSING", f"Bid {i+1} has no supplier_info enrichment")
                
                # Display bid details
                price = bid.get('price_quote')
                delivery = bid.get('delivery_estimate')
                status = bid.get('status')
                notes = bid.get('notes', '')
                
                print(f"     💰 Price: ₹{price:,.2f}" if price else "     ❌ No price")
                print(f"     📅 Delivery: {delivery}" if delivery else "     ❌ No delivery estimate")
                print(f"     📊 Status: {status}" if status else "     ❌ No status")
                print(f"     📝 Notes: {notes[:50]}..." if notes else "     📝 No notes")
        else:
            self.log_issue("BID_RETRIEVAL_FAILURE", "Buyer cannot retrieve bids for their job")
        
        # Test buyer dashboard stats
        success, buyer_stats = self.run_test(
            "Buyer Dashboard Stats",
            "GET",
            "dashboard/stats",
            200,
            token=self.buyer_token
        )
        
        if success:
            total_bids_received = buyer_stats.get('total_bids_received', 0)
            expected_bids = len(self.bid_ids)
            
            print(f"   📊 Dashboard shows {total_bids_received} total bids received")
            print(f"   📊 Expected: {expected_bids} bids")
            
            if total_bids_received != expected_bids:
                self.log_issue("DASHBOARD_STATS_INCORRECT", f"Dashboard shows {total_bids_received} bids but {expected_bids} were submitted")
            else:
                print("   ✅ Dashboard bid count is accurate")
        else:
            self.log_issue("DASHBOARD_STATS_FAILURE", "Cannot retrieve buyer dashboard stats")
        
        return True

    def test_chat_functionality(self):
        """Test chat functionality as specified in the review request"""
        print("\n📋 STEP 4: Chat Testing")
        print("-" * 40)
        
        if not self.job_id or not self.bid_ids:
            print("❌ Cannot test chat - no job or bids available")
            return
        
        # Award a bid to enable chat
        if self.bid_ids:
            success, award_response = self.run_test(
                "Award First Bid to Enable Chat",
                "POST",
                f"jobs/{self.job_id}/award/{self.bid_ids[0]}",
                200,
                token=self.buyer_token
            )
            
            if success:
                print("   ✅ Bid awarded - chat enabled")
            else:
                self.log_issue("BID_AWARD_FAILURE", "Cannot award bid to enable chat")
                return
        
        # Test initial chat state
        success, initial_chat = self.run_test(
            "Get Initial Chat Messages",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if success:
            print(f"   📨 Initial chat has {len(initial_chat)} messages")
        else:
            self.log_issue("CHAT_RETRIEVAL_FAILURE", "Cannot retrieve initial chat messages")
            return
        
        # Send messages back and forth
        messages_to_send = [
            {"sender": "buyer", "text": "Hello! Thank you for your excellent bid. When can you start the project?"},
            {"sender": "supplier", "text": "Hi! Thank you for selecting our bid. We can start within 3 days of contract signing."},
            {"sender": "buyer", "text": "That's great! Do you have all the materials ready? What about the steel quality certificates?"},
            {"sender": "supplier", "text": "Yes, all materials are in stock. We have ISI certified steel with all quality certificates ready."},
            {"sender": "buyer", "text": "Perfect! Let's schedule a meeting to finalize the contract details."}
        ]
        
        sent_messages = []
        for i, msg_info in enumerate(messages_to_send):
            sender_token = self.buyer_token if msg_info["sender"] == "buyer" else self.supplier_token
            sender_name = msg_info["sender"].title()
            
            message_data = {"message": msg_info["text"]}
            
            success, send_response = self.run_test(
                f"Send Message {i+1} ({sender_name})",
                "POST",
                f"jobs/{self.job_id}/chat",
                200,
                data=message_data,
                token=sender_token
            )
            
            if success:
                sent_messages.append(msg_info["text"])
                print(f"   ✅ {sender_name} message sent")
            else:
                self.log_issue("MESSAGE_SEND_FAILURE", f"Failed to send message {i+1} from {sender_name}")
        
        # Check if messages persist between API calls
        success, after_messages = self.run_test(
            "Check Messages After Sending",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if success:
            print(f"   📨 Chat now has {len(after_messages)} messages")
            
            # Verify all sent messages are present
            found_messages = 0
            for sent_msg in sent_messages:
                if any(sent_msg in msg['message'] for msg in after_messages):
                    found_messages += 1
            
            if found_messages == len(sent_messages):
                print("   ✅ All messages persist in chat history")
            else:
                self.log_issue("MESSAGE_PERSISTENCE_FAILURE", f"Only {found_messages}/{len(sent_messages)} messages found in chat history")
            
            # Test message history retrieval from supplier side
            success, supplier_view = self.run_test(
                "Supplier View Chat History",
                "GET",
                f"jobs/{self.job_id}/chat",
                200,
                token=self.supplier_token
            )
            
            if success:
                if len(supplier_view) == len(after_messages):
                    print("   ✅ Both parties see same chat history")
                else:
                    self.log_issue("CHAT_SYNC_FAILURE", f"Buyer sees {len(after_messages)} messages, supplier sees {len(supplier_view)}")
            else:
                self.log_issue("SUPPLIER_CHAT_ACCESS_FAILURE", "Supplier cannot access chat history")
        else:
            self.log_issue("CHAT_PERSISTENCE_CHECK_FAILURE", "Cannot retrieve messages after sending")
        
        # Test real-time message delivery (immediate retrieval)
        test_message = f"Real-time test message sent at {datetime.now().strftime('%H:%M:%S')}"
        message_data = {"message": test_message}
        
        # Send message and immediately check if it appears
        start_time = time.time()
        success, _ = self.run_test(
            "Send Real-time Test Message",
            "POST",
            f"jobs/{self.job_id}/chat",
            200,
            data=message_data,
            token=self.buyer_token
        )
        
        if success:
            success, immediate_check = self.run_test(
                "Immediate Message Check",
                "GET",
                f"jobs/{self.job_id}/chat",
                200,
                token=self.supplier_token
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if success:
                message_found = any(test_message in msg['message'] for msg in immediate_check)
                if message_found:
                    print(f"   ✅ Real-time delivery working (Response time: {response_time:.2f}s)")
                else:
                    self.log_issue("REAL_TIME_DELIVERY_FAILURE", "Message not immediately available after sending")
            else:
                self.log_issue("IMMEDIATE_CHECK_FAILURE", "Cannot check for immediate message delivery")

    def test_authorization_and_edge_cases(self):
        """Test authorization checks and edge cases"""
        print("\n📋 STEP 5: Authorization and Edge Cases")
        print("-" * 40)
        
        if not self.job_id:
            return
        
        # Test unauthorized bid viewing
        success, _ = self.run_test(
            "Supplier Try to View Other Job Bids (Should Fail)",
            "GET",
            f"jobs/{self.job_id}/bids",
            403,
            token=self.supplier_token
        )
        
        if success:
            print("   ✅ Authorization working - supplier blocked from viewing other job bids")
        else:
            self.log_issue("AUTHORIZATION_FAILURE", "Supplier can view bids for jobs they don't own")
        
        # Test data formatting and serialization
        if self.bid_ids:
            success, bid_data = self.run_test(
                "Check Bid Data Serialization",
                "GET",
                f"jobs/{self.job_id}/bids",
                200,
                token=self.buyer_token
            )
            
            if success and bid_data:
                # Check for common serialization issues
                for i, bid in enumerate(bid_data):
                    # Check for ObjectId serialization issues
                    for field, value in bid.items():
                        if isinstance(value, dict) and '$oid' in value:
                            self.log_issue("SERIALIZATION_ISSUE", f"Bid {i+1} field '{field}' contains unresolved ObjectId: {value}")
                        elif field == 'created_at' and not isinstance(value, str):
                            self.log_issue("DATE_SERIALIZATION_ISSUE", f"Bid {i+1} created_at not properly serialized: {value}")
                
                print("   ✅ Bid data serialization check completed")

    def print_detailed_summary(self):
        """Print detailed summary of findings"""
        print("\n" + "="*80)
        print("DETAILED TEST SUMMARY")
        print("="*80)
        
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.issues_found:
            print(f"\n🚨 ISSUES FOUND: {len(self.issues_found)}")
            print("-" * 40)
            for i, issue in enumerate(self.issues_found):
                print(f"{i+1}. {issue['type']}: {issue['description']}")
                if issue['details']:
                    print(f"   Details: {issue['details']}")
                print(f"   Time: {issue['timestamp']}")
                print()
        else:
            print("\n🎉 NO ISSUES FOUND!")
            print("✅ Chat History: Working correctly - messages persist and are retrievable")
            print("✅ Real-time Delivery: Working via REST API polling")
            print("✅ Bid Visibility: Buyers can see all bids with complete data")
            print("✅ Supplier Info: Properly enriched with company details")
            print("✅ Dashboard Stats: Accurate bid counts")
            print("✅ Authorization: Proper access controls in place")
            print("✅ Data Serialization: No ObjectId or formatting issues")
        
        print("\n📊 SPECIFIC AREAS TESTED:")
        print("🔍 Chat message persistence and retrieval")
        print("🔍 Real-time message delivery mechanism")
        print("🔍 Bid data retrieval and enrichment for buyers")
        print("🔍 Authorization checks for bid viewing")
        print("🔍 Data formatting and serialization")
        print("🔍 Dashboard statistics accuracy")
        print("🔍 Multi-user chat functionality")
        print("🔍 Cross-session data persistence")

def main():
    print("🚀 Starting BuildBidz Specific Issues Investigation...")
    print("🎯 Focus: Review Request Critical Issues")
    print("📋 Testing specific flow: Buyer creates job → Suppliers bid → Buyer views bids → Chat testing")
    print(f"Backend URL: https://bb-visibilityfix.preview.emergentagent.com")
    
    tester = SpecificIssuesTester()
    
    # Execute the specific test flow
    if tester.specific_test_flow():
        tester.test_chat_functionality()
        tester.test_authorization_and_edge_cases()
    else:
        print("❌ Test flow setup failed. Cannot continue with detailed testing.")
    
    # Print detailed summary
    tester.print_detailed_summary()
    
    return 0 if len(tester.issues_found) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())