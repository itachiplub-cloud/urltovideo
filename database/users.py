from database import users_col


async def add_user(user_id: int, first_name: str):
    existing = await users_col.find_one({"user_id": user_id})
    if not existing:
        await users_col.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "verified": False,
            "downloads": 0
        })
    else:
        await users_col.update_one(
            {"user_id": user_id},
            {"$set": {"first_name": first_name}}
        )


async def get_user(user_id: int):
    return await users_col.find_one({"user_id": user_id})


async def set_verified(user_id: int, verified: bool = True):
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {"verified": verified}}
    )


async def increment_downloads(user_id: int):
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"downloads": 1}}
    )


async def get_all_users():
    return users_col.find({})


async def get_user_count():
    return await users_col.count_documents({})


async def get_total_downloads():
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$downloads"}}}
    ]
    result = await users_col.aggregate(pipeline).to_list(1)
    if result:
        return result[0]["total"]
    return 0
