import os
from dotenv import load_dotenv

load_dotenv()

MAX_TOKEN = os.getenv("MAX_TOKEN")
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
AUDIO_DIR = os.getenv("AUDIO_DIR", "/app/audio_files/")
EDGE_VOICE = os.getenv("EDGE_VOICE", "ru-RU-DmitryNeural")
MAX_BOT_URL = os.getenv("MAX_BOT_URL", "https://max.ru/")
MAX_API_BASE = "https://platform-api.max.ru"
NGROK_PORT = int(os.getenv("NGROK_PORT", "8000"))

MAX_TOTAL_CHARS = int(os.getenv("MAX_TOTAL_CHARS", "4000"))
CHUNK_MAX = int(os.getenv("CHUNK_MAX", "300"))

if not MAX_TOKEN:
    raise ValueError("MAX_TOKEN не найден в .env")