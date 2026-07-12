import time
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID, YUKI_API_URL
from helpers.checks import is_authorized
from database.users import get_user_count, get_total_downloads, get_all_users
from database.channels import get_all_channels, add_channel, remove_channel, get_channel_by_username, get_channel_count
from database.sudo import add_sudo, remove_sudo, get_all_sudo
from database.settings import get_maintenance, set_maintenance
from database.downloads import get_total_stored_files, get_total_uploads
from helpers.yuki_storage import check_api_status

bot_start_time = time.time()


@Client.on_message(filters.command("stats") & filters.private)
async def stats_handler(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        return

    user_count = await get_user_count()
    download_count = await get_total_downloads()
    channel_count = await get_channel_count()
    uptime = int(time.time() - bot_start_time)
    hours = uptime // 3600
    minutes = (uptime % 3600) // 60
    seconds = uptime % 60

    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    await message.reply(
        f"📊 **Bot Statistics**\n\n"
        f"👥 Total Users: {user_count}\n"
        f"📥 Total Downloads: {download_count}\n"
        f"📢 Total Channels: {channel_count}\n"
        f"⏱ Uptime: {hours}h {minutes}m {seconds}s\n\n"
        f"💻 CPU: {cpu}%\n"
        f"🧠 RAM: {memory}%"
    )


@Client.on_message(filters.command("users") & filters.private)
async def users_handler(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        return

    count = await get_user_count()
    await message.reply(f"👥 Total Users: {count}")


@Client.on_message(filters.command("addsudo") & filters.private)
async def addsudo_handler(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /addsudo user_id")
        return

    try:
        target_id = int(args[1])
    except ValueError:
        await message.reply("Invalid user ID.")
        return

    await add_sudo(target_id)
    await message.reply(f"✅ User `{target_id}` added as sudo.")


@Client.on_message(filters.command("remsudo") & filters.private)
async def remsudo_handler(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /remsudo user_id")
        return

    try:
        target_id = int(args[1])
    except ValueError:
        await message.reply("Invalid user ID.")
        return

    await remove_sudo(target_id)
    await message.reply(f"✅ User `{target_id}` removed from sudo.")


@Client.on_message(filters.command("sudolist") & filters.private)
async def sudolist_handler(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        return

    sudo_users = await get_all_sudo()
    if not sudo_users:
        await message.reply("No sudo users found.")
        return

    text = "👑 **Sudo Users:**\n\n"
    for s in sudo_users:
        text += f"• `{s['user_id']}`\n"

    await message.reply(text)


@Client.on_message(filters.command("addchannel") & filters.private)
async def addchannel_handler(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /addchannel @channel or /addchannel https://t.me/channel")
        return

    channel_input = args[1]

    if "t.me/" in channel_input:
        username = channel_input.split("t.me/")[-1].strip("/")
    elif channel_input.startswith("@"):
        username = channel_input[1:]
    else:
        username = channel_input

    try:
        chat = await client.get_chat(f"@{username}")
        member = await client.get_chat_member(chat.id, "me")

        if member.status not in ["administrator", "creator"]:
            await message.reply("❌ Bot must be admin in the channel.")
            return

        if not member.privileges or not member.privileges.can_invite_users:
            await message.reply("❌ Bot needs invite users permission.")
            return

        await add_channel(chat.id, username, chat.title)
        await message.reply(f"✅ Channel **{chat.title}** added successfully.")

    except Exception as e:
        await message.reply(f"❌ Error: {str(e)[:300]}")


@Client.on_message(filters.command("delchannel") & filters.private)
async def delchannel_handler(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /delchannel @channel")
        return

    channel_input = args[1]
    if channel_input.startswith("@"):
        username = channel_input[1:]
    elif "t.me/" in channel_input:
        username = channel_input.split("t.me/")[-1].strip("/")
    else:
        username = channel_input

    channel = await get_channel_by_username(username)
    if not channel:
        await message.reply("❌ Channel not found in database.")
        return

    await remove_channel(channel["chat_id"])
    await message.reply(f"✅ Channel **{channel.get('title', username)}** removed.")


@Client.on_message(filters.command("listchannels") & filters.private)
async def listchannels_handler(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        return

    channels = await get_all_channels()
    if not channels:
        await message.reply("No channels configured.")
        return

    text = "📢 **Force-Sub Channels:**\n\n"
    for ch in channels:
        text += f"• **{ch.get('title', 'Unknown')}** (@{ch.get('username', 'N/A')})\n"

    await message.reply(text)


@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.reply("Reply to a message to broadcast it.")
        return

    sent = 0
    failed = 0

    status = await message.reply("📢 Broadcasting...")

    async for user in await get_all_users():
        try:
            await message.reply_to_message.copy(user["user_id"])
            sent += 1
        except Exception:
            failed += 1

    await status.edit_text(
        f"📢 **Broadcast Complete**\n\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )


@Client.on_message(filters.command("maintenance") & filters.private)
async def maintenance_handler(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        current = await get_maintenance()
        await message.reply(f"Maintenance mode: {'ON' if current else 'OFF'}\nUsage: /maintenance on|off")
        return

    state = args[1].lower()
    if state == "on":
        await set_maintenance(True)
        await message.reply("✅ Maintenance mode ON.")
    elif state == "off":
        await set_maintenance(False)
        await message.reply("✅ Maintenance mode OFF.")
    else:
        await message.reply("Usage: /maintenance on|off")


@Client.on_message(filters.command("storage_stats") & filters.private)
async def storage_stats_handler(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        return

    stored_files = await get_total_stored_files()
    total_uploads = await get_total_uploads()

    api_online = check_api_status()
    api_status = "🟢 Online" if api_online else "🔴 Offline"
    api_url = YUKI_API_URL if YUKI_API_URL else "Not configured"

    await message.reply(
        f"☁️ **Yuki Storage Stats**\n\n"
        f"📁 Total Stored Files: {stored_files}\n"
        f"📥 Total Uploads: {total_uploads}\n"
        f"🌐 API Status: {api_status}\n"
        f"🔗 API URL: {api_url}"
    )
