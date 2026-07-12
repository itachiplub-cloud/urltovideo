from database import channels_col


async def add_channel(chat_id: int, username: str, title: str):
    existing = await channels_col.find_one({"chat_id": chat_id})
    if existing:
        await channels_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"username": username, "title": title}}
        )
    else:
        invite_link = f"https://t.me/{username}" if username else ""
        await channels_col.insert_one({
            "chat_id": chat_id,
            "username": username,
            "title": title,
            "invite_link": invite_link
        })


async def remove_channel(chat_id: int):
    await channels_col.delete_one({"chat_id": chat_id})


async def get_channel_by_username(username: str):
    username = username.replace("@", "").replace("https://t.me/", "").strip("/")
    return await channels_col.find_one({"username": username})


async def get_all_channels():
    return await channels_col.find({}).to_list(100)


async def get_channel_count():
    return await channels_col.count_documents({})
