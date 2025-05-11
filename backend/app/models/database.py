from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")

client = MongoClient(MONGODB_URL)
db: Database = client[MONGODB_DB_NAME]

# Collections
users_collection: Collection = db.users
preferences_collection: Collection = db.preferences
statements_collection: Collection = db.statements
