from database import sudo_col


async def add_sudo(user_id: int):
    existing = await sudo_col.find_one({"user_id": user_id})
    if not existing:
        await sudo_col.insert_one({"user_id": user_id})


async def remove_sudo(user_id: int):
    await sudo_col.delete_one({"user_id": user_id})


async def is_sudo(user_id: int):
    return await sudo_col.find_one({"user_id": user_id}) is not None


async def get_all_sudo():
    return await sudo_col.find({}).to_list(100)
