from database import settings_col


async def get_maintenance():
    setting = await settings_col.find_one({"_id": "maintenance"})
    if setting:
        return setting.get("value", False)
    return False


async def set_maintenance(value: bool):
    await settings_col.update_one(
        {"_id": "maintenance"},
        {"$set": {"value": value}},
        upsert=True
    )
