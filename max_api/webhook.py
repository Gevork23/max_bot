import subprocess
import time
import requests
import sys
from typing import Tuple, Optional
import config

class NgrokManager:
    """Управление туннелем ngrok."""
    @staticmethod
    def start(port: int) -> Tuple[Optional[str], Optional[subprocess.Popen]]:
        """Запускает ngrok и возвращает (public_url, process)."""
        if not config.NGROK_AUTH_TOKEN:
            print("❌ NGROK_AUTH_TOKEN не найден")
            return None, None

        ngrok_cmd = ["ngrok", "http", str(port), "--authtoken", config.NGROK_AUTH_TOKEN]
        proc = subprocess.Popen(ngrok_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

        try:
            resp = requests.get("http://127.0.0.1:4040/api/tunnels")
            tunnels = resp.json().get("tunnels", [])
            for t in tunnels:
                if t.get("proto") == "https":
                    return t["public_url"], proc
        except Exception as e:
            print(f"Ошибка получения URL от ngrok: {e}")
        return None, proc