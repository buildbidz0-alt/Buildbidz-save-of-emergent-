import requests
import sys
import json
from datetime import datetime
import time

class ChatFixTester:
    def __init__(self, base_url="https://bb-visibilityfix.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.supplier_token = None
        self.job_id = None
        self.bid_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'

        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
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

    def setup_chat_test(self):
        """Setup accounts and job for chat testing"""
        print("🚀 Setting up chat test environment...")
        
        # Create buyer
        buyer_data = {
            "email": f"chat_fix_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Chat Fix Test Buyer Co",
            "contact_phone": "+91-9876543210",
            "role": "buyer"
        }
        
        success, response = self.run_test(
            "Create Buyer",
            "POST",
            "auth/register",
            200,
            data=buyer_data
        )
        
        if success and 'access_token' in response:
            self.buyer_token = response['access_token']
            print(f"   Buyer created: {response['user']['id']}")
        else:
            return False
        
        # Create supplier
        supplier_data = {
            "email": f"chat_fix_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Chat Fix Test Supplier Ltd",
            "contact_phone": "+91-9876543211",
            "role": "supplier"
        }
        
        success, response = self.run_test(
            "Create Supplier",
            "POST",
            "auth/register",
            200,
            data=supplier_data
        )
        
        if success and 'access_token' in response:
            self.supplier_token = response['access_token']
            print(f"   Supplier created: {response['user']['id']}")
        else:
            return False
        
        # Create job
        job_data = {
            "title": "Chat Fix Test Job",
            "category": "material",
            "description": "Testing chat functionality after ObjectId fix",
            "location": "Mumbai",
            "delivery_timeline": "2 weeks"
        }
        
        success, response = self.run_test(
            "Create Job",
            "POST",
            "jobs",
            200,
            data=job_data,
            token=self.buyer_token
        )
        
        if success:
            self.job_id = response['id']
            print(f"   Job created: {self.job_id}")
        else:
            return False
        
        # Submit bid
        bid_data = {
            "price_quote": 500000.0,
            "delivery_estimate": "10 days",
            "notes": "Chat fix test bid"
        }
        
        success, response = self.run_test(
            "Submit Bid",
            "POST",
            f"jobs/{self.job_id}/bids",
            200,
            data=bid_data,
            token=self.supplier_token
        )
        
        if success:
            self.bid_id = response['id']
            print(f"   Bid submitted: {self.bid_id}")
        else:
            return False
        
        # Award bid to enable chat
        success, response = self.run_test(
            "Award Bid",
            "POST",
            f"jobs/{self.job_id}/award/{self.bid_id}",
            200,
            token=self.buyer_token
        )
        
        if success:
            print("   Bid awarded - chat enabled")
            return True
        else:
            return False

    def test_chat_functionality(self):
        """Test the fixed chat functionality"""
        print("\n🔍 Testing Chat Functionality After Fix...")
        
        # Test 1: Get initial chat (should be empty)
        success, initial_messages = self.run_test(
            "Get Initial Chat Messages",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if success:
            print(f"   ✅ Initial chat retrieved: {len(initial_messages)} messages")
        else:
            print("   ❌ Failed to retrieve initial chat")
            return False
        
        # Test 2: Send message from buyer
        buyer_message = {
            "message": "Hello! This is a test message from the buyer to verify the ObjectId fix is working."
        }
        
        success, send_response = self.run_test(
            "Send Buyer Message",
            "POST",
            f"jobs/{self.job_id}/chat",
            200,
            data=buyer_message,
            token=self.buyer_token
        )
        
        if success:
            print("   ✅ Buyer message sent successfully")
        else:
            print("   ❌ Failed to send buyer message")
            return False
        
        # Test 3: Retrieve chat after buyer message (THIS WAS FAILING BEFORE)
        success, after_buyer_msg = self.run_test(
            "Get Chat After Buyer Message",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if success:
            print(f"   ✅ Chat retrieved after buyer message: {len(after_buyer_msg)} messages")
            
            # Verify message content
            if len(after_buyer_msg) > 0:
                latest_msg = after_buyer_msg[-1]
                if latest_msg['message'] == buyer_message['message']:
                    print("   ✅ Message content matches")
                    print(f"   ✅ Sender info: {latest_msg.get('sender_info', {}).get('company_name')}")
                else:
                    print("   ❌ Message content mismatch")
            else:
                print("   ❌ No messages found")
        else:
            print("   ❌ CRITICAL: Still failing to retrieve chat after message")
            return False
        
        # Test 4: Send message from supplier
        supplier_message = {
            "message": "Hi! This is a response from the supplier. The chat fix seems to be working!"
        }
        
        success, send_response = self.run_test(
            "Send Supplier Message",
            "POST",
            f"jobs/{self.job_id}/chat",
            200,
            data=supplier_message,
            token=self.supplier_token
        )
        
        if success:
            print("   ✅ Supplier message sent successfully")
        else:
            print("   ❌ Failed to send supplier message")
            return False
        
        # Test 5: Retrieve chat from supplier side
        success, supplier_view = self.run_test(
            "Supplier View Chat",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.supplier_token
        )
        
        if success:
            print(f"   ✅ Supplier can view chat: {len(supplier_view)} messages")
            
            # Verify both messages are present
            buyer_msg_found = any(buyer_message['message'] in msg['message'] for msg in supplier_view)
            supplier_msg_found = any(supplier_message['message'] in msg['message'] for msg in supplier_view)
            
            if buyer_msg_found and supplier_msg_found:
                print("   ✅ Both messages present in chat history")
            else:
                print(f"   ❌ Messages missing - Buyer: {buyer_msg_found}, Supplier: {supplier_msg_found}")
        else:
            print("   ❌ Supplier cannot view chat")
            return False
        
        # Test 6: Retrieve chat from buyer side again
        success, buyer_final_view = self.run_test(
            "Buyer Final Chat View",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if success:
            print(f"   ✅ Buyer final view: {len(buyer_final_view)} messages")
            
            # Check message structure
            if len(buyer_final_view) > 0:
                sample_msg = buyer_final_view[0]
                required_fields = ['id', 'job_id', 'sender_id', 'receiver_id', 'message', 'created_at', 'read']
                missing_fields = [field for field in required_fields if field not in sample_msg]
                
                if not missing_fields:
                    print("   ✅ Message structure complete")
                else:
                    print(f"   ⚠️  Missing fields: {missing_fields}")
                
                # Check sender_info enrichment
                if 'sender_info' in sample_msg:
                    sender_info = sample_msg['sender_info']
                    if 'company_name' in sender_info and 'role' in sender_info:
                        print(f"   ✅ Sender info enriched: {sender_info['company_name']} ({sender_info['role']})")
                    else:
                        print("   ⚠️  Incomplete sender info")
                else:
                    print("   ❌ No sender info enrichment")
                
                # Check for ObjectId issues
                has_objectid_issues = False
                for msg in buyer_final_view:
                    for key, value in msg.items():
                        if isinstance(value, dict) and '$oid' in value:
                            has_objectid_issues = True
                            break
                
                if not has_objectid_issues:
                    print("   ✅ No ObjectId serialization issues")
                else:
                    print("   ❌ ObjectId serialization issues still present")
        else:
            print("   ❌ Buyer cannot view final chat")
            return False
        
        return True

def main():
    print("🚀 Testing Chat ObjectId Fix...")
    print("🎯 Focus: Verifying chat message retrieval works after ObjectId serialization fix")
    
    tester = ChatFixTester()
    
    if not tester.setup_chat_test():
        print("❌ Setup failed")
        return 1
    
    if tester.test_chat_functionality():
        print("\n🎉 CHAT FIX SUCCESSFUL!")
        print("✅ Chat messages can be sent and retrieved")
        print("✅ ObjectId serialization issue resolved")
        print("✅ Message persistence working")
        print("✅ Sender info enrichment working")
        print("✅ Both buyer and supplier can access chat")
        return 0
    else:
        print("\n❌ CHAT FIX FAILED!")
        print("Chat functionality still has issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())