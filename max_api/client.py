import httpx
from typing import Optional, Dict, Any, List
import config

class MAXClient:
    """Клиент для работы с MAX API (отправка сообщений, подписки)."""
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.headers = {"Authorization": config.MAX_TOKEN, "Content-Type": "application/json"}

    async def send_message(
        self,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
        text: str = "",
        attachments: Optional[List[dict]] = None
    ) -> None:
        params = {}
        if chat_id is not None:
            params["chat_id"] = chat_id
        elif user_id is not None:
            params["user_id"] = user_id
        else:
            print("❌ send_message: нет chat_id и user_id")
            return

        print(f"📤 Отправка сообщения: {params}, text={text[:50]}...")
        body = {"text": text}
        if attachments:
            body["attachments"] = attachments

        try:
            r = await self.client.post(
                f"{config.MAX_API_BASE}/messages",
                headers=self.headers,
                params=params,
                json=body,
                timeout=40.0,
            )
            if r.status_code != 200:
                print(f"❌ Ошибка send_message: {r.status_code} {r.text}")
            else:
                print(f"✅ Сообщение отправлено (status {r.status_code})")
        except Exception as e:
            print(f"❌ Исключение в send_message: {e}")

    async def get_subscriptions(self) -> list:
        """Получить список текущих подписок."""
        r = await self.client.get(
            f"{config.MAX_API_BASE}/subscriptions",
            headers={"Authorization": config.MAX_TOKEN},
            timeout=20.0
        )
        if r.status_code == 200:
            return r.json().get("subscriptions", [])
        return []

    async def create_subscription(self, webhook_url: str, update_types: List[str]) -> bool:
        """Создать подписку на вебхук."""
        payload = {
            "url": webhook_url,
            "update_types": update_types
        }
        r = await self.client.post(
            f"{config.MAX_API_BASE}/subscriptions",
            headers=self.headers,
            json=payload,
            timeout=20.0
        )
        return r.status_code == 200

    async def delete_all_subscriptions(self):
        """Удаляет все подписки (используется при настройке ngrok)."""
        subs = await self.get_subscriptions()
        for sub in subs:
            url = sub.get("url")
            if not url:
                continue
            await self.client.delete(
                f"{config.MAX_API_BASE}/subscriptions?url={url}",
                headers={"Authorization": config.MAX_TOKEN},
                timeout=20.0
            )