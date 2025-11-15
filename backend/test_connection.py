"""
Test MongoDB connection with detailed diagnostics
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Your MongoDB connection string
MONGODB_URL = "mongodb+srv://thanhhieu53:phamthanhhieu53@cluster0.6ehiqh2.mongodb.net/?retryWrites=true&w=majority"

async def test_connection():
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    print()

    print("Step 1: Testing basic connectivity...")
    try:
        # Try with minimal settings first
        client = AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=10000
        )

        print("[OK] Client created")

        # Test ping
        print("\nStep 2: Pinging MongoDB...")
        result = await client.admin.command('ping')
        print(f"[OK] Ping successful: {result}")

        # List databases
        print("\nStep 3: Listing databases...")
        dbs = await client.list_database_names()
        print(f"[OK] Available databases: {dbs}")

        # Test specific database
        print("\nStep 4: Testing 'social_network_db'...")
        db = client['social_network_db']
        collections = await db.list_collection_names()
        print(f"[OK] Collections: {collections if collections else '(empty)'}")

        client.close()

        print("\n" + "=" * 60)
        print("SUCCESS! MongoDB connection is working perfectly!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}")
        print(f"Message: {e}")
        print()
        print("Troubleshooting tips:")
        print("  1. Check MongoDB Atlas cluster is running (not paused)")
        print("  2. Verify IP whitelist: 0.0.0.0/0 in Network Access")
        print("  3. Check username/password are correct")
        print("  4. Ensure internet connection is stable")
        print()

        # Try alternative connection
        print("Trying alternative connection method...")
        try:
            client2 = AsyncIOMotorClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=15000,
                tlsAllowInvalidCertificates=True
            )
            result = await client2.admin.command('ping')
            print(f"[OK] Alternative method worked: {result}")
            client2.close()

            print("\nRECOMMENDATION: Use tlsAllowInvalidCertificates=True in database.py")
            return True

        except Exception as e2:
            print(f"[ERROR] Alternative method also failed: {e2}")
            return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)
