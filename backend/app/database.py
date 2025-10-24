from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def get_database():
    return db.client[settings.database_name]

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    db.client.close()
    print("❌ Closed MongoDB connection")

async def init_database():
    database = await get_database()
    
    # Tạo indexes
    await database.users.create_index("username", unique=True)
    await database.users.create_index("email", unique=True)
    await database.posts.create_index("user_id")
    await database.posts.create_index([("created_at", -1)])
    await database.posts.create_index("tags")
    await database.likes.create_index([("user_id", 1), ("post_id", 1)], unique=True)
    await database.comments.create_index("post_id")
    await database.comments.create_index("user_id")
    
    print("✅ Database indexes created")