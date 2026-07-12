import os
import re
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from config import MAX_FILE_SIZE, DOWNLOAD_DIR
from database.users import increment_downloads, get_user, set_verified
from database.channels import get_all_channels
from database.downloads import (
    get_download_by_url, save_download,
    update_telegram_file_id, update_yuki_url
)
from helpers.downloader import download_video, get_thumbnail
from helpers.yuki_storage import upload_file, get_file_url, delete_local_file
from helpers.utils import format_size
from helpers.buttons import get_force_sub_buttons

logger = logging.getLogger(__name__)

active_downloads = {}


def extract_url_from_message(message) -> str:
    """Extract URL from message text or caption."""
    text = message.text or message.caption or ""
    url_match = re.search(r'https?://[^\s]+', text)
    if url_match:
        return url_match.group().rstrip('.')
    return None


@Client.on_callback_query(filters.regex("^quality_"))
async def quality_handler(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data

    if user_id in active_downloads:
        await callback.answer("⚠️ Wait until your current download finishes.", show_alert=True)
        return

    if data == "quality_audio":
        height = 0
        format_name = "Audio MP3"
    else:
        height = int(data.replace("quality_", ""))
        format_name = f"{height}p"

    message = callback.message
    url = None

    if message.reply_to_message:
        url = extract_url_from_message(message.reply_to_message)

    if not url:
        url = extract_url_from_message(message)

    if not url:
        await callback.answer("❌ Could not find the URL.", show_alert=True)
        return

    channels = await get_all_channels()
    if channels:
        not_joined = []
        for ch in channels:
            try:
                member = await client.get_chat_member(ch["chat_id"], user_id)
                if member.status in ["left", "kicked"]:
                    not_joined.append(ch)
            except Exception:
                not_joined.append(ch)
        if not_joined:
            buttons = get_force_sub_buttons(not_joined)
            await callback.message.edit_text(
                "❌ You haven't joined all channels.\n\n"
                "Please join all channels and try again.",
                reply_markup=buttons
            )
            return

    active_downloads[user_id] = True
    file_path = None

    progress_msg = await message.reply(
        f"⬇️ Downloading {format_name}...\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"Please wait..."
    )

    try:
        cached = await get_download_by_url(url, user_id)

        if cached and cached.get("telegram_file_id"):
            try:
                await progress_msg.delete()
                if format_name == "Audio MP3":
                    await message.reply_cached_media(
                        cached["telegram_file_id"],
                        caption="🎵 Audio Download"
                    )
                else:
                    await message.reply_cached_media(
                        cached["telegram_file_id"],
                        caption="🎥 Video Download"
                    )
                await increment_downloads(user_id)
                return
            except Exception:
                pass

        if cached and cached.get("yuki_url"):
            try:
                await progress_msg.edit_text("⬇️ Downloading from cache...")
                import requests
                resp = requests.get(cached["yuki_url"], timeout=300, stream=True)
                resp.raise_for_status()

                from helpers.utils import sanitize_filename, generate_unique_id
                unique_id = generate_unique_id(user_id, url)
                ext = cached["yuki_url"].rsplit('.', 1)[-1].split('?')[0]
                if ext not in ['mp4', 'mkv', 'webm', 'mp3', 'm4a', 'opus', 'ogg', 'wav']:
                    ext = 'mp4'
                file_path = os.path.join(DOWNLOAD_DIR, str(user_id), f"{unique_id}_cache.{ext}")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)

                file_size = os.path.getsize(file_path)
                if file_size > MAX_FILE_SIZE:
                    await progress_msg.edit_text(
                        f"❌ File is too large to upload.\n\n"
                        f"📦 Size: {format_size(file_size)}\n"
                        f"📏 Limit: {format_size(MAX_FILE_SIZE)}"
                    )
                    delete_local_file(file_path)
                    return

                await progress_msg.edit_text("⚙️ Processing...")

                thumb_path = await get_thumbnail(url)

                await progress_msg.edit_text("📤 Uploading to Telegram...")
                telegram_file_id = None

                if file_path.endswith('.mp3'):
                    if thumb_path and os.path.exists(thumb_path):
                        msg = await message.reply_audio(
                            audio=file_path,
                            caption="🎵 Audio Download",
                            thumb=thumb_path,
                            title="Audio Download"
                        )
                    else:
                        msg = await message.reply_audio(
                            audio=file_path,
                            caption="🎵 Audio Download",
                            title="Audio Download"
                        )
                    if msg.audio:
                        telegram_file_id = msg.audio.file_id
                else:
                    if thumb_path and os.path.exists(thumb_path):
                        msg = await message.reply_video(
                            video=file_path,
                            caption="🎥 Video Download",
                            thumb=thumb_path,
                            supports_streaming=True
                        )
                    else:
                        msg = await message.reply_video(
                            video=file_path,
                            caption="🎥 Video Download",
                            supports_streaming=True
                        )
                    if msg.video:
                        telegram_file_id = msg.video.file_id

                await progress_msg.delete()
                await increment_downloads(user_id)

                if telegram_file_id:
                    await update_telegram_file_id(url, user_id, telegram_file_id)

                delete_local_file(file_path)
                if thumb_path and os.path.exists(thumb_path):
                    delete_local_file(thumb_path)
                return

            except Exception as e:
                logger.error(f"Cache download failed, falling back to yt-dlp: {e}")
                if file_path and os.path.exists(file_path):
                    delete_local_file(file_path)

        await progress_msg.edit_text(f"⬇️ Downloading {format_name}...")
        file_path = await download_video(url, height, user_id, f"download_{user_id}")

        if not os.path.exists(file_path):
            raise Exception("Downloaded file not found")

        file_size = os.path.getsize(file_path)

        if file_size > MAX_FILE_SIZE:
            await progress_msg.edit_text(
                f"❌ File is too large to upload.\n\n"
                f"📦 Size: {format_size(file_size)}\n"
                f"📏 Limit: {format_size(MAX_FILE_SIZE)}"
            )
            delete_local_file(file_path)
            return

        await progress_msg.edit_text("☁️ Uploading to Yuki Storage...")
        yuki_url = None
        try:
            response = upload_file(file_path)
            yuki_url = get_file_url(response)
            await update_yuki_url(url, user_id, yuki_url)
        except Exception as e:
            logger.warning(f"Yuki Storage upload failed: {e}")
            await progress_msg.edit_text(
                "⚠️ Storage upload failed.\nSending Telegram file only."
            )

        thumb_path = await get_thumbnail(url)

        await progress_msg.edit_text("📤 Uploading to Telegram...")
        telegram_file_id = None

        try:
            if file_path.endswith('.mp3'):
                caption = "🎵 Audio Download"
                if thumb_path and os.path.exists(thumb_path):
                    await progress_msg.delete()
                    msg = await message.reply_audio(
                        audio=file_path,
                        caption=caption,
                        thumb=thumb_path,
                        title="Audio Download"
                    )
                else:
                    await progress_msg.delete()
                    msg = await message.reply_audio(
                        audio=file_path,
                        caption=caption,
                        title="Audio Download"
                    )
                if msg.audio:
                    telegram_file_id = msg.audio.file_id
            else:
                caption = "🎥 Video Download"
                if thumb_path and os.path.exists(thumb_path):
                    await progress_msg.delete()
                    msg = await message.reply_video(
                        video=file_path,
                        caption=caption,
                        thumb=thumb_path,
                        supports_streaming=True
                    )
                else:
                    await progress_msg.delete()
                    msg = await message.reply_video(
                        video=file_path,
                        caption=caption,
                        supports_streaming=True
                    )
                if msg.video:
                    telegram_file_id = msg.video.file_id
        except Exception as e:
            logger.error(f"Telegram upload error: {e}")
            try:
                await progress_msg.edit_text(
                    f"❌ Failed to upload file.\nError: {str(e)[:300]}"
                )
            except Exception:
                pass

        await increment_downloads(user_id)

        record = await get_download_by_url(url, user_id)
        if not record:
            title = "Unknown"
            try:
                from helpers.downloader import extract_info
                info = await extract_info(url)
                title = info.get("title", "Unknown")
            except Exception:
                pass
            await save_download(
                user_id=user_id,
                original_url=url,
                title=title,
                telegram_file_id=telegram_file_id,
                yuki_url=yuki_url
            )
        else:
            if telegram_file_id:
                await update_telegram_file_id(url, user_id, telegram_file_id)

        delete_local_file(file_path)
        if thumb_path and os.path.exists(thumb_path):
            delete_local_file(thumb_path)

    except Exception as e:
        logger.error(f"Download error: {e}")
        try:
            await progress_msg.edit_text(f"❌ Download failed.\nError: {str(e)[:300]}")
        except Exception:
            pass

        if file_path and os.path.exists(file_path):
            delete_local_file(file_path)

    finally:
        active_downloads.pop(user_id, None)
