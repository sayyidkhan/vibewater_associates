#!/usr/bin/env python3
"""
MongoDB Connection Test Script
Tests the MongoDB connection using the configuration from .env file
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    
    # Get MongoDB URL from environment
    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME", "vibewater_db")
    
    if not mongodb_url:
        print("❌ ERROR: MONGODB_URL not found in .env file")
        return False
    
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    print(f"Database Name: {database_name}")
    print(f"MongoDB URL: {mongodb_url[:30]}..." if len(mongodb_url) > 30 else f"MongoDB URL: {mongodb_url}")
    print("-" * 60)
    
    client = None
    try:
        # Create MongoDB client
        print("\n1. Creating MongoDB client...")
        client = AsyncIOMotorClient(
            mongodb_url,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        print("   ✓ Client created successfully")
        
        # Test connection with ping
        print("\n2. Testing connection with ping...")
        await client.admin.command('ping')
        print("   ✓ Ping successful - Connected to MongoDB!")
        
        # Get database
        print(f"\n3. Accessing database '{database_name}'...")
        db = client[database_name]
        print("   ✓ Database accessed")
        
        # List collections
        print("\n4. Listing collections...")
        collections = await db.list_collection_names()
        if collections:
            print(f"   ✓ Found {len(collections)} collection(s):")
            for collection in collections:
                print(f"     - {collection}")
        else:
            print("   ℹ No collections found (database might be empty)")
        
        # Test write operation (optional)
        print("\n5. Testing write operation...")
        test_collection = db["_connection_test"]
        test_doc = {"test": "connection", "timestamp": "test"}
        result = await test_collection.insert_one(test_doc)
        print(f"   ✓ Write test successful (inserted id: {result.inserted_id})")
        
        # Test read operation
        print("\n6. Testing read operation...")
        found_doc = await test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("   ✓ Read test successful")
        
        # Clean up test document
        print("\n7. Cleaning up test data...")
        await test_collection.delete_one({"_id": result.inserted_id})
        print("   ✓ Test data cleaned up")
        
        # Get server info
        print("\n8. Getting server information...")
        server_info = await client.server_info()
        print(f"   ✓ MongoDB Version: {server_info.get('version', 'Unknown')}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - MongoDB connection is working!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ CONNECTION FAILED")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("\nPossible issues:")
        print("  - Check if MONGODB_URL in .env is correct")
        print("  - Verify network connectivity")
        print("  - Ensure MongoDB Atlas IP whitelist includes your IP")
        print("  - Check if database credentials are valid")
        return False
        
    finally:
        if client:
            print("\n9. Closing connection...")
            client.close()
            print("   ✓ Connection closed")

def main():
    """Main entry point"""
    try:
        result = asyncio.run(test_mongodb_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
