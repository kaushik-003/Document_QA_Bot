from pymongo import MongoClient
from app.config import settings

_client = None
_db = None

def get_mongodb_client():
    """Get MongoDB client (singleton)"""
    global _client
    
    if _client is None:
        try:
            _client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            _client.admin.command('ping')
            print("MongoDB connected successfully")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            _client = None
    
    return _client

def get_database():
    """Get database instance"""
    global _db
    
    if _db is None:
        client = get_mongodb_client()
        if client is not None:
            _db = client[settings.MONGODB_DB_NAME]
    
    return _db

# Initialize collections
def get_documents_collection():
    """Get documents collection"""
    db = get_database()
    if db is not None:
        return db["documents"]
    return None

def get_chunks_collection():
    """Get chunks collection"""
    db = get_database()
    if db is not None:
        return db["chunks"]
    return None

# Test connection
if __name__ == "__main__":
    db = get_database()
    if db is not None:  # Fixed: Compare with None instead of using bool()
        print(f"Connected to database: {settings.MONGODB_DB_NAME}")
        try:
            collections = db.list_collection_names()
            print(f"Collections: {collections if collections else '(no collections yet)'}")
        except Exception as e:
            print(f"Error listing collections: {e}")
    else:
        print("Failed to connect to database")