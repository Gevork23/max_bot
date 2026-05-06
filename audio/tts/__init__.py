from .base import TTSProvider
from .edge_tts import EdgeTTSProvider
from .google_tts import GoogleTTSProvider

class TTSFactory:
    @staticmethod
    def create(engine: str) -> TTSProvider:
        if engine == 'ms':
            return EdgeTTSProvider()
        elif engine == 'google':
            return GoogleTTSProvider()
        else:
            raise ValueError(f"Неизвестный TTS движок: {engine}")