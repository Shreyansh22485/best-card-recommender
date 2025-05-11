#!/usr/bin/env python
"""
Script to reset and recreate test data
"""
from pymongo import MongoClient
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")

def reset_database(confirm=True):
    """Delete all data in the database"""
    try:
        # Check if confirmation is needed
        if confirm:
            confirmation = input("This will DELETE ALL DATA in the database. Continue? (y/n): ")
            if confirmation.lower() != "y":
                print("Operation cancelled.")
                return False
        
        # Connect to MongoDB
        client = MongoClient(MONGODB_URL)
        db = client[MONGODB_DB_NAME]
        
        # Clear all collections
        db.users.delete_many({})
        db.preferences.delete_many({})
        db.statements.delete_many({})
        
        print("Database reset successfully.")
        print("Now run create_test_data.py to recreate test data.")
        return True
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    response = input("This will DELETE ALL DATA in the database. Continue? (y/n): ")
    if response.lower() == 'y':
        reset_database()
    else:
        print("Operation cancelled.")
