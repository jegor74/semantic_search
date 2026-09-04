import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)

DATA_ROOT = PROJECT_ROOT / "data"
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/search",
)
