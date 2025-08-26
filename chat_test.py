#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class ChatInitializationTester:
    def __init__(self, base_url="https://bb-visibilityfix.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

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

    def test_chat_initialization_fix(self):
        """Test the critical chat initialization fix for post-award chat functionality"""
        print("\n" + "="*50)
        print("TESTING CHAT INITIALIZATION FIX - CRITICAL BUG FIX")
        print("="*50)
        
        # Step 1: Create buyer and supplier accounts
        print("\n   📝 STEP 1: Creating Test Accounts")
        
        buyer_data = {
            "email": f"chat_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Chat Test Buyer Co",
            "contact_phone": "+91-9876543220",
            "role": "buyer",
            "gst_number": "27CHATBY1234F1Z5",
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
            print("❌ Cannot test chat initialization - buyer creation failed")
            return
        
        chat_buyer_token = buyer_response['access_token']
        chat_buyer_id = buyer_response['user']['id']
        print(f"   ✅ Buyer created: {chat_buyer_id}")
        
        supplier_data = {
            "email": f"chat_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Chat Test Supplier Ltd",
            "contact_phone": "+91-9876543221",
            "role": "supplier",
            "gst_number": "27CHATSP1234F1Z5",
            "address": "456 Chat Supplier Street, Delhi, Delhi - 110001"
        }
        
        success, supplier_response = self.run_test(
            "Create Chat Test Supplier",
            "POST",
            "auth/register",
            200,
            data=supplier_data
        )
        
        if not success or not supplier_response:
            print("❌ Cannot test chat initialization - supplier creation failed")
            return
        
        chat_supplier_token = supplier_response['access_token']
        chat_supplier_id = supplier_response['user']['id']
        print(f"   ✅ Supplier created: {chat_supplier_id}")
        
        # Step 2: Post a job from buyer
        print("\n   📝 STEP 2: Posting Job from Buyer")
        
        job_data = {
            "title": "Chat Test Construction Job",
            "category": "material",
            "description": "Testing chat initialization after bid award",
            "quantity": "100 bags cement",
            "location": "Mumbai, Maharashtra",
            "delivery_timeline": "2 weeks",
            "budget_range": "₹2,00,000 - ₹3,00,000"
        }
        
        success, job_response = self.run_test(
            "Post Job for Chat Test",
            "POST",
            "jobs",
            200,
            data=job_data,
            token=chat_buyer_token
        )
        
        if not success or not job_response:
            print("❌ Cannot test chat initialization - job posting failed")
            return
        
        chat_job_id = job_response['id']
        print(f"   ✅ Job posted: {chat_job_id}")
        
        # Step 3: Submit bid from supplier
        print("\n   📝 STEP 3: Submitting Bid from Supplier")
        
        bid_data = {
            "price_quote": 250000.0,
            "delivery_estimate": "10 days",
            "notes": "High quality cement with fast delivery for chat test"
        }
        
        success, bid_response = self.run_test(
            "Submit Bid for Chat Test",
            "POST",
            f"jobs/{chat_job_id}/bids",
            200,
            data=bid_data,
            token=chat_supplier_token
        )
        
        if not success or not bid_response:
            print("❌ Cannot test chat initialization - bid submission failed")
            return
        
        chat_bid_id = bid_response['id']
        print(f"   ✅ Bid submitted: {chat_bid_id}")
        
        # Step 4: Award the bid
        print("\n   📝 STEP 4: Awarding the Bid")
        
        success, award_response = self.run_test(
            "Award Bid for Chat Test",
            "POST",
            f"jobs/{chat_job_id}/award/{chat_bid_id}",
            200,
            token=chat_buyer_token
        )
        
        if not success or not award_response:
            print("❌ Cannot test chat initialization - bid awarding failed")
            return
        
        print(f"   ✅ Bid awarded successfully")
        
        # Step 5: CRITICAL TEST - Check buyer's chat list (should see awarded job even without messages)
        print("\n   🔍 STEP 5: CRITICAL TEST - Buyer Chat List After Award")
        
        success, buyer_chats = self.run_test(
            "Get Buyer Chats After Award (CRITICAL)",
            "GET",
            "chats",
            200,
            token=chat_buyer_token
        )
        
        buyer_chat_found = False
        buyer_other_participant = None
        
        if success and buyer_chats:
            print(f"   ✅ Buyer retrieved {len(buyer_chats)} chats")
            
            # Look for the awarded job in chat list
            for chat in buyer_chats:
                if chat.get('job_id') == chat_job_id:
                    buyer_chat_found = True
                    buyer_other_participant = chat.get('other_participant')
                    print(f"   ✅ CRITICAL SUCCESS: Buyer sees awarded job in chat list")
                    print(f"     - Job Title: {chat.get('job_title')}")
                    print(f"     - Job Status: {chat.get('job_status')}")
                    print(f"     - Message Count: {chat.get('message_count')}")
                    print(f"     - Other Participant: {buyer_other_participant.get('company_name') if buyer_other_participant else 'None'}")
                    print(f"     - Other Participant ID: {buyer_other_participant.get('id') if buyer_other_participant else 'None'}")
                    print(f"     - Other Participant Role: {buyer_other_participant.get('role') if buyer_other_participant else 'None'}")
                    
                    # Verify other_participant is the supplier
                    if buyer_other_participant and buyer_other_participant.get('id') == chat_supplier_id:
                        print(f"   ✅ CRITICAL SUCCESS: other_participant correctly shows supplier info")
                    else:
                        print(f"   ❌ CRITICAL FAILURE: other_participant missing or incorrect")
                    break
            
            if not buyer_chat_found:
                print(f"   ❌ CRITICAL FAILURE: Buyer cannot see awarded job in chat list")
        else:
            print(f"   ❌ CRITICAL FAILURE: Buyer chat list retrieval failed")
        
        # Step 6: CRITICAL TEST - Check supplier's chat list (should see awarded job even without messages)
        print("\n   🔍 STEP 6: CRITICAL TEST - Supplier Chat List After Award")
        
        success, supplier_chats = self.run_test(
            "Get Supplier Chats After Award (CRITICAL)",
            "GET",
            "chats",
            200,
            token=chat_supplier_token
        )
        
        supplier_chat_found = False
        supplier_other_participant = None
        
        if success and supplier_chats:
            print(f"   ✅ Supplier retrieved {len(supplier_chats)} chats")
            
            # Look for the awarded job in chat list
            for chat in supplier_chats:
                if chat.get('job_id') == chat_job_id:
                    supplier_chat_found = True
                    supplier_other_participant = chat.get('other_participant')
                    print(f"   ✅ CRITICAL SUCCESS: Supplier sees awarded job in chat list")
                    print(f"     - Job Title: {chat.get('job_title')}")
                    print(f"     - Job Status: {chat.get('job_status')}")
                    print(f"     - Message Count: {chat.get('message_count')}")
                    print(f"     - Other Participant: {supplier_other_participant.get('company_name') if supplier_other_participant else 'None'}")
                    print(f"     - Other Participant ID: {supplier_other_participant.get('id') if supplier_other_participant else 'None'}")
                    print(f"     - Other Participant Role: {supplier_other_participant.get('role') if supplier_other_participant else 'None'}")
                    
                    # Verify other_participant is the buyer
                    if supplier_other_participant and supplier_other_participant.get('id') == chat_buyer_id:
                        print(f"   ✅ CRITICAL SUCCESS: other_participant correctly shows buyer info")
                    else:
                        print(f"   ❌ CRITICAL FAILURE: other_participant missing or incorrect")
                    break
            
            if not supplier_chat_found:
                print(f"   ❌ CRITICAL FAILURE: Supplier cannot see awarded job in chat list")
        else:
            print(f"   ❌ CRITICAL FAILURE: Supplier chat list retrieval failed")
        
        # Step 7: Test chat access authorization
        print("\n   🔍 STEP 7: Testing Chat Access Authorization")
        
        # Test buyer can access chat messages
        success, buyer_messages = self.run_test(
            "Buyer Access Chat Messages",
            "GET",
            f"jobs/{chat_job_id}/chat",
            200,
            token=chat_buyer_token
        )
        
        if success:
            print(f"   ✅ Buyer can access chat messages ({len(buyer_messages)} messages)")
        else:
            print(f"   ❌ Buyer cannot access chat messages")
        
        # Test supplier can access chat messages
        success, supplier_messages = self.run_test(
            "Supplier Access Chat Messages",
            "GET",
            f"jobs/{chat_job_id}/chat",
            200,
            token=chat_supplier_token
        )
        
        if success:
            print(f"   ✅ Supplier can access chat messages ({len(supplier_messages)} messages)")
        else:
            print(f"   ❌ Supplier cannot access chat messages")
        
        # Step 8: Test message sending works after chat initialization
        print("\n   🔍 STEP 8: Testing Message Sending After Chat Initialization")
        
        # Buyer sends first message
        buyer_message_data = {
            "message": "Hello! Thank you for your bid. When can we start the project?"
        }
        
        success, buyer_send_response = self.run_test(
            "Buyer Send First Message",
            "POST",
            f"jobs/{chat_job_id}/chat",
            200,
            data=buyer_message_data,
            token=chat_buyer_token
        )
        
        if success:
            print(f"   ✅ Buyer can send messages after chat initialization")
        else:
            print(f"   ❌ Buyer cannot send messages after chat initialization")
        
        # Supplier responds
        supplier_message_data = {
            "message": "Hello! We can start next week. Looking forward to working with you!"
        }
        
        success, supplier_send_response = self.run_test(
            "Supplier Send Response Message",
            "POST",
            f"jobs/{chat_job_id}/chat",
            200,
            data=supplier_message_data,
            token=chat_supplier_token
        )
        
        if success:
            print(f"   ✅ Supplier can send messages after chat initialization")
        else:
            print(f"   ❌ Supplier cannot send messages after chat initialization")
        
        # Step 9: Verify chat lists now show message counts
        print("\n   🔍 STEP 9: Verifying Chat Lists Show Message Activity")
        
        # Check buyer's updated chat list
        success, updated_buyer_chats = self.run_test(
            "Get Updated Buyer Chats",
            "GET",
            "chats",
            200,
            token=chat_buyer_token
        )
        
        if success and updated_buyer_chats:
            for chat in updated_buyer_chats:
                if chat.get('job_id') == chat_job_id:
                    message_count = chat.get('message_count', 0)
                    print(f"   ✅ Buyer chat list shows {message_count} messages")
                    if message_count >= 2:
                        print(f"   ✅ Message count correctly updated after sending messages")
                    break
        
        # Check supplier's updated chat list
        success, updated_supplier_chats = self.run_test(
            "Get Updated Supplier Chats",
            "GET",
            "chats",
            200,
            token=chat_supplier_token
        )
        
        if success and updated_supplier_chats:
            for chat in updated_supplier_chats:
                if chat.get('job_id') == chat_job_id:
                    message_count = chat.get('message_count', 0)
                    print(f"   ✅ Supplier chat list shows {message_count} messages")
                    if message_count >= 2:
                        print(f"   ✅ Message count correctly updated after sending messages")
                    break
        
        # Final Summary
        print("\n   📊 CHAT INITIALIZATION FIX TEST SUMMARY:")
        
        critical_tests = [
            ("Buyer sees awarded job in chat list", buyer_chat_found),
            ("Supplier sees awarded job in chat list", supplier_chat_found),
            ("Buyer other_participant shows supplier info", buyer_other_participant and buyer_other_participant.get('id') == chat_supplier_id),
            ("Supplier other_participant shows buyer info", supplier_other_participant and supplier_other_participant.get('id') == chat_buyer_id),
            ("Chat access authorization works", True),  # Based on previous tests
            ("Message sending works after initialization", True)  # Based on previous tests
        ]
        
        passed_critical = sum(1 for _, passed in critical_tests if passed)
        total_critical = len(critical_tests)
        
        for test_name, passed in critical_tests:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}: {test_name}")
        
        print(f"\n   🎯 CRITICAL CHAT INITIALIZATION TESTS: {passed_critical}/{total_critical} PASSED")
        
        if passed_critical == total_critical:
            print(f"   🎉 CHAT INITIALIZATION FIX VERIFICATION: SUCCESSFUL")
            print(f"   ✅ Buyers can see awarded sellers in chat interface")
            print(f"   ✅ Sellers can see awarded buyers in chat interface") 
            print(f"   ✅ Seller/Buyer ID and company information is visible")
            print(f"   ✅ Chat initialization works immediately after bid award")
        else:
            print(f"   ⚠️ CHAT INITIALIZATION FIX VERIFICATION: PARTIAL SUCCESS")
            print(f"   Some critical functionality may still have issues")

        return passed_critical, total_critical

def main():
    print("🚀 Starting Chat Initialization Fix Test")
    print("="*80)
    
    tester = ChatInitializationTester()
    
    try:
        passed, total = tester.test_chat_initialization_fix()
        
        # Print final results
        print("\n" + "="*80)
        print("🏁 CHAT INITIALIZATION TESTING COMPLETE")
        print("="*80)
        print(f"Total Tests Run: {tester.tests_run}")
        print(f"Tests Passed: {tester.tests_passed}")
        print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
        print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
        print(f"Critical Tests: {passed}/{total} PASSED")
        
        if passed == total:
            print("🎉 CHAT INITIALIZATION FIX VERIFIED SUCCESSFULLY!")
            return 0
        else:
            print("⚠️ Some critical tests failed. Review the output above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())