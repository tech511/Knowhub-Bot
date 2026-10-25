from motor.motor_asyncio import AsyncIOMotorClient
from config import DATABASE_URL, DATABASE_NAME

client = None
db = None


async def connect_mongo():
    global client, db
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing. Configure MongoDB Atlas connection string.")
    client = AsyncIOMotorClient(DATABASE_URL, serverSelectionTimeoutMS=10000)
    await client.admin.command("ping")
    db = client[DATABASE_NAME]
    await db.entries.create_index([("scope_id", 1), ("status", 1), ("created_at", -1)])
    await db.entries.create_index([("owner_id", 1), ("created_at", -1)])
    await db.entries.create_index([("title", "text"), ("content", "text"), ("tags", "text")])
    await db.entries.create_index([("entry_id", 1)], unique=True)
    await db.communities.create_index([("chat_id", 1)], unique=True)


def get_db():
    if db is None:
        raise RuntimeError("MongoDB is not connected.")
    return db


async def close_mongo():
    if client is not None:
        client.close()
