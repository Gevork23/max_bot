from abc import ABC, abstractmethod
from typing import List, Optional
import asyncio

class TTSProvider(ABC):
    """Абстрактный базовый класс для синтеза речи."""
    
    @abstractmethod
    async def synthesize(self, text: str, output_path: str) -> bool:
        """Синтезирует текст в аудиофайл. Возвращает True при успехе."""
        pass

    @abstractmethod
    async def get_supported_voices(self) -> List[dict]:
        """Возвращает список доступных голосов (для edge-tts)."""
        return []