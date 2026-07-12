from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database.users import set_verified
from database.channels import get_all_channels
from helpers.buttons import get_force_sub_buttons


@Client.on_callback_query(filters.regex("^verify$"))
async def verify_handler(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    channels = await get_all_channels()

    if not channels:
        await callback.message.edit_text(
            f"✅ Verification Successful!\n\nNow send me your video URL."
        )
        return

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
        await callback.answer("❌ You haven't joined all channels.", show_alert=True)
        await callback.message.edit_text(
            "❌ You haven't joined all channels.\n\n"
            "Please join all channels and try again.",
            reply_markup=buttons
        )
        return

    await set_verified(user_id, True)

    await callback.message.edit_text(
        "✅ Verification Successful!\n\nNow send me your video URL."
    )
