import os
from gtts import gTTS
from .base import TTSProvider

class GoogleTTSProvider(TTSProvider):
    async def synthesize(self, text: str, output_path: str) -> bool:
        try:
            # gTTS синхронный, запускаем в потоке
            await asyncio.to_thread(self._synthesize_sync, text, output_path)
            return os.path.exists(output_path)
        except Exception as e:
            print(f"Google TTS ошибка: {e}")
            return False

    def _synthesize_sync(self, text: str, output_path: str):
        tts = gTTS(text=text, lang='ru')
        tts.save(output_path)