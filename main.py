import os
import sys
import logging
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
from database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/error.log", mode="a")
    ]
)
logger = logging.getLogger(__name__)

app = Client(
    "url_video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
)


async def main():
    await init_db()
    logger.info("Database initialized.")
    await app.start()
    bot_info = await app.get_me()
    logger.info(f"Bot started: @{bot_info.username}")
    await idle()
    await app.stop()
    logger.info("Bot stopped.")


if __name__ == "__main__":
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        logger.error("Missing required environment variables. Check .env file.")
        sys.exit(1)

    from pyrogram import asyncio as pyrogram_asyncio
    pyrogram_asyncio.run(main())
