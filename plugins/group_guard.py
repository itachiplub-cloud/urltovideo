import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_TOKEN


@Client.on_message(filters.group & ~filters.service)
async def group_guard(client: Client, message: Message):
    try:
        await message.reply(
            "❌ This bot works only in private messages.",
            reply_markup=None
        )

        btn_text = "📩 Open Bot"
        bot_username = (await client.get_me()).username
        btn_url = f"https://t.me/{bot_username}?start=start"

        from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(btn_text, url=btn_url)]
        ])

        await message.reply(
            "❌ This bot works only in private messages.",
            reply_markup=markup
        )

        await asyncio.sleep(5)

        await client.leave_chat(message.chat.id)

    except Exception:
        pass
