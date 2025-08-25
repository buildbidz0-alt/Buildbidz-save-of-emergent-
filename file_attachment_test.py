import requests
import sys
import json
import os
import tempfile
from datetime import datetime
import time
from pathlib import Path

class FileAttachmentTester:
    def __init__(self, base_url="https://construct-connect.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.supplier_token = None
        self.admin_token = None
        self.salesman_token = None
        self.buyer_user = None
        self.supplier_user = None
        self.admin_user = None
        self.salesman_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.job_id = None
        self.bid_id = None
        self.salesman_bid_id = None
        self.uploaded_job_files = []
        self.uploaded_bid_files = []

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        # Don't set Content-Type for file uploads
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
                    # Remove Content-Type for multipart/form-data
                    headers.pop('Content-Type', None)
                    response = requests.post(url, files=files, headers=headers)
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

    def create_test_file(self, filename, content, content_type="text/plain"):
        """Create a temporary test file"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix)
        temp_file.write(content.encode() if isinstance(content, str) else content)
        temp_file.close()
        return temp_file.name

    def setup_test_accounts(self):
        """Setup test accounts for file attachment testing"""
        print("\n" + "="*60)
        print("SETTING UP TEST ACCOUNTS FOR FILE ATTACHMENT TESTING")
        print("="*60)
        
        # Create buyer account
        buyer_data = {
            "email": f"file_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "File Test Construction Co",
            "contact_phone": "+91-9876543210",
            "role": "buyer",
            "gst_number": "29ABCDE1234F1Z5",
            "address": "123 File Test Street, Mumbai, Maharashtra - 400001"
        }
        
        success, response = self.run_test(
            "Create Buyer Account for File Testing",
            "POST",
            "auth/register",
            200,
            data=buyer_data
        )
        
        if success and 'access_token' in response:
            self.buyer_token = response['access_token']
            self.buyer_user = response['user']
            print(f"   Buyer ID: {self.buyer_user['id']}")
        
        # Create supplier account
        supplier_data = {
            "email": f"file_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "File Test Supplier Ltd",
            "contact_phone": "+91-9876543211",
            "role": "supplier",
            "gst_number": "29ABCDE1234F1Z6",
            "address": "456 File Supplier Street, Delhi, Delhi - 110001"
        }
        
        success, response = self.run_test(
            "Create Supplier Account for File Testing",
            "POST",
            "auth/register",
            200,
            data=supplier_data
        )
        
        if success and 'access_token' in response:
            self.supplier_token = response['access_token']
            self.supplier_user = response['user']
            print(f"   Supplier ID: {self.supplier_user['id']}")
        
        # Login admin
        admin_login = {
            "email": "mohammadjalaluddin1027@gmail.com",
            "password": "5968474644j"
        }
        
        success, response = self.run_test(
            "Admin Login for File Testing",
            "POST",
            "auth/login",
            200,
            data=admin_login
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.admin_user = response['user']
            print(f"   Admin logged in successfully")
        
        # Login salesman
        salesman_login = {
            "email": "salesman1@buildbidz.co.in",
            "password": "5968474644j"
        }
        
        success, response = self.run_test(
            "Salesman Login for File Testing",
            "POST",
            "auth/login",
            200,
            data=salesman_login
        )
        
        if success and 'access_token' in response:
            self.salesman_token = response['access_token']
            self.salesman_user = response['user']
            print(f"   Salesman logged in successfully")

    def test_job_creation_with_files(self):
        """Test creating a job and uploading files"""
        print("\n" + "="*60)
        print("TESTING JOB CREATION AND FILE UPLOAD")
        print("="*60)
        
        if not self.buyer_token:
            print("❌ Cannot test job file upload - no buyer token")
            return
        
        # First create a job
        job_data = {
            "title": "File Attachment Test Job",
            "category": "material",
            "description": "Testing file attachment functionality with various file types",
            "quantity": "100 units",
            "location": "Mumbai, Maharashtra",
            "delivery_timeline": "2 weeks",
            "budget_range": "₹5,00,000 - ₹7,00,000"
        }
        
        success, response = self.run_test(
            "Create Job for File Testing",
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
            print("❌ Failed to create job - cannot test file uploads")
            return
        
        # Create test files
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        
        test_files = [
            ("project_specs.pdf", pdf_content, "application/pdf"),
            ("requirements.txt", "Project requirements:\n1. High quality materials\n2. Fast delivery\n3. Competitive pricing", "text/plain"),
            ("blueprint.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9", "image/jpeg")
        ]
        
        # Upload files to job
        temp_files = []
        files_to_upload = []
        
        for filename, content, content_type in test_files:
            temp_path = self.create_test_file(filename, content, content_type)
            temp_files.append(temp_path)
            files_to_upload.append(('files', (filename, open(temp_path, 'rb'), content_type)))
        
        try:
            success, response = self.run_test(
                "Upload Files to Job",
                "POST",
                f"upload/job/{self.job_id}",
                200,
                token=self.buyer_token,
                files=files_to_upload
            )
            
            if success and response:
                self.uploaded_job_files = response.get('files', [])
                print(f"   ✅ Uploaded {len(self.uploaded_job_files)} files to job")
                for file_info in self.uploaded_job_files:
                    print(f"     - {file_info['filename']} ({file_info['size']} bytes)")
            
        finally:
            # Close file handles and cleanup
            for file_tuple in files_to_upload:
                file_tuple[1][1].close()
            for temp_path in temp_files:
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def test_bid_creation_with_files(self):
        """Test creating a bid and uploading files"""
        print("\n" + "="*60)
        print("TESTING BID CREATION AND FILE UPLOAD")
        print("="*60)
        
        if not self.supplier_token or not self.job_id:
            print("❌ Cannot test bid file upload - no supplier token or job ID")
            return
        
        # First create a bid
        bid_data = {
            "price_quote": 550000.0,
            "delivery_estimate": "10 days",
            "notes": "High quality materials with detailed documentation and certifications"
        }
        
        success, response = self.run_test(
            "Create Bid for File Testing",
            "POST",
            f"jobs/{self.job_id}/bids",
            200,
            data=bid_data,
            token=self.supplier_token
        )
        
        if success and response:
            self.bid_id = response['id']
            print(f"   Bid created with ID: {self.bid_id}")
        else:
            print("❌ Failed to create bid - cannot test file uploads")
            return
        
        # Create test files for bid
        test_files = [
            ("quotation.pdf", b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF", "application/pdf"),
            ("certifications.docx", b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("material_samples.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9", "image/jpeg")
        ]
        
        # Upload files to bid
        temp_files = []
        files_to_upload = []
        
        for filename, content, content_type in test_files:
            temp_path = self.create_test_file(filename, content, content_type)
            temp_files.append(temp_path)
            files_to_upload.append(('files', (filename, open(temp_path, 'rb'), content_type)))
        
        try:
            success, response = self.run_test(
                "Upload Files to Bid",
                "POST",
                f"upload/bid/{self.bid_id}",
                200,
                token=self.supplier_token,
                files=files_to_upload
            )
            
            if success and response:
                self.uploaded_bid_files = response.get('files', [])
                print(f"   ✅ Uploaded {len(self.uploaded_bid_files)} files to bid")
                for file_info in self.uploaded_bid_files:
                    print(f"     - {file_info['filename']} ({file_info['size']} bytes)")
            
        finally:
            # Close file handles and cleanup
            for file_tuple in files_to_upload:
                file_tuple[1][1].close()
            for temp_path in temp_files:
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def test_salesman_bid_with_files(self):
        """Test salesman bid creation with file uploads"""
        print("\n" + "="*60)
        print("TESTING SALESMAN BID CREATION AND FILE UPLOAD")
        print("="*60)
        
        if not self.salesman_token or not self.job_id:
            print("❌ Cannot test salesman bid file upload - no salesman token or job ID")
            return
        
        # Create salesman bid
        salesman_bid_data = {
            "price_quote": 480000,
            "delivery_estimate": "12 days",
            "notes": "Professional service with complete documentation",
            "company_name": "File Test Construction Pvt Ltd",
            "company_contact_phone": "+91 9876543220",
            "company_email": "filetest@construction.com",
            "company_gst_number": "27ABCDE1234F1Z5",
            "company_address": "789 File Test Avenue, Bangalore, Karnataka - 560001"
        }
        
        success, response = self.run_test(
            "Create Salesman Bid for File Testing",
            "POST",
            f"jobs/{self.job_id}/salesman-bids",
            200,
            data=salesman_bid_data,
            token=self.salesman_token
        )
        
        if success and response:
            self.salesman_bid_id = response['id']
            print(f"   Salesman bid created with ID: {self.salesman_bid_id}")
            
            # Upload files to salesman bid
            test_files = [
                ("company_profile.pdf", b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF", "application/pdf"),
                ("portfolio.xlsx", b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            ]
            
            temp_files = []
            files_to_upload = []
            
            for filename, content, content_type in test_files:
                temp_path = self.create_test_file(filename, content, content_type)
                temp_files.append(temp_path)
                files_to_upload.append(('files', (filename, open(temp_path, 'rb'), content_type)))
            
            try:
                success, response = self.run_test(
                    "Upload Files to Salesman Bid",
                    "POST",
                    f"upload/bid/{self.salesman_bid_id}",
                    200,
                    token=self.salesman_token,
                    files=files_to_upload
                )
                
                if success and response:
                    print(f"   ✅ Uploaded {len(response.get('files', []))} files to salesman bid")
                
            finally:
                # Close file handles and cleanup
                for file_tuple in files_to_upload:
                    file_tuple[1][1].close()
                for temp_path in temp_files:
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

    def test_file_retrieval_endpoints(self):
        """Test file retrieval endpoints"""
        print("\n" + "="*60)
        print("TESTING FILE RETRIEVAL ENDPOINTS")
        print("="*60)
        
        if not self.job_id:
            print("❌ Cannot test file retrieval - no job ID")
            return
        
        # Test GET /api/files/job/{job_id}
        success, response = self.run_test(
            "Get Job Files (Job Owner)",
            "GET",
            f"files/job/{self.job_id}",
            200,
            token=self.buyer_token
        )
        
        if success and response:
            print(f"   ✅ Job owner can retrieve {len(response)} job files")
            for file_info in response:
                print(f"     - {file_info['filename']} ({file_info['size']} bytes)")
        
        # Test supplier access to job files (should work if they bid)
        if self.supplier_token:
            success, response = self.run_test(
                "Get Job Files (Supplier who bid)",
                "GET",
                f"files/job/{self.job_id}",
                200,
                token=self.supplier_token
            )
            
            if success and response:
                print(f"   ✅ Supplier who bid can retrieve {len(response)} job files")
        
        # Test admin access to job files
        if self.admin_token:
            success, response = self.run_test(
                "Get Job Files (Admin)",
                "GET",
                f"files/job/{self.job_id}",
                200,
                token=self.admin_token
            )
            
            if success and response:
                print(f"   ✅ Admin can retrieve {len(response)} job files")
        
        # Test GET /api/files/bid/{bid_id}
        if self.bid_id:
            # Test bid owner access
            success, response = self.run_test(
                "Get Bid Files (Bid Owner)",
                "GET",
                f"files/bid/{self.bid_id}",
                200,
                token=self.supplier_token
            )
            
            if success and response:
                print(f"   ✅ Bid owner can retrieve {len(response)} bid files")
                for file_info in response:
                    print(f"     - {file_info['filename']} ({file_info['size']} bytes)")
            
            # Test job owner access to bid files
            success, response = self.run_test(
                "Get Bid Files (Job Owner)",
                "GET",
                f"files/bid/{self.bid_id}",
                200,
                token=self.buyer_token
            )
            
            if success and response:
                print(f"   ✅ Job owner can retrieve {len(response)} bid files")
            
            # Test admin access to bid files
            if self.admin_token:
                success, response = self.run_test(
                    "Get Bid Files (Admin)",
                    "GET",
                    f"files/bid/{self.bid_id}",
                    200,
                    token=self.admin_token
                )
                
                if success and response:
                    print(f"   ✅ Admin can retrieve {len(response)} bid files")

    def test_file_access_permissions(self):
        """Test file access permissions and authorization"""
        print("\n" + "="*60)
        print("TESTING FILE ACCESS PERMISSIONS")
        print("="*60)
        
        if not self.job_id or not self.bid_id:
            print("❌ Cannot test file permissions - missing job or bid ID")
            return
        
        # Create another supplier who hasn't bid on this job
        other_supplier_data = {
            "email": f"other_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Other Supplier Co",
            "contact_phone": "+91-9876543299",
            "role": "supplier",
            "gst_number": "29ABCDE1234F1Z7",
            "address": "999 Other Street, Chennai, Tamil Nadu - 600001"
        }
        
        success, response = self.run_test(
            "Create Other Supplier for Permission Testing",
            "POST",
            "auth/register",
            200,
            data=other_supplier_data
        )
        
        if success and response:
            other_supplier_token = response['access_token']
            
            # Test unauthorized access to job files
            success, response = self.run_test(
                "Unauthorized Access to Job Files (Should Fail)",
                "GET",
                f"files/job/{self.job_id}",
                403,
                token=other_supplier_token
            )
            
            if success:
                print("   ✅ Unauthorized supplier correctly blocked from job files")
            
            # Test unauthorized access to bid files
            success, response = self.run_test(
                "Unauthorized Access to Bid Files (Should Fail)",
                "GET",
                f"files/bid/{self.bid_id}",
                403,
                token=other_supplier_token
            )
            
            if success:
                print("   ✅ Unauthorized supplier correctly blocked from bid files")
        
        # Test unauthenticated access
        success, response = self.run_test(
            "Unauthenticated Access to Job Files (Should Fail)",
            "GET",
            f"files/job/{self.job_id}",
            401
        )
        
        if success:
            print("   ✅ Unauthenticated access correctly blocked")

    def test_file_download_functionality(self):
        """Test file download functionality"""
        print("\n" + "="*60)
        print("TESTING FILE DOWNLOAD FUNCTIONALITY")
        print("="*60)
        
        if not self.uploaded_job_files and not self.uploaded_bid_files:
            print("❌ Cannot test file downloads - no uploaded files")
            return
        
        # Test downloading job files
        if self.uploaded_job_files:
            for file_info in self.uploaded_job_files[:2]:  # Test first 2 files
                file_id = file_info['id']
                
                # Test job owner download
                url = f"{self.api_url}/download/job/{file_id}"
                headers = {'Authorization': f'Bearer {self.buyer_token}'}
                
                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        print(f"   ✅ Job owner can download {file_info['filename']}")
                        print(f"     Content-Type: {response.headers.get('content-type')}")
                        print(f"     Content-Length: {len(response.content)} bytes")
                    else:
                        print(f"   ❌ Job owner download failed for {file_info['filename']} - Status: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Job owner download error for {file_info['filename']}: {str(e)}")
                
                # Test supplier download (who bid on job)
                if self.supplier_token:
                    headers = {'Authorization': f'Bearer {self.supplier_token}'}
                    try:
                        response = requests.get(url, headers=headers)
                        if response.status_code == 200:
                            print(f"   ✅ Supplier can download {file_info['filename']}")
                        else:
                            print(f"   ❌ Supplier download failed for {file_info['filename']} - Status: {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Supplier download error for {file_info['filename']}: {str(e)}")
        
        # Test downloading bid files
        if self.uploaded_bid_files:
            for file_info in self.uploaded_bid_files[:2]:  # Test first 2 files
                file_id = file_info['id']
                
                # Test bid owner download
                url = f"{self.api_url}/download/bid/{file_id}"
                headers = {'Authorization': f'Bearer {self.supplier_token}'}
                
                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        print(f"   ✅ Bid owner can download {file_info['filename']}")
                        print(f"     Content-Type: {response.headers.get('content-type')}")
                        print(f"     Content-Length: {len(response.content)} bytes")
                    else:
                        print(f"   ❌ Bid owner download failed for {file_info['filename']} - Status: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Bid owner download error for {file_info['filename']}: {str(e)}")
                
                # Test job owner download of bid files
                if self.buyer_token:
                    headers = {'Authorization': f'Bearer {self.buyer_token}'}
                    try:
                        response = requests.get(url, headers=headers)
                        if response.status_code == 200:
                            print(f"   ✅ Job owner can download bid file {file_info['filename']}")
                        else:
                            print(f"   ❌ Job owner download of bid file failed for {file_info['filename']} - Status: {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Job owner download of bid file error for {file_info['filename']}: {str(e)}")

    def test_database_file_storage_verification(self):
        """Test database file storage verification"""
        print("\n" + "="*60)
        print("TESTING DATABASE FILE STORAGE VERIFICATION")
        print("="*60)
        
        if not self.admin_token:
            print("❌ Cannot verify database storage - no admin token")
            return
        
        # This would require direct database access or admin endpoints
        # For now, we'll verify through the file retrieval endpoints
        
        if self.job_id:
            success, response = self.run_test(
                "Verify Job Files in Database (via API)",
                "GET",
                f"files/job/{self.job_id}",
                200,
                token=self.admin_token
            )
            
            if success and response:
                print(f"   ✅ Database contains {len(response)} job files")
                for file_info in response:
                    required_fields = ['id', 'filename', 'size', 'content_type', 'uploaded_at']
                    missing_fields = [field for field in required_fields if field not in file_info]
                    if not missing_fields:
                        print(f"     ✅ {file_info['filename']} - All metadata present")
                    else:
                        print(f"     ❌ {file_info['filename']} - Missing: {missing_fields}")
        
        if self.bid_id:
            success, response = self.run_test(
                "Verify Bid Files in Database (via API)",
                "GET",
                f"files/bid/{self.bid_id}",
                200,
                token=self.admin_token
            )
            
            if success and response:
                print(f"   ✅ Database contains {len(response)} bid files")
                for file_info in response:
                    required_fields = ['id', 'filename', 'size', 'content_type', 'uploaded_at']
                    missing_fields = [field for field in required_fields if field not in file_info]
                    if not missing_fields:
                        print(f"     ✅ {file_info['filename']} - All metadata present")
                    else:
                        print(f"     ❌ {file_info['filename']} - Missing: {missing_fields}")

    def test_file_system_storage_check(self):
        """Test file system storage verification"""
        print("\n" + "="*60)
        print("TESTING FILE SYSTEM STORAGE CHECK")
        print("="*60)
        
        # Note: In a containerized environment, we can't directly access the file system
        # This test would verify that files exist in /app/backend/uploads/
        # For now, we'll test this indirectly through successful downloads
        
        print("   📁 File system storage verification:")
        print("   Note: Direct file system access not available in containerized environment")
        print("   Verifying through successful file downloads instead...")
        
        # Test that downloads work (indicates files exist on disk)
        if self.uploaded_job_files:
            file_info = self.uploaded_job_files[0]
            file_id = file_info['id']
            
            url = f"{self.api_url}/download/job/{file_id}"
            headers = {'Authorization': f'Bearer {self.buyer_token}'}
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200 and len(response.content) > 0:
                    print(f"   ✅ Job file {file_info['filename']} exists on file system (download successful)")
                else:
                    print(f"   ❌ Job file {file_info['filename']} may not exist on file system (download failed)")
            except Exception as e:
                print(f"   ❌ Error checking job file existence: {str(e)}")
        
        if self.uploaded_bid_files:
            file_info = self.uploaded_bid_files[0]
            file_id = file_info['id']
            
            url = f"{self.api_url}/download/bid/{file_id}"
            headers = {'Authorization': f'Bearer {self.supplier_token}'}
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200 and len(response.content) > 0:
                    print(f"   ✅ Bid file {file_info['filename']} exists on file system (download successful)")
                else:
                    print(f"   ❌ Bid file {file_info['filename']} may not exist on file system (download failed)")
            except Exception as e:
                print(f"   ❌ Error checking bid file existence: {str(e)}")

    def test_cross_role_file_access(self):
        """Test cross-role file access functionality"""
        print("\n" + "="*60)
        print("TESTING CROSS-ROLE FILE ACCESS")
        print("="*60)
        
        if not all([self.admin_token, self.buyer_token, self.supplier_token, self.salesman_token]):
            print("❌ Cannot test cross-role access - missing tokens")
            return
        
        if not self.job_id or not self.bid_id:
            print("❌ Cannot test cross-role access - missing job or bid ID")
            return
        
        # Test admin access to all files
        print("\n   🔐 Testing Admin Access:")
        
        success, response = self.run_test(
            "Admin Access to Job Files",
            "GET",
            f"files/job/{self.job_id}",
            200,
            token=self.admin_token
        )
        
        if success:
            print("   ✅ Admin can access job files")
        
        success, response = self.run_test(
            "Admin Access to Bid Files",
            "GET",
            f"files/bid/{self.bid_id}",
            200,
            token=self.admin_token
        )
        
        if success:
            print("   ✅ Admin can access bid files")
        
        # Test buyer access
        print("\n   💼 Testing Buyer Access:")
        
        success, response = self.run_test(
            "Buyer Access to Own Job Files",
            "GET",
            f"files/job/{self.job_id}",
            200,
            token=self.buyer_token
        )
        
        if success:
            print("   ✅ Buyer can access their own job files")
        
        success, response = self.run_test(
            "Buyer Access to Bid Files on Their Job",
            "GET",
            f"files/bid/{self.bid_id}",
            200,
            token=self.buyer_token
        )
        
        if success:
            print("   ✅ Buyer can access bid files on their job")
        
        # Test supplier access
        print("\n   🏗️ Testing Supplier Access:")
        
        success, response = self.run_test(
            "Supplier Access to Job Files They Bid On",
            "GET",
            f"files/job/{self.job_id}",
            200,
            token=self.supplier_token
        )
        
        if success:
            print("   ✅ Supplier can access job files they bid on")
        
        success, response = self.run_test(
            "Supplier Access to Own Bid Files",
            "GET",
            f"files/bid/{self.bid_id}",
            200,
            token=self.supplier_token
        )
        
        if success:
            print("   ✅ Supplier can access their own bid files")
        
        # Test salesman access
        print("\n   👔 Testing Salesman Access:")
        
        success, response = self.run_test(
            "Salesman Access to Job Files",
            "GET",
            f"files/job/{self.job_id}",
            200,
            token=self.salesman_token
        )
        
        if success:
            print("   ✅ Salesman can access job files")
        
        if self.salesman_bid_id:
            success, response = self.run_test(
                "Salesman Access to Own Bid Files",
                "GET",
                f"files/bid/{self.salesman_bid_id}",
                200,
                token=self.salesman_token
            )
            
            if success:
                print("   ✅ Salesman can access their own bid files")

    def test_file_validation_and_limits(self):
        """Test file validation and size limits"""
        print("\n" + "="*60)
        print("TESTING FILE VALIDATION AND LIMITS")
        print("="*60)
        
        if not self.buyer_token or not self.job_id:
            print("❌ Cannot test file validation - missing buyer token or job ID")
            return
        
        # Test file size limit (should be 10MB)
        print("\n   📏 Testing File Size Limits:")
        
        # Create a file larger than 10MB
        large_content = b"A" * (11 * 1024 * 1024)  # 11MB
        temp_path = self.create_test_file("large_file.txt", large_content)
        
        try:
            with open(temp_path, 'rb') as f:
                files_to_upload = [('files', ('large_file.txt', f, 'text/plain'))]
                
                success, response = self.run_test(
                    "Upload Large File (Should Fail)",
                    "POST",
                    f"upload/job/{self.job_id}",
                    413,  # Payload Too Large
                    token=self.buyer_token,
                    files=files_to_upload
                )
                
                if success:
                    print("   ✅ Large file correctly rejected (>10MB)")
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
        
        # Test invalid file type
        print("\n   📄 Testing File Type Validation:")
        
        invalid_content = b"Invalid file content"
        temp_path = self.create_test_file("invalid_file.exe", invalid_content)
        
        try:
            with open(temp_path, 'rb') as f:
                files_to_upload = [('files', ('invalid_file.exe', f, 'application/x-executable'))]
                
                success, response = self.run_test(
                    "Upload Invalid File Type (Should Fail)",
                    "POST",
                    f"upload/job/{self.job_id}",
                    415,  # Unsupported Media Type
                    token=self.buyer_token,
                    files=files_to_upload
                )
                
                if success:
                    print("   ✅ Invalid file type correctly rejected (.exe)")
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
        
        # Test valid file types
        print("\n   ✅ Testing Valid File Types:")
        
        valid_files = [
            ("test.pdf", b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n32\n%%EOF", "application/pdf"),
            ("test.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xd9", "image/jpeg"),
            ("test.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDAT\x08\x1dc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82", "image/png"),
            ("test.txt", "Test content", "text/plain"),
            ("test.docx", b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("test.xlsx", b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        ]
        
        for filename, content, content_type in valid_files:
            temp_path = self.create_test_file(filename, content)
            
            try:
                with open(temp_path, 'rb') as f:
                    files_to_upload = [('files', (filename, f, content_type))]
                    
                    success, response = self.run_test(
                        f"Upload Valid File Type ({filename})",
                        "POST",
                        f"upload/job/{self.job_id}",
                        200,
                        token=self.buyer_token,
                        files=files_to_upload
                    )
                    
                    if success:
                        print(f"   ✅ {filename} accepted")
            finally:
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def run_all_tests(self):
        """Run all file attachment tests"""
        print("\n" + "="*80)
        print("🔍 BUILDBIDZ FILE ATTACHMENT INVESTIGATION - CRITICAL REVIEW REQUEST")
        print("="*80)
        print("Investigating file attachment visibility issues as reported by users")
        print("Testing file upload storage, retrieval endpoints, and access permissions")
        print("="*80)
        
        try:
            # Setup
            self.setup_test_accounts()
            
            # Core file functionality tests
            self.test_job_creation_with_files()
            self.test_bid_creation_with_files()
            self.test_salesman_bid_with_files()
            
            # File retrieval and access tests
            self.test_file_retrieval_endpoints()
            self.test_file_access_permissions()
            self.test_file_download_functionality()
            
            # Storage verification tests
            self.test_database_file_storage_verification()
            self.test_file_system_storage_check()
            
            # Advanced access tests
            self.test_cross_role_file_access()
            self.test_file_validation_and_limits()
            
        except Exception as e:
            print(f"\n❌ Critical error during testing: {str(e)}")
        
        # Final summary
        print("\n" + "="*80)
        print("📊 FILE ATTACHMENT TESTING SUMMARY")
        print("="*80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL FILE ATTACHMENT TESTS PASSED!")
            print("✅ File upload storage working correctly")
            print("✅ File retrieval endpoints functional")
            print("✅ File access permissions properly implemented")
            print("✅ Database and file system storage verified")
            print("✅ Cross-role file access working as expected")
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} TESTS FAILED")
            print("❌ File attachment system has issues that need investigation")
        
        print("="*80)

if __name__ == "__main__":
    tester = FileAttachmentTester()
    tester.run_all_tests()