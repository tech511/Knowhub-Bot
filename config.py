import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DATABASE_NAME = os.getenv("DATABASE_NAME", "knowhub").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "0") or "0")

MAX_TITLE_LENGTH = 120
MAX_CONTENT_LENGTH = 3500
PAGE_SIZE = 5
