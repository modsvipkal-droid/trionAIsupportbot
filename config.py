import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("TRION_AI_BOT")

# Bot token validation
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is missing! Please set it in your .env file.")
    sys.exit(1)

# Support URL formatting
raw_support_url = os.getenv("SUPPORT_URL", "https://t.me/kal_mods").strip()
if raw_support_url.startswith("t.me/"):
    SUPPORT_URL = f"https://{raw_support_url}"
elif not raw_support_url.startswith("http"):
    SUPPORT_URL = f"https://t.me/{raw_support_url.lstrip('@')}"
else:
    SUPPORT_URL = raw_support_url

# Telegram Post references
GUIDE_CHAT_ID = os.getenv("GUIDE_CHAT_ID", "@postkalmoda").strip()
LOGIN_MESSAGE_ID = int(os.getenv("LOGIN_MESSAGE_ID", 11))
BUY_MESSAGE_ID = int(os.getenv("BUY_MESSAGE_ID", 13))
PLAY_MESSAGE_ID = int(os.getenv("PLAY_MESSAGE_ID", 14))

# Clean channel username for fallback web links
CLEAN_CHANNEL_NAME = GUIDE_CHAT_ID.lstrip("@")
