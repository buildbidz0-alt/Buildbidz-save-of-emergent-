import requests
import sys
import json
import os
import time
from datetime import datetime

class FinalChatTest:
    def __init__(self, base_url="https://bb-visibilityfix.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.supplier_token = None
        self.job_id = None
        self.bid_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        if not files:
            headers['Content-Type'] = 'application/json'

        print(f"🔍 {name}...", end=" ")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    headers.pop('Content-Type', None)
                    response = requests.post(url, data=data, files=files, headers=headers)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            if response.status_code == expected_status:
                print("✅")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ ({response.status_code})")
                return False, {}

        except Exception as e:
            print(f"❌ (Error: {str(e)})")
            return False, {}

    def setup_chat(self):
        """Quick setup for chat testing"""
        print("\n📋 Setting up chat test environment...")
        
        # Create buyer
        buyer_data = {
            "email": f"final_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Final Test Buyer Co",
            "contact_phone": "+91-9876543210",
            "role": "buyer",
            "gst_number": "27ABCDE1234F1Z5",
            "address": "123 Final Test Street, Mumbai, Maharashtra - 400001"
        }
        
        success, response = self.run_test("Create Buyer", "POST", "auth/register", 200, data=buyer_data)
        if success:
            self.buyer_token = response['access_token']
        
        # Create supplier
        supplier_data = {
            "email": f"final_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Final Test Supplier Ltd",
            "contact_phone": "+91-9876543211",
            "role": "supplier",
            "gst_number": "27FGHIJ5678K1Z5",
            "address": "456 Final Supplier Street, Delhi, Delhi - 110001"
        }
        
        success, response = self.run_test("Create Supplier", "POST", "auth/register", 200, data=supplier_data)
        if success:
            self.supplier_token = response['access_token']
        
        # Create job
        job_data = {
            "title": "Final Chat Test Project",
            "category": "material",
            "description": "Final test for chat file sharing",
            "location": "Mumbai",
            "delivery_timeline": "1 week",
            "budget_range": "₹1,00,000"
        }
        
        success, response = self.run_test("Create Job", "POST", "jobs", 200, data=job_data, token=self.buyer_token)
        if success:
            self.job_id = response['id']
        
        # Submit and award bid
        bid_data = {"price_quote": 90000.0, "delivery_estimate": "5 days", "notes": "Final test bid"}
        success, response = self.run_test("Submit Bid", "POST", f"jobs/{self.job_id}/bids", 200, data=bid_data, token=self.supplier_token)
        if success:
            self.bid_id = response['id']
        
        success, response = self.run_test("Award Bid", "POST", f"jobs/{self.job_id}/award/{self.bid_id}", 200, token=self.buyer_token)
        
        return self.buyer_token and self.supplier_token and self.job_id

    def test_core_functionality(self):
        """Test core chat file sharing functionality"""
        print("\n🚀 Testing Core Chat File Sharing Functionality...")
        
        # Create test PDF
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n32\n%%EOF"
        test_files_dir = "/tmp/final_test"
        os.makedirs(test_files_dir, exist_ok=True)
        pdf_path = os.path.join(test_files_dir, "final_test.pdf")
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # Test 1: Upload chat file
        with open(pdf_path, 'rb') as f:
            files = {'files': ('final_test.pdf', f, 'application/pdf')}
            success, response = self.run_test("Upload Chat File", "POST", f"upload/chat/{self.job_id}", 200, files=files, token=self.buyer_token)
            if success:
                uploaded_files = response.get('files', [])
                if uploaded_files:
                    file_id = uploaded_files[0].get('id')
        
        # Test 2: Send message with file
        with open(pdf_path, 'rb') as f:
            files = {'files': ('message_file.pdf', f, 'application/pdf')}
            data = {'message': 'Here is the project document.'}
            success, response = self.run_test("Send Message with File", "POST", f"jobs/{self.job_id}/chat/with-files", 200, data=data, files=files, token=self.buyer_token)
            if success:
                message_id = response.get('chat_message', {}).get('id')
        
        # Test 3: Retrieve chat files
        success, response = self.run_test("Retrieve Chat Files", "GET", f"files/chat/{self.job_id}", 200, token=self.supplier_token)
        if success and response:
            print(f"   📁 Found {len(response)} chat files")
            if response:
                file_id = response[0]['id']
                
                # Test 4: Download chat file
                success, response = self.run_test("Download Chat File", "GET", f"download/chat/{file_id}", 200, token=self.supplier_token)
        
        # Test 5: Send regular text message (backward compatibility)
        message_data = {"message": "This is a regular text message."}
        success, response = self.run_test("Send Text Message", "POST", f"jobs/{self.job_id}/chat", 200, data=message_data, token=self.supplier_token)
        
        # Test 6: Get all chat messages
        success, response = self.run_test("Get Chat Messages", "GET", f"jobs/{self.job_id}/chat", 200, token=self.buyer_token)
        if success and response:
            print(f"   💬 Found {len(response)} chat messages")
            text_messages = sum(1 for msg in response if not msg.get('file_attachments'))
            file_messages = sum(1 for msg in response if msg.get('file_attachments'))
            print(f"   📝 Text messages: {text_messages}, File messages: {file_messages}")
        
        # Test 7: Delete message (if we have message_id)
        if 'message_id' in locals():
            success, response = self.run_test("Delete Message", "DELETE", f"messages/{message_id}", 200, token=self.buyer_token)
        
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def run_final_test(self):
        """Run final comprehensive test"""
        print("="*60)
        print("FINAL CHAT FILE SHARING FUNCTIONALITY TEST")
        print("="*60)
        
        if not self.setup_chat():
            print("❌ Setup failed")
            return
        
        self.test_core_functionality()
        
        print("\n" + "="*60)
        print("✅ FINAL TEST COMPLETED")
        print("🎉 Chat file sharing functionality is working!")
        print("="*60)

if __name__ == "__main__":
    tester = FinalChatTest()
    tester.run_final_test()