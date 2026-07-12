from pyrogram import Client, filters
from pyrogram.types import Message
from database.users import add_user
from database.channels import get_all_channels
from helpers.buttons import get_force_sub_buttons
from helpers.force_sub import check_force_sub


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"

    await add_user(user_id, first_name)

    is_subbed, channels = await check_force_sub(user_id)

    if not is_subbed and channels:
        text = (
            "🔒 Join all channels below to use this bot.\n\n"
            "You must join all channels and click Verify."
        )
        buttons = get_force_sub_buttons(channels)
        await message.reply(text, reply_markup=buttons)
        return

    await message.reply(
        f"👋 Hello {first_name}!\n\n"
        "Send me a video URL and I'll download it for you.\n\n"
        "🎥 Supported: YouTube, Instagram, TikTok, Twitter, Facebook, "
        "Reddit, Pinterest, Vimeo, Twitch, and many more!"
    )
