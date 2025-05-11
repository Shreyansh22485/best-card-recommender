#!/usr/bin/env python
"""
Script to create sample data for testing
"""
from pymongo import MongoClient
from app.utils.auth import get_password_hash
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")

def create_test_data():
    # Connect to MongoDB
    client = MongoClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]
    
    # Clear existing data
    db.users.delete_many({})
    db.preferences.delete_many({})
    db.statements.delete_many({})
    
    # Get current UTC time using the modern approach
    now = datetime.now(timezone.utc)
    
    # Create a test user
    test_user = {
        "email": "test@example.com",
        "hashed_password": get_password_hash("password123"),
        "is_active": True,
        "created_at": now,
        "updated_at": now
    }
    
    user_id = db.users.insert_one(test_user).inserted_id
    
    print(f"Created test user with ID: {user_id}")
    print("Email: test@example.com")
    print("Password: password123")
    
    # Sample spending data for testing
    sample_spending = {
        "user_id": str(user_id),
        "preferences": {
            "preferred_categories": ["Dining", "Travel", "Entertainment"]
        },
        "created_at": now,
        "updated_at": now
    }
    
    # Insert preferences
    try:
        db.preferences.insert_one(sample_spending)
        print("Sample data created successfully!")
    except Exception as e:
        print(f"Error creating preferences: {e}")

if __name__ == "__main__":
    create_test_data()
