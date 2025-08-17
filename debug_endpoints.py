import requests
import json

def test_specific_endpoints():
    """Test the specific failing endpoints with detailed error analysis"""
    base_url = "https://construct-connect.preview.emergentagent.com/api"
    
    # First, let's login as admin to get a token
    admin_login = {
        "email": "mohammadjalaluddin1027@gmail.com",
        "password": "5968474644j"
    }
    
    print("🔍 Testing admin login...")
    response = requests.post(f"{base_url}/auth/login", json=admin_login)
    if response.status_code == 200:
        admin_token = response.json()['access_token']
        print("✅ Admin login successful")
        
        # Test admin bids endpoint (this works)
        print("\n🔍 Testing admin bids endpoint...")
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = requests.get(f"{base_url}/admin/bids", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            bids = response.json()
            print(f"Found {len(bids)} bids")
            if bids:
                print("First bid keys:", list(bids[0].keys()))
                # Check for ObjectId issues
                for key, value in bids[0].items():
                    if str(value).startswith('ObjectId('):
                        print(f"⚠️  ObjectId found in {key}: {value}")
        else:
            print(f"Error: {response.text}")
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        return
    
    # Now let's create a test scenario and see the raw error
    print("\n🔍 Creating test scenario...")
    
    # Create buyer
    buyer_data = {
        "email": f"debug_buyer_{int(__import__('time').time())}@test.com",
        "password": "TestPass123!",
        "company_name": "Debug Buyer Co",
        "contact_phone": "+91-9876543210",
        "role": "buyer"
    }
    
    response = requests.post(f"{base_url}/auth/register", json=buyer_data)
    if response.status_code == 200:
        buyer_token = response.json()['access_token']
        buyer_id = response.json()['user']['id']
        print(f"✅ Buyer created: {buyer_id}")
        
        # Create supplier
        supplier_data = {
            "email": f"debug_supplier_{int(__import__('time').time())}@test.com",
            "password": "TestPass123!",
            "company_name": "Debug Supplier Co",
            "contact_phone": "+91-9876543211",
            "role": "supplier"
        }
        
        response = requests.post(f"{base_url}/auth/register", json=supplier_data)
        if response.status_code == 200:
            supplier_token = response.json()['access_token']
            supplier_id = response.json()['user']['id']
            print(f"✅ Supplier created: {supplier_id}")
            
            # Create job
            job_data = {
                "title": "Debug Test Job",
                "category": "material",
                "description": "Debug job for testing",
                "location": "Mumbai",
                "delivery_timeline": "1 week"
            }
            
            headers = {'Authorization': f'Bearer {buyer_token}'}
            response = requests.post(f"{base_url}/jobs", json=job_data, headers=headers)
            if response.status_code == 200:
                job_id = response.json()['id']
                print(f"✅ Job created: {job_id}")
                
                # Create bid
                bid_data = {
                    "price_quote": 100000.0,
                    "delivery_estimate": "5 days",
                    "notes": "Debug bid"
                }
                
                headers = {'Authorization': f'Bearer {supplier_token}'}
                response = requests.post(f"{base_url}/jobs/{job_id}/bids", json=bid_data, headers=headers)
                if response.status_code == 200:
                    bid_id = response.json()['id']
                    print(f"✅ Bid created: {bid_id}")
                    
                    # Now test the failing endpoints
                    print("\n🔍 Testing GET /jobs/{job_id}/bids (buyer view)...")
                    headers = {'Authorization': f'Bearer {buyer_token}'}
                    response = requests.get(f"{base_url}/jobs/{job_id}/bids", headers=headers)
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    
                    print("\n🔍 Testing GET /bids/my (supplier view)...")
                    headers = {'Authorization': f'Bearer {supplier_token}'}
                    response = requests.get(f"{base_url}/bids/my", headers=headers)
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    
                else:
                    print(f"❌ Bid creation failed: {response.status_code} - {response.text}")
            else:
                print(f"❌ Job creation failed: {response.status_code} - {response.text}")
        else:
            print(f"❌ Supplier creation failed: {response.status_code} - {response.text}")
    else:
        print(f"❌ Buyer creation failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_specific_endpoints()