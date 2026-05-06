import asyncio
import uvicorn
import sys
from max_api.webhook import NgrokManager
from max_api.client import MAXClient
from fastapi_app import app
import config
import httpx

async def setup_ngrok_and_subscription():
    """Запускает ngrok, создаёт подписку, возвращает URL."""
    public_url, proc = NgrokManager.start(config.NGROK_PORT)
    if not public_url:
        print("❌ Не удалось запустить ngrok")
        sys.exit(1)
    print(f"✅ Ngrok: {public_url}")

    async with httpx.AsyncClient() as client:
        max_cli = MAXClient(client)
        # Очистка старых подписок
        await max_cli.delete_all_subscriptions()
        # Создание новой
        webhook_url = public_url.rstrip("/") + "/webhook"
        ok = await max_cli.create_subscription(webhook_url, ["message_created", "bot_started"])
        if ok:
            print(f"✅ Подписка на {webhook_url} создана")
        else:
            print("❌ Не удалось создать подписку")
            proc.terminate()
            sys.exit(1)
    return proc

def main():
    if config.NGROK_AUTH_TOKEN:
        # Режим с ngrok (для разработки)
        ngrok_proc = asyncio.run(setup_ngrok_and_subscription())
        try:
            uvicorn.run(app, host="0.0.0.0", port=config.NGROK_PORT)
        except KeyboardInterrupt:
            pass
        finally:
            ngrok_proc.terminate()
    else:
        # Режим без ngrok (например, внутри Docker с известным публичным URL)
        uvicorn.run(app, host="0.0.0.0", port=config.NGROK_PORT)

if __name__ == "__main__":
    main()