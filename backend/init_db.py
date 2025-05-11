#!/usr/bin/env python
"""
Initialize database indexes and validate the environment setup
"""
from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv
import sys

def init_db():
    """Initialize database indexes and collections"""
    load_dotenv()
    
    # Check environment variables
    required_env_vars = [
        "MONGODB_URL", 
        "MONGODB_DB_NAME", 
        "SECRET_KEY", 
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in the .env file")
        sys.exit(1)
    
    # Connect to MongoDB
    MONGODB_URL = os.getenv("MONGODB_URL")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
    
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Verify connection
        client.server_info()
        db = client[MONGODB_DB_NAME]
          # Create indexes
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.preferences.create_index([("user_id", ASCENDING)], unique=True)
        db.statements.create_index([("user_id", ASCENDING)])
        # Create a compound index for email_id and user_id to allow different users to parse the same email
        db.statements.create_index([("email_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
        
        print(f"Successfully connected to MongoDB: {MONGODB_URL}")
        print(f"Database '{MONGODB_DB_NAME}' is ready")
        
    except Exception as e:
        print(f"ERROR connecting to MongoDB: {e}")
        print("Please ensure MongoDB is running and the connection URL is correct")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
