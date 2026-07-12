import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
ERROR_LOG = os.path.join(LOG_DIR, "error.log")

YUKI_API_URL = os.getenv("YUKI_API_URL", "")
YUKI_UPLOAD_ENDPOINT = os.getenv("YUKI_UPLOAD_ENDPOINT", "/upload")

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
