import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [int(os.environ.get("ADMIN_ID", "0"))]
DB_FILE = "data/database.json"
