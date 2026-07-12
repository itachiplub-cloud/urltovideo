from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_force_sub_buttons(channels: list) -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        title = ch.get("title", "Channel")
        username = ch.get("username", "")
        if username:
            link = f"https://t.me/{username}"
        else:
            link = ch.get("invite_link", "#")
        buttons.append([InlineKeyboardButton(f"📢 {title}", url=link)])
    buttons.append([InlineKeyboardButton("✅ Verify", callback_data="verify")])
    return InlineKeyboardMarkup(buttons)


def get_quality_buttons(qualities: list) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, q in enumerate(qualities):
        label = q["label"]
        callback = q["callback"]
        row.append(InlineKeyboardButton(label, callback_data=callback))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


def get_back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])
