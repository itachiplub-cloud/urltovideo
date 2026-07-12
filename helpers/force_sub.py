from database.channels import get_all_channels
from database.users import get_user, set_verified


async def check_force_sub(user_id: int) -> tuple[bool, list]:
    channels = await get_all_channels()
    if not channels:
        return True, []

    user = await get_user(user_id)
    if user and user.get("verified"):
        return True, channels

    return False, channels


async def mark_verified(user_id: int):
    await set_verified(user_id, True)
