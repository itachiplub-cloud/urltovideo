from pyrogram import Client, filters
from pyrogram.types import Message
from database.users import add_user


@Client.on_message(filters.private & ~filters.command([
    "start", "stats", "users", "broadcast", "addsudo", "remsudo",
    "sudolist", "addchannel", "delchannel", "listchannels", "maintenance"
]))
async def track_user(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    await add_user(user_id, first_name)
