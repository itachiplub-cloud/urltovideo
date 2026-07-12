import os
import time
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import MAX_FILE_SIZE
from database.users import get_user, increment_downloads, set_verified
from database.channels import get_all_channels
from helpers.checks import is_valid_url
from helpers.buttons import get_force_sub_buttons, get_quality_buttons
from helpers.downloader import extract_info, download_video, get_thumbnail
from helpers.utils import format_size, cleanup_dir
from helpers.progress import ProgressTracker

logger = logging.getLogger(__name__)

active_downloads = {}


@Client.on_message(filters.text & filters.private & ~filters.command(["start", "stats", "users", "broadcast", "addsudo", "remsudo", "sudolist", "addchannel", "delchannel", "listchannels", "maintenance", "storage_stats"]))
async def url_handler(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if not is_valid_url(text):
        return

    if user_id in active_downloads:
        await message.reply("⚠️ Wait until your current download finishes.")
        return

    channels = await get_all_channels()
    if channels:
        user = await get_user(user_id)
        needs_check = True
        if user and user.get("verified"):
            not_joined = []
            for ch in channels:
                try:
                    member = await client.get_chat_member(ch["chat_id"], user_id)
                    if member.status in ["left", "kicked"]:
                        not_joined.append(ch)
                except Exception:
                    not_joined.append(ch)
            if not not_joined:
                needs_check = False
            else:
                await set_verified(user_id, False)

        if needs_check:
            buttons = get_force_sub_buttons(channels)
            await message.reply(
                "🔒 Join all channels below to use this bot.\n\n"
                "You must join all channels and click Verify.",
                reply_markup=buttons
            )
            return

    status_msg = await message.reply("🔄 Extracting video information...")

    try:
        info = await extract_info(text)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)[:500]}")
        return

    title = info["title"]
    duration = info["duration_str"]
    uploader = info["uploader"]
    thumbnail_url = info["thumbnail"]
    qualities = info["qualities"]

    thumb_path = None
    if thumbnail_url:
        thumb_path = await get_thumbnail(text)

    quality_buttons = get_quality_buttons(qualities)

    caption = (
        f"🎬 **{title}**\n\n"
        f"⏱ Duration: {duration}\n"
        f"👤 Uploader: {uploader}\n\n"
        f"Choose format below."
    )

    try:
        if thumb_path and os.path.exists(thumb_path):
            await status_msg.delete()
            await message.reply_photo(
                photo=thumb_path,
                caption=caption,
                reply_markup=quality_buttons
            )
        else:
            await status_msg.edit_text(caption, reply_markup=quality_buttons)
    except Exception as e:
        await status_msg.edit_text(caption, reply_markup=quality_buttons)

    if thumb_path and os.path.exists(thumb_path):
        try:
            os.remove(thumb_path)
        except Exception:
            pass
