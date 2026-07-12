from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["url_video_bot"]

users_col = db["users"]
channels_col = db["channels"]
sudo_col = db["sudo"]
settings_col = db["settings"]
downloads_col = db["downloads"]


async def init_db():
    await users_col.create_index("user_id", unique=True)
    await channels_col.create_index("chat_id", unique=True)
    await sudo_col.create_index("user_id", unique=True)
    await downloads_col.create_index("original_url")
    await downloads_col.create_index("user_id")
    await downloads_col.create_index("yuki_url")
