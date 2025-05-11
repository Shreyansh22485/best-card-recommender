#!/usr/bin/env python
"""
Test script to verify authentication is working correctly
"""
import requests
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import sys
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
API_URL = "https://localhost:8000"

def test_auth():
    """Test authentication flow"""
    
    # Test user credentials
    email = "test@example.com"
    password = "password123"
    
    print(f"Testing authentication for user: {email}")
    
    # Try to login
    print("\nTesting login...")
    try:
        response = requests.post(
            f"{API_URL}/api/auth/token", 
            data={
                "username": email,
                "password": password
            },
            verify=False  # Skip SSL verification for self-signed certificate
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print(f"Access token: {token_data['access_token'][:20]}...")
            
            # Test token by accessing a protected endpoint
            print("\nTesting token with /api/auth/me endpoint...")
            me_response = requests.get(
                f"{API_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
                verify=False
            )
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print("✅ Token is valid!")
                print(f"User data: {json.dumps(user_data, indent=2)}")
            else:
                print(f"❌ Token validation failed: {me_response.status_code}")
                print(me_response.text)
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            
            # Examine the user in the database
            print("\nExamining user in database...")
            client = MongoClient(MONGODB_URL)
            db = client[MONGODB_DB_NAME]
            user = db.users.find_one({"email": email})
            
            if user:
                print(f"User found in database with ID: {user['_id']}")
                print(f"Password hash: {user['hashed_password'][:20]}...")
            else:
                print("User not found in database.")
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("=== Authentication Test ===")
    success = test_auth()
    if success:
        print("\n✅ All tests completed.")
    else:
        print("\n❌ Tests failed.")
        sys.exit(1)
