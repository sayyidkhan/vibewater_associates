from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from .config import settings

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def connect_to_mongo():
    """Connect to MongoDB Atlas using the Python driver"""
    # Create client with ServerApi for MongoDB Atlas
    db.client = AsyncIOMotorClient(
        settings.mongodb_url,
        server_api=ServerApi('1')
    )
    
    # Test the connection
    try:
        await db.client.admin.command('ping')
        print("✓ Pinged MongoDB deployment. Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("✓ Closed MongoDB connection")

def get_database():
    """Get the database instance"""
    if db.client is None:
        raise Exception("Database not connected. Call connect_to_mongo() first.")
    return db.client[settings.database_name]
