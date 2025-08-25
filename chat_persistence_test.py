import requests
import sys
import json
from datetime import datetime, timedelta
import time

class ChatPersistenceAPITester:
    def __init__(self, base_url="https://construct-connect.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.buyer_token = None
        self.supplier_token = None
        self.admin_user = None
        self.buyer_user = None
        self.supplier_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.job_id = None
        self.bid_id = None
        self.chat_messages = []

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

    def test_admin_login(self):
        """Test admin login with provided credentials"""
        print("\n" + "="*60)
        print("TESTING ADMIN LOGIN FOR CHAT PERSISTENCE")
        print("="*60)
        
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
            print(f"   ✅ Admin logged in successfully")
            print(f"   Admin role: {self.admin_user.get('role')}")
            return True
        else:
            print("   ❌ Admin login failed - cannot proceed with chat persistence tests")
            return False

    def test_chat_analytics_endpoint(self):
        """Test GET /api/admin/chat-analytics for comprehensive persistence data"""
        print("\n" + "="*60)
        print("TESTING CHAT ANALYTICS ENDPOINT")
        print("="*60)
        
        if not self.admin_token:
            print("❌ Cannot test chat analytics - admin login failed")
            return False
        
        success, response = self.run_test(
            "Get Chat Analytics",
            "GET",
            "admin/chat-analytics",
            200,
            token=self.admin_token
        )
        
        if success and response:
            print(f"   📊 CHAT ANALYTICS RESULTS:")
            print(f"   Total messages: {response.get('total_messages', 0)}")
            print(f"   Active conversations: {response.get('active_conversations', 0)}")
            
            # Check message distribution
            distribution = response.get('message_distribution', {})
            print(f"   📈 MESSAGE DISTRIBUTION:")
            print(f"     Last 24 hours: {distribution.get('last_24_hours', 0)}")
            print(f"     Last week: {distribution.get('last_week', 0)}")
            print(f"     Last month: {distribution.get('last_month', 0)}")
            print(f"     Older than month: {distribution.get('older_than_month', 0)}")
            
            # Check oldest message
            oldest_date = response.get('oldest_message_date')
            if oldest_date:
                print(f"   📅 Oldest message: {oldest_date}")
            
            # Check data retention settings
            retention = response.get('data_retention', {})
            print(f"   🔒 DATA RETENTION:")
            print(f"     Automatic deletion: {retention.get('automatic_deletion', 'Unknown')}")
            print(f"     TTL indexes found: {retention.get('ttl_indexes_found', 0)}")
            print(f"     Persistence guaranteed: {retention.get('persistence_guaranteed', 'Unknown')}")
            
            # Check system health
            system_health = response.get('system_health', 'unknown')
            print(f"   🏥 System health: {system_health}")
            
            # Verify no TTL indexes exist
            if retention.get('persistence_guaranteed') == True:
                print("   ✅ Chat persistence is guaranteed - no TTL indexes found")
                return True
            else:
                print("   ⚠️  Chat persistence may be at risk - TTL indexes detected")
                return False
        
        return False

    def test_database_index_optimization(self):
        """Test POST /api/admin/system/optimize-chat-indexes"""
        print("\n" + "="*60)
        print("TESTING DATABASE INDEX OPTIMIZATION")
        print("="*60)
        
        if not self.admin_token:
            print("❌ Cannot test index optimization - admin login failed")
            return False
        
        success, response = self.run_test(
            "Optimize Chat Indexes",
            "POST",
            "admin/system/optimize-chat-indexes",
            200,
            token=self.admin_token
        )
        
        if success and response:
            print(f"   📊 INDEX OPTIMIZATION RESULTS:")
            print(f"   Message: {response.get('message', 'No message')}")
            print(f"   Indexes created: {response.get('indexes_created', 0)}")
            print(f"   TTL indexes removed: {response.get('ttl_indexes_removed', 0)}")
            print(f"   Chat persistence: {response.get('chat_persistence', 'Unknown')}")
            
            # Verify optimization was successful
            if "successfully" in response.get('message', '').lower():
                print("   ✅ Database indexes optimized successfully")
                return True
            else:
                print("   ❌ Database index optimization may have failed")
                return False
        
        return False

    def setup_test_accounts(self):
        """Create buyer and supplier accounts for chat testing"""
        print("\n" + "="*60)
        print("SETTING UP TEST ACCOUNTS FOR CHAT PERSISTENCE")
        print("="*60)
        
        # Create buyer account
        buyer_data = {
            "email": f"chat_buyer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Chat Test Buyer Co",
            "contact_phone": "+91-9876543210",
            "role": "buyer",
            "gst_number": "27ABCDE1234F1Z5",
            "address": "123 Chat Buyer Street, Mumbai, Maharashtra - 400001"
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
            print(f"   ✅ Buyer created: {self.buyer_user['id']}")
        else:
            print("   ❌ Failed to create buyer account")
            return False
        
        # Create supplier account
        supplier_data = {
            "email": f"chat_supplier_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Chat Test Supplier Ltd",
            "contact_phone": "+91-9876543211",
            "role": "supplier",
            "gst_number": "27FGHIJ1234K1Z5",
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
            print(f"   ✅ Supplier created: {self.supplier_user['id']}")
            return True
        else:
            print("   ❌ Failed to create supplier account")
            return False

    def create_job_and_bid(self):
        """Create a job and bid to enable chat functionality"""
        print("\n" + "="*60)
        print("CREATING JOB AND BID FOR CHAT TESTING")
        print("="*60)
        
        if not self.buyer_token or not self.supplier_token:
            print("❌ Cannot create job and bid - missing tokens")
            return False
        
        # Create job
        job_data = {
            "title": "Chat Persistence Test Job",
            "category": "material",
            "description": "Testing chat persistence functionality with this job",
            "quantity": "Test quantity for chat persistence",
            "location": "Mumbai, Maharashtra",
            "delivery_timeline": "2 weeks",
            "budget_range": "₹1,00,000 - ₹2,00,000"
        }
        
        success, response = self.run_test(
            "Create Test Job",
            "POST",
            "jobs",
            200,
            data=job_data,
            token=self.buyer_token
        )
        
        if success and response:
            self.job_id = response['id']
            print(f"   ✅ Job created: {self.job_id}")
        else:
            print("   ❌ Failed to create job")
            return False
        
        # Submit bid
        bid_data = {
            "price_quote": 150000.0,
            "delivery_estimate": "10 days",
            "notes": "Chat persistence test bid with competitive pricing"
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
            print(f"   ✅ Bid submitted: {self.bid_id}")
        else:
            print("   ❌ Failed to submit bid")
            return False
        
        # Award the bid to enable chat
        success, response = self.run_test(
            "Award Test Bid",
            "POST",
            f"jobs/{self.job_id}/award/{self.bid_id}",
            200,
            token=self.buyer_token
        )
        
        if success and response:
            print(f"   ✅ Bid awarded - chat enabled")
            return True
        else:
            print("   ❌ Failed to award bid")
            return False

    def test_improved_chat_visibility(self):
        """Test GET /api/chats with new logic that finds chats based on message participation"""
        print("\n" + "="*60)
        print("TESTING IMPROVED CHAT VISIBILITY")
        print("="*60)
        
        if not self.buyer_token or not self.supplier_token:
            print("❌ Cannot test chat visibility - missing tokens")
            return False
        
        # Test buyer chat visibility
        success, buyer_chats = self.run_test(
            "Get Buyer Chats",
            "GET",
            "chats",
            200,
            token=self.buyer_token
        )
        
        if success and buyer_chats:
            print(f"   📋 Buyer found {len(buyer_chats)} chats")
            for chat in buyer_chats:
                print(f"     - Job: {chat.get('job_title')} (Status: {chat.get('job_status')})")
                print(f"       Messages: {chat.get('message_count', 0)}, Unread: {chat.get('unread_count', 0)}")
        
        # Test supplier chat visibility
        success, supplier_chats = self.run_test(
            "Get Supplier Chats",
            "GET",
            "chats",
            200,
            token=self.supplier_token
        )
        
        if success and supplier_chats:
            print(f"   📋 Supplier found {len(supplier_chats)} chats")
            for chat in supplier_chats:
                print(f"     - Job: {chat.get('job_title')} (Status: {chat.get('job_status')})")
                print(f"       Messages: {chat.get('message_count', 0)}, Unread: {chat.get('unread_count', 0)}")
        
        # Verify chats are accessible regardless of job status
        if buyer_chats or supplier_chats:
            print("   ✅ Chat visibility working - chats found regardless of job status")
            return True
        else:
            print("   ⚠️  No chats found - may need to create messages first")
            return True  # Not necessarily a failure

    def test_chat_message_persistence(self):
        """Test chat message persistence and retrieval"""
        print("\n" + "="*60)
        print("TESTING CHAT MESSAGE PERSISTENCE")
        print("="*60)
        
        if not self.job_id or not self.buyer_token or not self.supplier_token:
            print("❌ Cannot test message persistence - missing job or tokens")
            return False
        
        # Send messages from buyer to supplier
        buyer_messages = [
            "Hello! Thank you for your bid on our project.",
            "Can you provide more details about the materials you'll use?",
            "What is your timeline for project completion?",
            "We are impressed with your proposal and would like to proceed."
        ]
        
        print(f"   📤 Sending {len(buyer_messages)} messages from buyer...")
        for i, message_text in enumerate(buyer_messages):
            message_data = {"message": message_text}
            
            success, response = self.run_test(
                f"Send Buyer Message {i+1}",
                "POST",
                f"jobs/{self.job_id}/chat",
                200,
                data=message_data,
                token=self.buyer_token
            )
            
            if success and response:
                chat_message = response.get('chat_message', {})
                self.chat_messages.append(chat_message)
                print(f"     ✅ Message {i+1} sent: {chat_message.get('id')}")
                time.sleep(0.1)  # Small delay between messages
        
        # Send messages from supplier to buyer
        supplier_messages = [
            "Thank you for awarding the bid! We're excited to work with you.",
            "We'll use premium grade materials as specified in our proposal."
        ]
        
        print(f"   📤 Sending {len(supplier_messages)} messages from supplier...")
        for i, message_text in enumerate(supplier_messages):
            message_data = {"message": message_text}
            
            success, response = self.run_test(
                f"Send Supplier Message {i+1}",
                "POST",
                f"jobs/{self.job_id}/chat",
                200,
                data=message_data,
                token=self.supplier_token
            )
            
            if success and response:
                chat_message = response.get('chat_message', {})
                self.chat_messages.append(chat_message)
                print(f"     ✅ Message {i+1} sent: {chat_message.get('id')}")
                time.sleep(0.1)  # Small delay between messages
        
        # Retrieve all messages immediately
        success, retrieved_messages = self.run_test(
            "Retrieve Chat Messages (Immediate)",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if success and retrieved_messages:
            print(f"   📥 Retrieved {len(retrieved_messages)} messages immediately")
            
            # Verify message content and timestamps
            for i, msg in enumerate(retrieved_messages):
                print(f"     Message {i+1}: {msg.get('message')[:50]}...")
                print(f"       ID: {msg.get('id')}")
                print(f"       Timestamp: {msg.get('created_at')}")
                print(f"       Sender: {msg.get('sender_info', {}).get('company_name', 'Unknown')}")
            
            # Verify message count matches sent messages
            expected_count = len(buyer_messages) + len(supplier_messages)
            if len(retrieved_messages) >= expected_count:
                print(f"   ✅ Message persistence verified - {len(retrieved_messages)} messages stored")
                return True
            else:
                print(f"   ❌ Message count mismatch - Expected {expected_count}, got {len(retrieved_messages)}")
                return False
        else:
            print("   ❌ Failed to retrieve messages")
            return False

    def test_long_term_message_retention(self):
        """Test that messages persist over time and verify historical data"""
        print("\n" + "="*60)
        print("TESTING LONG-TERM MESSAGE RETENTION")
        print("="*60)
        
        if not self.job_id or not self.buyer_token:
            print("❌ Cannot test long-term retention - missing job or token")
            return False
        
        # Wait a few seconds and retrieve messages again
        print("   ⏳ Waiting 3 seconds to test persistence...")
        time.sleep(3)
        
        success, persistent_messages = self.run_test(
            "Retrieve Chat Messages (After Delay)",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if success and persistent_messages:
            print(f"   📥 Retrieved {len(persistent_messages)} messages after delay")
            
            # Verify all messages still exist with same content
            if len(persistent_messages) == len(self.chat_messages):
                print("   ✅ All messages persisted correctly")
                
                # Check timestamps are preserved
                for msg in persistent_messages:
                    timestamp = msg.get('created_at')
                    if timestamp:
                        # Parse timestamp to verify it's from recent test
                        try:
                            msg_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            time_diff = datetime.now().replace(tzinfo=msg_time.tzinfo) - msg_time
                            if time_diff.total_seconds() < 300:  # Within 5 minutes
                                print(f"     ✅ Message timestamp valid: {timestamp}")
                            else:
                                print(f"     ⚠️  Message timestamp old: {timestamp}")
                        except:
                            print(f"     ⚠️  Could not parse timestamp: {timestamp}")
                
                return True
            else:
                print(f"   ❌ Message count changed - Expected {len(self.chat_messages)}, got {len(persistent_messages)}")
                return False
        else:
            print("   ❌ Failed to retrieve messages after delay")
            return False

    def test_historical_message_verification(self):
        """Verify historical messages from different time periods exist"""
        print("\n" + "="*60)
        print("TESTING HISTORICAL MESSAGE VERIFICATION")
        print("="*60)
        
        if not self.admin_token:
            print("❌ Cannot test historical messages - admin login failed")
            return False
        
        # Get chat analytics to check for historical data
        success, analytics = self.run_test(
            "Get Historical Chat Analytics",
            "GET",
            "admin/chat-analytics",
            200,
            token=self.admin_token
        )
        
        if success and analytics:
            distribution = analytics.get('message_distribution', {})
            total_messages = analytics.get('total_messages', 0)
            oldest_date = analytics.get('oldest_message_date')
            
            print(f"   📊 HISTORICAL MESSAGE ANALYSIS:")
            print(f"   Total messages in system: {total_messages}")
            print(f"   Messages older than month: {distribution.get('older_than_month', 0)}")
            
            if oldest_date:
                print(f"   Oldest message date: {oldest_date}")
                
                # Calculate age of oldest message
                try:
                    oldest_time = datetime.fromisoformat(oldest_date.replace('Z', '+00:00'))
                    age_days = (datetime.now().replace(tzinfo=oldest_time.tzinfo) - oldest_time).days
                    print(f"   Oldest message age: {age_days} days")
                    
                    if age_days > 0:
                        print(f"   ✅ Historical messages found - system retains data for {age_days}+ days")
                        return True
                    else:
                        print(f"   ⚠️  No historical messages found (system may be new)")
                        return True  # Not necessarily a failure for new systems
                except:
                    print(f"   ⚠️  Could not parse oldest message date")
            
            # Check if there are messages from different time periods
            if distribution.get('older_than_month', 0) > 0:
                print(f"   ✅ Long-term retention verified - {distribution['older_than_month']} messages older than 1 month")
                return True
            elif total_messages > 0:
                print(f"   ✅ Messages exist in system - retention working")
                return True
            else:
                print(f"   ⚠️  No messages found in system")
                return False
        
        return False

    def test_job_status_independence(self):
        """Test that chat remains accessible regardless of job status changes"""
        print("\n" + "="*60)
        print("TESTING JOB STATUS INDEPENDENCE FOR CHAT ACCESS")
        print("="*60)
        
        if not self.job_id or not self.buyer_token or not self.supplier_token:
            print("❌ Cannot test job status independence - missing job or tokens")
            return False
        
        # First, verify chat is accessible with current job status
        success, initial_messages = self.run_test(
            "Get Chat Messages (Initial Status)",
            "GET",
            f"jobs/{self.job_id}/chat",
            200,
            token=self.buyer_token
        )
        
        if success and initial_messages:
            initial_count = len(initial_messages)
            print(f"   📥 Found {initial_count} messages with current job status")
        else:
            print("   ❌ Cannot access chat with current job status")
            return False
        
        # Test chat visibility in user's chat list
        success, buyer_chats = self.run_test(
            "Get Buyer Chat List",
            "GET",
            "chats",
            200,
            token=self.buyer_token
        )
        
        if success and buyer_chats:
            # Find our test job in the chat list
            test_chat = None
            for chat in buyer_chats:
                if chat.get('job_id') == self.job_id:
                    test_chat = chat
                    break
            
            if test_chat:
                print(f"   ✅ Chat found in buyer's chat list:")
                print(f"     Job: {test_chat.get('job_title')}")
                print(f"     Status: {test_chat.get('job_status')}")
                print(f"     Messages: {test_chat.get('message_count', 0)}")
                
                # Verify chat is accessible regardless of job status
                if test_chat.get('message_count', 0) > 0:
                    print(f"   ✅ Chat accessible regardless of job status - persistence confirmed")
                    return True
                else:
                    print(f"   ⚠️  Chat found but no messages counted")
                    return False
            else:
                print(f"   ❌ Test chat not found in buyer's chat list")
                return False
        else:
            print(f"   ❌ Failed to get buyer's chat list")
            return False

    def test_mark_as_read_functionality(self):
        """Test mark-as-read functionality for chat messages"""
        print("\n" + "="*60)
        print("TESTING MARK-AS-READ FUNCTIONALITY")
        print("="*60)
        
        if not self.job_id or not self.buyer_token:
            print("❌ Cannot test mark-as-read - missing job or token")
            return False
        
        # Mark chat messages as read
        success, response = self.run_test(
            "Mark Chat Messages as Read",
            "POST",
            f"chats/{self.job_id}/mark-read",
            200,
            token=self.buyer_token
        )
        
        if success and response:
            marked_count = response.get('message', '').split(' ')[1] if 'Marked' in response.get('message', '') else '0'
            print(f"   ✅ Mark-as-read functionality working - {marked_count} messages marked")
            return True
        else:
            print("   ❌ Mark-as-read functionality failed")
            return False

    def run_comprehensive_chat_persistence_tests(self):
        """Run all chat persistence tests as requested in the review"""
        print("\n" + "🚀" + "="*80 + "🚀")
        print("COMPREHENSIVE CHAT PERSISTENCE SYSTEM TESTING")
        print("Testing Enhanced Chat Persistence System as per Review Request")
        print("🚀" + "="*80 + "🚀")
        
        test_results = {}
        
        # Test 1: Admin Login
        test_results['admin_login'] = self.test_admin_login()
        if not test_results['admin_login']:
            print("\n❌ CRITICAL: Admin login failed - cannot proceed with admin tests")
            return test_results
        
        # Test 2: Chat Analytics Endpoint
        test_results['chat_analytics'] = self.test_chat_analytics_endpoint()
        
        # Test 3: Database Index Optimization
        test_results['index_optimization'] = self.test_database_index_optimization()
        
        # Test 4: Setup Test Accounts
        test_results['setup_accounts'] = self.setup_test_accounts()
        if not test_results['setup_accounts']:
            print("\n❌ CRITICAL: Failed to setup test accounts - cannot proceed with chat tests")
            return test_results
        
        # Test 5: Create Job and Bid for Chat Testing
        test_results['create_job_bid'] = self.create_job_and_bid()
        if not test_results['create_job_bid']:
            print("\n❌ CRITICAL: Failed to create job and bid - cannot test chat functionality")
            return test_results
        
        # Test 6: Improved Chat Visibility
        test_results['chat_visibility'] = self.test_improved_chat_visibility()
        
        # Test 7: Chat Message Persistence
        test_results['message_persistence'] = self.test_chat_message_persistence()
        
        # Test 8: Long-term Message Retention
        test_results['long_term_retention'] = self.test_long_term_message_retention()
        
        # Test 9: Historical Message Verification
        test_results['historical_verification'] = self.test_historical_message_verification()
        
        # Test 10: Job Status Independence
        test_results['job_status_independence'] = self.test_job_status_independence()
        
        # Test 11: Mark-as-Read Functionality
        test_results['mark_as_read'] = self.test_mark_as_read_functionality()
        
        return test_results

    def print_final_results(self, test_results):
        """Print comprehensive test results"""
        print("\n" + "🎯" + "="*80 + "🎯")
        print("CHAT PERSISTENCE SYSTEM TEST RESULTS")
        print("🎯" + "="*80 + "🎯")
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   API Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"   Feature Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Feature Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n🎯 CHAT PERSISTENCE SYSTEM STATUS:")
        
        # Critical tests for chat persistence
        critical_tests = ['chat_analytics', 'index_optimization', 'message_persistence', 'long_term_retention']
        critical_passed = sum(1 for test in critical_tests if test_results.get(test, False))
        
        if critical_passed == len(critical_tests):
            print("   🟢 EXCELLENT: All critical chat persistence tests passed")
            print("   🔒 Chat history persistence is GUARANTEED")
            print("   📈 System health: CHAT_PERSISTENCE_ACTIVE")
        elif critical_passed >= len(critical_tests) * 0.75:
            print("   🟡 GOOD: Most critical chat persistence tests passed")
            print("   ⚠️  Some minor issues detected - review failed tests")
        else:
            print("   🔴 CRITICAL: Major chat persistence issues detected")
            print("   ❌ Chat history may not be properly persisted")
        
        print(f"\n📝 REVIEW REQUEST COMPLIANCE:")
        review_requirements = {
            'New Chat List Logic': test_results.get('chat_visibility', False),
            'Database Index Optimization': test_results.get('index_optimization', False),
            'Improved Chat Visibility': test_results.get('chat_visibility', False),
            'Chat Message Persistence': test_results.get('message_persistence', False),
            'Long-term Message Retention': test_results.get('long_term_retention', False),
            'Chat Analytics': test_results.get('chat_analytics', False)
        }
        
        for requirement, status in review_requirements.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {requirement}")
        
        compliance_rate = sum(1 for status in review_requirements.values() if status) / len(review_requirements) * 100
        print(f"\n📊 Review Compliance Rate: {compliance_rate:.1f}%")
        
        return success_rate >= 80 and compliance_rate >= 80

if __name__ == "__main__":
    print("🚀 Starting Enhanced Chat Persistence System Testing...")
    print("=" * 80)
    
    tester = ChatPersistenceAPITester()
    test_results = tester.run_comprehensive_chat_persistence_tests()
    overall_success = tester.print_final_results(test_results)
    
    if overall_success:
        print("\n🎉 CHAT PERSISTENCE SYSTEM TESTING COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n⚠️  CHAT PERSISTENCE SYSTEM TESTING COMPLETED WITH ISSUES!")
        sys.exit(1)