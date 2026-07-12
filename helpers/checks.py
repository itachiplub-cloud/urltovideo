import re
from config import OWNER_ID
from database.sudo import is_sudo


URL_PATTERN = re.compile(
    r'https?://(?:www\.)?[\w\-]+(\.[\w\-]+)+[/\w\-._~:/?#\[\]@!$&\'()*+,;=%]*'
)


def is_valid_url(text: str) -> bool:
    return bool(URL_PATTERN.match(text.strip()))


async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def is_authorized(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    return await is_sudo(user_id)
