from database import db

downloads_col = db["downloads"]


async def save_download(
    user_id: int,
    original_url: str,
    title: str,
    telegram_file_id: str = None,
    yuki_url: str = None
):
    """Save a download record."""
    from datetime import datetime
    doc = {
        "user_id": user_id,
        "original_url": original_url,
        "title": title,
        "telegram_file_id": telegram_file_id,
        "yuki_url": yuki_url,
        "uploaded_at": datetime.utcnow()
    }
    await downloads_col.insert_one(doc)


async def get_download_by_url(original_url: str, user_id: int = None):
    """Find a download record by original URL."""
    query = {"original_url": original_url}
    if user_id:
        query["user_id"] = user_id
    return await downloads_col.find_one(query)


async def get_download_by_yuki_url(yuki_url: str):
    """Find a download record by Yuki URL."""
    return await downloads_col.find_one({"yuki_url": yuki_url})


async def update_telegram_file_id(original_url: str, user_id: int, telegram_file_id: str):
    """Update the telegram file_id for a download."""
    await downloads_col.update_one(
        {"original_url": original_url, "user_id": user_id},
        {"$set": {"telegram_file_id": telegram_file_id}}
    )


async def update_yuki_url(original_url: str, user_id: int, yuki_url: str):
    """Update the Yuki URL for a download."""
    await downloads_col.update_one(
        {"original_url": original_url, "user_id": user_id},
        {"$set": {"yuki_url": yuki_url}}
    )


async def get_total_stored_files():
    """Count distinct files that have a Yuki URL."""
    return await downloads_col.count_documents({"yuki_url": {"$ne": None}})


async def get_total_uploads():
    """Count total download records."""
    return await downloads_col.count_documents({})


async def init_downloads_db():
    """Create indexes for downloads collection."""
    await downloads_col.create_index("original_url")
    await downloads_col.create_index("user_id")
    await downloads_col.create_index("yuki_url")
