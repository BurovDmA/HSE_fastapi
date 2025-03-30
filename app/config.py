import os

from dotenv import load_dotenv

load_dotenv()

FULL_URL = os.getenv("DB_FULL_LINK")