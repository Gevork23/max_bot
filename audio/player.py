import os
import asyncio
import time
import subprocess
import pygame
from pydub import AudioSegment
import config

class AudioPlayer:
    """Воспроизведение аудиофайлов с fallback механизмами."""
    def __init__(self):
        self._initialized = self._init_pygame()

    def _init_pygame(self) -> bool:
        """Пытается инициализировать pygame.mixer с разными параметрами."""
        attempts = [
            lambda: pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096),
            lambda: pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=2048),
            lambda: pygame.mixer.init(),
            lambda: (os.environ.__setitem__('SDL_AUDIODRIVER', 'alsa'), pygame.mixer.quit(), pygame.mixer.init()),
            lambda: pygame.mixer.init(frequency=11025, size=-8, channels=1, buffer=1024),
        ]
        for i, attempt in enumerate(attempts):
            try:
                attempt()
                if pygame.mixer.get_init():
                    print(f"Аудио инициализировано (попытка {i+1})")
                    return True
            except Exception as e:
                print(f"Попытка {i+1} не удалась: {e}")
                time.sleep(0.5)
        print("Не удалось инициализировать pygame.mixer – будет использоваться mpg123")
        return False

    def play_sync(self, file_path: str) -> bool:
        """Синхронное воспроизведение (блокирующее)."""
        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
            return False

        if self._initialized:
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    time.sleep(0.1)
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                # ждём окончания
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                return True
            except Exception as e:
                print(f"Ошибка pygame: {e}")

        # Fallback через mpg123
        try:
            subprocess.run(['mpg123', '-q', file_path], check=True, timeout=30)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        # Попробовать другие плееры
        players = ['ffplay', 'paplay', 'aplay', 'play']
        for player in players:
            try:
                subprocess.Popen([player, file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # нет точного ожидания, просто даём время
                time.sleep(self._estimate_duration(file_path))
                return True
            except FileNotFoundError:
                continue
        return False

    async def play(self, file_path: str) -> bool:
        """Асинхронное воспроизведение с ожиданием."""
        ok = await asyncio.to_thread(self.play_sync, file_path)
        return ok

    def _estimate_duration(self, file_path: str) -> float:
        """Примерная длительность в секундах."""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0
        except:
            return 10.0  # fallback