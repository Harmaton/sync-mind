"""
MongoDB Initialization Script for MindsDB Integration
- Ensures the 'mindscluster' database and 'orders' collection exist
- Inserts a dummy document if the collection is empty
"""
import os
from pymongo import MongoClient

# Load settings from environment variables
MONGO_USER = os.environ.get("MONGO_USERNAME", "mindsuser")
MONGO_PASS = os.environ.get("MONGO_PASSWORD", "")
MONGO_CLUSTER = os.environ.get("MONGO_CLUSTER_URL", "mindcluster.qhsxpfc.mongodb.net")
MONGO_DB = os.environ.get("MONGO_DATABASE", "mindscluster")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "orders")

uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_CLUSTER}/{MONGO_DB}"

print(f"Connecting to MongoDB with URI: {uri}")
client = MongoClient(uri)
db = client[MONGO_DB]

# Ensure collection exists
if MONGO_COLLECTION not in db.list_collection_names():
    db.create_collection(MONGO_COLLECTION)
    print(f"Created collection: {MONGO_COLLECTION}")
else:
    print(f"Collection {MONGO_COLLECTION} already exists.")

# Ensure collection is not empty
if db[MONGO_COLLECTION].count_documents({}) == 0:
    db[MONGO_COLLECTION].insert_one({"order_id": 1, "note": "Dummy order for MindsDB integration"})
    print(f"Inserted dummy document into {MONGO_COLLECTION}")
else:
    print(f"Collection {MONGO_COLLECTION} already has documents.")

print(f"MongoDB setup complete for {MONGO_DB}.{MONGO_COLLECTION}")
