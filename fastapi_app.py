from fastapi import FastAPI, Request
import json
import traceback
import httpx
from contextlib import asynccontextmanager
from max_api.client import MAXClient
from audio.player import AudioPlayer
from audio.tts import TTSFactory
from models import WhiteList
from handlers.messages import process_text_message
from handlers.confirmation import handle_confirmation_response
import config

# Глобальные объекты
http_client = httpx.AsyncClient()
max_client = MAXClient(http_client)
player = AudioPlayer()
whitelist = WhiteList()
tts_provider = TTSFactory.create('ms')   # можно переключать через команду

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ Бот запускается")
    yield
    await http_client.aclose()
    print("👋 Завершение")

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🌐 {request.method} {request.url.path}")
    body = await request.body()
    if body:
        print(f"   Body: {body[:500]}")
    response = await call_next(request)
    print(f"🌐 Ответ: {response.status_code}")
    return response

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print(f"📨 Вебхук: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
        auto_play = data.get("auto_play", False)
        update = data.get("update", data)
        # Извлекаем message
        if update.get("update_type") == "message_created":
            message = update.get("message")
            if message:
                text = message.get("body", {}).get("text", "")
                sender = message.get("sender", {})
                user_id = sender.get("user_id")
                chat_id = message.get("recipient", {}).get("chat_id")
                sender_name = sender.get("name", "")
                # Сначала проверяем подтверждение
                if user_id and await handle_confirmation_response(text, user_id, chat_id, max_client, player):
                    return {"status": "ok"}
                # Иначе обычная обработка
                await process_text_message(
                    text, chat_id, user_id, sender_name,
                    max_client, whitelist, tts_provider, player, auto_play
                )
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Ошибка вебхука: {e}")
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}, 500