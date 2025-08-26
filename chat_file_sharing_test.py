import requests
import sys
import json
import os
import time
from datetime import datetime
from pathlib import Path

class ChatFileSharingTester:
    def __init__(self, base_url="https://bb-visibilityfix.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.supplier_token = None
        self.admin_token = None
        self.buyer_user = None
        self.supplier_user = None
        self.admin_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.job_id = None
        self.bid_id = None
        self.chat_files = []
        self.chat_messages = []

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        # Don't set Content-Type for multipart/form-data requests
        if not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    # For file uploads, don't set Content-Type header
                    headers.pop('Content-Type', None)
                    response = requests.post(url, data=data, files=files, headers=headers)
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

    def create_test_file(self, filename, content, file_type="text"):
        """Create a test file for upload"""
        test_files_dir = "/tmp/test_files"
        os.makedirs(test_files_dir, exist_ok=True)
        
        file_path = os.path.join(test_files_dir, filename)
        
        if file_type == "text":
            with open(file_path, 'w') as f:
                f.write(content)
        elif file_type == "binary":
            with open(file_path, 'wb') as f:
                f.write(content)
        
        return file_path

    def setup_test_accounts(self):
        """Create test buyer and supplier accounts"""
        print("\n" + "="*60)
        print("SETTING UP TEST ACCOUNTS FOR CHAT FILE SHARING")
        print("="*60)
        
        # Create buyer account
        buyer_data = {
            "email": f"chat_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Chat Test Construction Co",
            "contact_phone": "+91-9876543210",
            "role": "buyer",
            "gst_number": "27ABCDE1234F1Z5",
            "address": "123 Chat Test Street, Mumbai, Maharashtra - 400001"
        }
        
        success, response = self.run_test(
            "Create Chat Test Buyer",
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
            print("❌ Failed to create buyer account")
            return False
        
        # Create supplier account
        supplier_data = {
            "email": f"chat_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Chat Test Supplier Ltd",
            "contact_phone": "+91-9876543211",
            "role": "supplier",
            "gst_number": "29CHATSUP1234F1Z5",
            "address": "456 Chat Supplier Street, Delhi, Delhi - 110001"
        }
        
        success, response = self.run_test(
            "Create Chat Test Supplier",
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
            print("❌ Failed to create supplier account")
            return False
        
        # Login admin
        admin_login = {
            "email": "mohammadjalaluddin1027@gmail.com",
            "password": "5968474644j"
        }
        
        success, response = self.run_test(
            "Admin Login for Chat Testing",
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
            print("❌ Failed to login admin")
            return False
        
        return True

    def establish_chat_eligibility(self):
        """Create job, bid, and award to establish chat eligibility"""
        print("\n" + "="*60)
        print("ESTABLISHING CHAT ELIGIBILITY (JOB -> BID -> AWARD)")
        print("="*60)
        
        # Create job
        job_data = {
            "title": "Chat File Sharing Test Project",
            "category": "material",
            "description": "Test project for chat file sharing functionality",
            "quantity": "100 units",
            "location": "Mumbai, Maharashtra",
            "delivery_timeline": "2 weeks",
            "budget_range": "₹5,00,000 - ₹7,00,000"
        }
        
        success, response = self.run_test(
            "Create Test Job for Chat",
            "POST",
            "jobs",
            200,
            data=job_data,
            token=self.buyer_token
        )
        
        if success and response:
            self.job_id = response['id']
            print(f"   Job created with ID: {self.job_id}")
        else:
            print("❌ Failed to create job")
            return False
        
        # Submit bid
        bid_data = {
            "price_quote": 600000.0,
            "delivery_estimate": "10 days",
            "notes": "High quality materials for chat file sharing test"
        }
        
        success, response = self.run_test(
            "Submit Test Bid",
            "POST",
            f"jobs/{self.job_id}/bids",
            200,
            data=bid_data,
            token=self.supplier_token
        )
        
        if success and response:
            self.bid_id = response['id']
            print(f"   Bid submitted with ID: {self.bid_id}")
        else:
            print("❌ Failed to submit bid")
            return False
        
        # Award bid to establish chat
        success, response = self.run_test(
            "Award Bid to Establish Chat",
            "POST",
            f"jobs/{self.job_id}/award/{self.bid_id}",
            200,
            token=self.buyer_token
        )
        
        if success:
            print("   ✅ Bid awarded - Chat eligibility established")
            return True
        else:
            print("❌ Failed to award bid")
            return False

    def test_chat_file_upload_endpoint(self):
        """Test POST /api/upload/chat/{job_id} endpoint"""
        print("\n" + "="*60)
        print("TESTING CHAT FILE UPLOAD ENDPOINT")
        print("="*60)
        
        if not self.job_id:
            print("❌ Cannot test file upload - no job ID")
            return
        
        # Test 1: Upload valid PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        pdf_path = self.create_test_file("test_document.pdf", pdf_content, "binary")
        
        with open(pdf_path, 'rb') as f:
            files = {'files': ('test_document.pdf', f, 'application/pdf')}
            success, response = self.run_test(
                "Upload Valid PDF File",
                "POST",
                f"upload/chat/{self.job_id}",
                200,
                files=files,
                token=self.buyer_token
            )
            
            if success and response:
                uploaded_files = response.get('files', [])
                if uploaded_files:
                    self.chat_files.extend(uploaded_files)
                    print(f"   ✅ PDF uploaded: {uploaded_files[0]['filename']}")
        
        # Test 2: Upload valid JPG file
        # Create a minimal JPG file (just header)
        jpg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        jpg_path = self.create_test_file("test_image.jpg", jpg_content, "binary")
        
        with open(jpg_path, 'rb') as f:
            files = {'files': ('test_image.jpg', f, 'image/jpeg')}
            success, response = self.run_test(
                "Upload Valid JPG File",
                "POST",
                f"upload/chat/{self.job_id}",
                200,
                files=files,
                token=self.supplier_token
            )
            
            if success and response:
                uploaded_files = response.get('files', [])
                if uploaded_files:
                    self.chat_files.extend(uploaded_files)
                    print(f"   ✅ JPG uploaded: {uploaded_files[0]['filename']}")
        
        # Test 3: Try uploading invalid file type (should fail)
        txt_path = self.create_test_file("invalid.txt", "This should not be allowed")
        
        with open(txt_path, 'rb') as f:
            files = {'files': ('invalid.txt', f, 'text/plain')}
            success, response = self.run_test(
                "Upload Invalid File Type (Should Fail)",
                "POST",
                f"upload/chat/{self.job_id}",
                415,  # Unsupported Media Type
                files=files,
                token=self.buyer_token
            )
        
        # Test 4: Try uploading file >10MB (should fail)
        large_content = b'A' * (11 * 1024 * 1024)  # 11MB
        large_path = self.create_test_file("large_file.pdf", large_content, "binary")
        
        with open(large_path, 'rb') as f:
            files = {'files': ('large_file.pdf', f, 'application/pdf')}
            success, response = self.run_test(
                "Upload Large File >10MB (Should Fail)",
                "POST",
                f"upload/chat/{self.job_id}",
                413,  # Payload Too Large
                files=files,
                token=self.buyer_token
            )
        
        # Test 5: Unauthorized user trying to upload (should fail)
        with open(pdf_path, 'rb') as f:
            files = {'files': ('unauthorized.pdf', f, 'application/pdf')}
            success, response = self.run_test(
                "Unauthorized Upload (Should Fail)",
                "POST",
                f"upload/chat/{self.job_id}",
                403,  # Forbidden
                files=files,
                token=None  # No token
            )
        
        # Clean up test files
        for path in [pdf_path, jpg_path, txt_path, large_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_enhanced_message_sending(self):
        """Test POST /api/jobs/{job_id}/chat/with-files endpoint"""
        print("\n" + "="*60)
        print("TESTING ENHANCED MESSAGE SENDING WITH FILES")
        print("="*60)
        
        if not self.job_id:
            print("❌ Cannot test message sending - no job ID")
            return
        
        # Test 1: Send message with file attachments
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        pdf_path = self.create_test_file("message_attachment.pdf", pdf_content, "binary")
        
        with open(pdf_path, 'rb') as f:
            files = {'files': ('message_attachment.pdf', f, 'application/pdf')}
            data = {'message': 'Here is the project specification document.'}
            
            success, response = self.run_test(
                "Send Message with File Attachment",
                "POST",
                f"jobs/{self.job_id}/chat/with-files",
                200,
                data=data,
                files=files,
                token=self.buyer_token
            )
            
            if success and response:
                chat_message = response.get('chat_message', {})
                files_uploaded = response.get('files_uploaded', 0)
                print(f"   ✅ Message sent with {files_uploaded} file(s)")
                if chat_message:
                    self.chat_messages.append(chat_message)
        
        # Test 2: Send text-only message using with-files endpoint
        data = {'message': 'This is a text-only message using the with-files endpoint.'}
        
        success, response = self.run_test(
            "Send Text-Only Message via With-Files Endpoint",
            "POST",
            f"jobs/{self.job_id}/chat/with-files",
            200,
            data=data,
            token=self.supplier_token
        )
        
        if success and response:
            chat_message = response.get('chat_message', {})
            files_uploaded = response.get('files_uploaded', 0)
            print(f"   ✅ Text message sent with {files_uploaded} file(s)")
            if chat_message:
                self.chat_messages.append(chat_message)
        
        # Test 3: Send message with multiple files
        jpg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        jpg_path = self.create_test_file("multiple_file1.jpg", jpg_content, "binary")
        pdf_path2 = self.create_test_file("multiple_file2.pdf", pdf_content, "binary")
        
        with open(jpg_path, 'rb') as f1, open(pdf_path2, 'rb') as f2:
            files = [
                ('files', ('multiple_file1.jpg', f1, 'image/jpeg')),
                ('files', ('multiple_file2.pdf', f2, 'application/pdf'))
            ]
            data = {'message': 'Here are multiple attachments for the project.'}
            
            success, response = self.run_test(
                "Send Message with Multiple Files",
                "POST",
                f"jobs/{self.job_id}/chat/with-files",
                200,
                data=data,
                files=files,
                token=self.supplier_token
            )
            
            if success and response:
                files_uploaded = response.get('files_uploaded', 0)
                print(f"   ✅ Message sent with {files_uploaded} multiple files")
        
        # Test 4: Unauthorized user trying to send message (should fail)
        data = {'message': 'Unauthorized message attempt'}
        
        success, response = self.run_test(
            "Unauthorized Message Send (Should Fail)",
            "POST",
            f"jobs/{self.job_id}/chat/with-files",
            403,
            data=data,
            token=None
        )
        
        # Clean up test files
        for path in [pdf_path, jpg_path, pdf_path2]:
            if os.path.exists(path):
                os.remove(path)

    def test_chat_file_retrieval(self):
        """Test GET /api/files/chat/{job_id} endpoint"""
        print("\n" + "="*60)
        print("TESTING CHAT FILE RETRIEVAL")
        print("="*60)
        
        if not self.job_id:
            print("❌ Cannot test file retrieval - no job ID")
            return
        
        # Test 1: Buyer retrieving chat files
        success, response = self.run_test(
            "Buyer Retrieve Chat Files",
            "GET",
            f"files/chat/{self.job_id}",
            200,
            token=self.buyer_token
        )
        
        if success and response:
            print(f"   ✅ Buyer retrieved {len(response)} chat files")
            for file_info in response[:3]:  # Show first 3 files
                print(f"     - {file_info['filename']} ({file_info['size']} bytes)")
        
        # Test 2: Supplier retrieving chat files
        success, response = self.run_test(
            "Supplier Retrieve Chat Files",
            "GET",
            f"files/chat/{self.job_id}",
            200,
            token=self.supplier_token
        )
        
        if success and response:
            print(f"   ✅ Supplier retrieved {len(response)} chat files")
        
        # Test 3: Admin retrieving chat files
        success, response = self.run_test(
            "Admin Retrieve Chat Files",
            "GET",
            f"files/chat/{self.job_id}",
            200,
            token=self.admin_token
        )
        
        if success and response:
            print(f"   ✅ Admin retrieved {len(response)} chat files")
        
        # Test 4: Unauthorized user trying to retrieve files (should fail)
        success, response = self.run_test(
            "Unauthorized File Retrieval (Should Fail)",
            "GET",
            f"files/chat/{self.job_id}",
            401,  # Unauthorized
            token=None
        )
        
        # Test 5: Non-participant trying to retrieve files (should fail)
        # Create another supplier who hasn't bid on this job
        other_supplier_data = {
            "email": f"other_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Other Supplier Co",
            "contact_phone": "+91-9876543212",
            "role": "supplier",
            "gst_number": "29OTHER1234F1Z5",
            "address": "789 Other Street, Bangalore, Karnataka - 560001"
        }
        
        success, reg_response = self.run_test(
            "Create Other Supplier for Authorization Test",
            "POST",
            "auth/register",
            200,
            data=other_supplier_data
        )
        
        if success and reg_response:
            other_supplier_token = reg_response['access_token']
            
            success, response = self.run_test(
                "Non-Participant File Retrieval (Should Fail)",
                "GET",
                f"files/chat/{self.job_id}",
                403,  # Forbidden
                token=other_supplier_token
            )

    def test_chat_file_download(self):
        """Test GET /api/download/chat/{file_id} endpoint"""
        print("\n" + "="*60)
        print("TESTING CHAT FILE DOWNLOAD")
        print("="*60)
        
        if not self.job_id:
            print("❌ Cannot test file download - no job ID")
            return
        
        # First, get the list of chat files to get file IDs
        success, files_response = self.run_test(
            "Get Chat Files for Download Test",
            "GET",
            f"files/chat/{self.job_id}",
            200,
            token=self.buyer_token
        )
        
        if not success or not files_response or len(files_response) == 0:
            print("❌ No chat files available for download test")
            return
        
        # Test downloading the first file
        test_file = files_response[0]
        file_id = test_file['id']
        
        # Test 1: Buyer downloading chat file
        success, response = self.run_test(
            "Buyer Download Chat File",
            "GET",
            f"download/chat/{file_id}",
            200,
            token=self.buyer_token
        )
        
        if success:
            print(f"   ✅ Buyer successfully downloaded file: {test_file['filename']}")
        
        # Test 2: Supplier downloading chat file
        success, response = self.run_test(
            "Supplier Download Chat File",
            "GET",
            f"download/chat/{file_id}",
            200,
            token=self.supplier_token
        )
        
        if success:
            print(f"   ✅ Supplier successfully downloaded file: {test_file['filename']}")
        
        # Test 3: Admin downloading chat file
        success, response = self.run_test(
            "Admin Download Chat File",
            "GET",
            f"download/chat/{file_id}",
            200,
            token=self.admin_token
        )
        
        if success:
            print(f"   ✅ Admin successfully downloaded file: {test_file['filename']}")
        
        # Test 4: Unauthorized download (should fail)
        success, response = self.run_test(
            "Unauthorized File Download (Should Fail)",
            "GET",
            f"download/chat/{file_id}",
            401,
            token=None
        )
        
        # Test 5: Download non-existent file (should fail)
        fake_file_id = "non-existent-file-id"
        success, response = self.run_test(
            "Download Non-Existent File (Should Fail)",
            "GET",
            f"download/chat/{fake_file_id}",
            404,
            token=self.buyer_token
        )

    def test_message_deletion(self):
        """Test DELETE /api/messages/{message_id} endpoint"""
        print("\n" + "="*60)
        print("TESTING MESSAGE DELETION")
        print("="*60)
        
        if not self.job_id:
            print("❌ Cannot test message deletion - no job ID")
            return
        
        # First, send a message with file attachment to test deletion
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        pdf_path = self.create_test_file("deletion_test.pdf", pdf_content, "binary")
        
        with open(pdf_path, 'rb') as f:
            files = {'files': ('deletion_test.pdf', f, 'application/pdf')}
            data = {'message': 'This message will be deleted to test deletion functionality.'}
            
            success, response = self.run_test(
                "Send Message for Deletion Test",
                "POST",
                f"jobs/{self.job_id}/chat/with-files",
                200,
                data=data,
                files=files,
                token=self.buyer_token
            )
            
            if success and response:
                message_to_delete = response.get('chat_message', {})
                message_id = message_to_delete.get('id')
                print(f"   ✅ Message created for deletion test: {message_id}")
                
                # Test 1: User deleting their own message
                success, delete_response = self.run_test(
                    "User Delete Own Message",
                    "DELETE",
                    f"messages/{message_id}",
                    200,
                    token=self.buyer_token
                )
                
                if success:
                    print("   ✅ User successfully deleted their own message")
        
        # Send another message for admin deletion test
        data = {'message': 'This message will be deleted by admin.'}
        
        success, response = self.run_test(
            "Send Message for Admin Deletion Test",
            "POST",
            f"jobs/{self.job_id}/chat",
            200,
            data=data,
            token=self.supplier_token
        )
        
        if success and response:
            message_to_delete = response.get('chat_message', {})
            message_id = message_to_delete.get('id')
            
            # Test 2: Admin deleting any message
            success, delete_response = self.run_test(
                "Admin Delete Any Message",
                "DELETE",
                f"messages/{message_id}",
                200,
                token=self.admin_token
            )
            
            if success:
                print("   ✅ Admin successfully deleted message")
        
        # Test 3: User trying to delete someone else's message (should fail)
        data = {'message': 'This message belongs to supplier.'}
        
        success, response = self.run_test(
            "Send Message from Supplier",
            "POST",
            f"jobs/{self.job_id}/chat",
            200,
            data=data,
            token=self.supplier_token
        )
        
        if success and response:
            message_to_delete = response.get('chat_message', {})
            message_id = message_to_delete.get('id')
            
            # Buyer trying to delete supplier's message
            success, delete_response = self.run_test(
                "User Delete Others Message (Should Fail)",
                "DELETE",
                f"messages/{message_id}",
                403,
                token=self.buyer_token
            )
        
        # Test 4: Delete non-existent message (should fail)
        fake_message_id = "non-existent-message-id"
        success, response = self.run_test(
            "Delete Non-Existent Message (Should Fail)",
            "DELETE",
            f"messages/{fake_message_id}",
            404,
            token=self.buyer_token
        )
        
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_backward_compatibility(self):
        """Test backward compatibility with original chat endpoint"""
        print("\n" + "="*60)
        print("TESTING BACKWARD COMPATIBILITY")
        print("="*60)
        
        if not self.job_id:
            print("❌ Cannot test backward compatibility - no job ID")
            return
        
        # Test 1: Original POST /api/jobs/{job_id}/chat endpoint still works
        message_data = {
            "message": "Testing backward compatibility with original chat endpoint."
        }
        
        success, response = self.run_test(
            "Original Chat Endpoint (Backward Compatibility)",
            "POST",
            f"jobs/{self.job_id}/chat",
            200,
            data=message_data,
            token=self.buyer_token
        )
        
        if success and response:
            print("   ✅ Original chat endpoint works correctly")
        
        # Test 2: Get chat messages to verify both old and new formats work
        success, response = self.run_test(
            "Get Chat Messages (Mixed Formats)",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if success and response:
            print(f"   ✅ Retrieved {len(response)} chat messages")
            
            # Check message formats
            text_only_messages = 0
            messages_with_files = 0
            
            for message in response:
                file_attachments = message.get('file_attachments', [])
                if file_attachments:
                    messages_with_files += 1
                else:
                    text_only_messages += 1
            
            print(f"     - Text-only messages: {text_only_messages}")
            print(f"     - Messages with files: {messages_with_files}")
            print("   ✅ Both message formats handled correctly")

    def test_authorization_scenarios(self):
        """Test comprehensive authorization scenarios"""
        print("\n" + "="*60)
        print("TESTING AUTHORIZATION SCENARIOS")
        print("="*60)
        
        if not self.job_id:
            print("❌ Cannot test authorization - no job ID")
            return
        
        # Create unauthorized user (not part of the chat)
        unauthorized_data = {
            "email": f"unauthorized_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Unauthorized Co",
            "contact_phone": "+91-9876543213",
            "role": "supplier",
            "gst_number": "29UNAUTH1234F1Z5",
            "address": "999 Unauthorized Street, Chennai, Tamil Nadu - 600001"
        }
        
        success, response = self.run_test(
            "Create Unauthorized User",
            "POST",
            "auth/register",
            200,
            data=unauthorized_data
        )
        
        if success and response:
            unauthorized_token = response['access_token']
            
            # Test unauthorized file upload
            pdf_content = b"%PDF-1.4\ntest"
            pdf_path = self.create_test_file("unauthorized.pdf", pdf_content, "binary")
            
            with open(pdf_path, 'rb') as f:
                files = {'files': ('unauthorized.pdf', f, 'application/pdf')}
                success, response = self.run_test(
                    "Unauthorized File Upload (Should Fail)",
                    "POST",
                    f"upload/chat/{self.job_id}",
                    403,
                    files=files,
                    token=unauthorized_token
                )
            
            # Test unauthorized message sending
            data = {'message': 'Unauthorized message'}
            success, response = self.run_test(
                "Unauthorized Message Send (Should Fail)",
                "POST",
                f"jobs/{self.job_id}/chat/with-files",
                403,
                data=data,
                token=unauthorized_token
            )
            
            # Test unauthorized file retrieval
            success, response = self.run_test(
                "Unauthorized File Retrieval (Should Fail)",
                "GET",
                f"files/chat/{self.job_id}",
                403,
                token=unauthorized_token
            )
            
            # Test unauthorized chat access
            success, response = self.run_test(
                "Unauthorized Chat Access (Should Fail)",
                "GET",
                f"jobs/{self.job_id}/chat",
                403,
                token=unauthorized_token
            )
            
            # Clean up
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

    def run_all_tests(self):
        """Run all chat file sharing tests"""
        print("\n" + "="*80)
        print("BUILDBIDZ CHAT FILE SHARING FUNCTIONALITY TEST SUITE")
        print("="*80)
        
        # Setup
        if not self.setup_test_accounts():
            print("❌ Failed to setup test accounts")
            return
        
        if not self.establish_chat_eligibility():
            print("❌ Failed to establish chat eligibility")
            return
        
        # Run all tests
        self.test_chat_file_upload_endpoint()
        self.test_enhanced_message_sending()
        self.test_chat_file_retrieval()
        self.test_chat_file_download()
        self.test_message_deletion()
        self.test_backward_compatibility()
        self.test_authorization_scenarios()
        
        # Final summary
        print("\n" + "="*80)
        print("CHAT FILE SHARING TEST RESULTS SUMMARY")
        print("="*80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL CHAT FILE SHARING TESTS PASSED!")
            print("✅ Chat file upload endpoint working")
            print("✅ Enhanced message sending working")
            print("✅ Chat file retrieval working")
            print("✅ Chat file download working")
            print("✅ Message deletion working")
            print("✅ Backward compatibility maintained")
            print("✅ Authorization controls working")
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} TESTS FAILED")
            print("Please review the failed tests above")

if __name__ == "__main__":
    tester = ChatFileSharingTester()
    tester.run_all_tests()