import os
from constants import AUDIO_FILES_MAPPING
import config

class AudioFileManager:
    """Проверка наличия аудиофайлов и временные файлы."""
    
    @staticmethod
    def check_missing() -> list[tuple[str, str]]:
        """Возвращает список (название_фразы, имя_файла) для отсутствующих файлов."""
        missing = []
        for phrase, fname in AUDIO_FILES_MAPPING.items():
            path = os.path.join(config.AUDIO_DIR, fname)
            if not os.path.exists(path):
                missing.append((phrase, fname))
        return missing

    @staticmethod
    def get_path(filename: str) -> str:
        """Полный путь к файлу в AUDIO_DIR."""
        return os.path.join(config.AUDIO_DIR, filename)

    @staticmethod
    def cleanup_temp_files():
        """Удаляет временные файлы, начинающиеся с voice_ или tts_."""
        cnt = 0
        for f in os.listdir(config.AUDIO_DIR):
            if (f.startswith("voice_") or f.startswith("tts_")) and f.endswith((".mp3", ".wav", ".ogg")):
                try:
                    os.remove(os.path.join(config.AUDIO_DIR, f))
                    cnt += 1
                except:
                    pass
        return cnt