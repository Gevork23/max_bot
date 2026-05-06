import os
import edge_tts
from .base import TTSProvider
import config

class EdgeTTSProvider(TTSProvider):
    def __init__(self, voice: str = config.EDGE_VOICE):
        self.voice = voice

    async def synthesize(self, text: str, output_path: str) -> bool:
        try:
            communicate = edge_tts.Communicate(text=text, voice=self.voice)
            await communicate.save(output_path)
            return os.path.exists(output_path)
        except Exception as e:
            print(f"EdgeTTS ошибка: {e}")
            return False

    async def get_supported_voices(self):
        return await edge_tts.list_voices()

    def set_voice(self, voice: str):
        self.voice = voice