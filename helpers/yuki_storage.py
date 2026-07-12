import os
import logging
import requests
from config import YUKI_API_URL, YUKI_UPLOAD_ENDPOINT

logger = logging.getLogger(__name__)


def upload_file(file_path: str) -> dict:
    """Upload file to Yuki Storage. Returns dict with 'url' key or raises."""
    if not YUKI_API_URL or not YUKI_UPLOAD_ENDPOINT:
        raise Exception("Yuki Storage not configured")

    if not os.path.exists(file_path):
        raise Exception(f"File not found: {file_path}")

    url = f"{YUKI_API_URL}{YUKI_UPLOAD_ENDPOINT}"
    timeout = 300

    with open(file_path, "rb") as f:
        response = requests.post(
            url,
            files={"file": f},
            timeout=timeout
        )

    response.raise_for_status()
    return response.json()


def get_file_url(response: dict) -> str:
    """Extract URL from Yuki Storage response."""
    if not response:
        raise Exception("Empty response from Yuki Storage")

    url = response.get("url")
    if url:
        return url

    raise Exception("No URL in Yuki Storage response")


def delete_local_file(file_path: str) -> bool:
    """Delete a local file. Returns True if deleted."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete {file_path}: {e}")
        return False


def check_api_status() -> bool:
    """Check if Yuki Storage API is reachable."""
    if not YUKI_API_URL:
        return False
    try:
        response = requests.get(YUKI_API_URL, timeout=10)
        return response.status_code < 500
    except Exception:
        return False
