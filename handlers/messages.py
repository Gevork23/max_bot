import os
import time
import asyncio
from typing import Optional
from max_api.client import MAXClient
from audio.player import AudioPlayer
from audio.tts.base import TTSProvider
from audio.manager import AudioFileManager
from constants import AUDIO_TEXTS, AUDIO_FILES_MAPPING, CATEGORIES
from utils import split_text_to_chunks, truncate_text
from keyboards import make_category_keyboard, make_main_keyboard, make_confirmation_keyboard
from models import ConfirmationState
import config
from handlers.commands import (
    cmd_start, cmd_check_files, cmd_phrases, cmd_clean,
    cmd_myid, cmd_voices, cmd_setvoice, cmd_test_tts
)

# Глобальный словарь для состояний подтверждения (можно перенести в models и менеджер)
confirmation_states = {}

async def generate_and_play_tts(
    text: str,
    chat_id: Optional[int],
    user_id: Optional[int],
    client: MAXClient,
    tts: TTSProvider,
    player: AudioPlayer,
    prefix: str = "🔊"
):
    """Генерация и воспроизведение TTS с разбивкой на части."""
    truncated_text, was_truncated = truncate_text(text, config.MAX_TOTAL_CHARS)
    await client.send_message(chat_id, user_id, f"{prefix} Генерирую речь...")

    chunks = split_text_to_chunks(truncated_text, config.CHUNK_MAX)
    base = f"tts_{int(time.time()*1000)}"
    any_success = False

    for idx, chunk in enumerate(chunks, start=1):
        mp3_path = os.path.join(config.AUDIO_DIR, f"{base}_{idx}.mp3")
        await client.send_message(chat_id, user_id, f"🔄 Часть {idx}/{len(chunks)}...")
        ok = await tts.synthesize(chunk, mp3_path)
        if not ok:
            await client.send_message(chat_id, user_id, "❌ Ошибка синтеза")
            break
        ok = await player.play(mp3_path)
        if not ok:
            await client.send_message(chat_id, user_id, "❌ Ошибка воспроизведения")
            break
        any_success = True
        try:
            os.remove(mp3_path)
        except:
            pass

    if any_success:
        msg = "✅ Текст озвучен."
        if was_truncated:
            msg += f" (обрезан до {config.MAX_TOTAL_CHARS} симв.)"
        await client.send_message(chat_id, user_id, msg)
    else:
        await client.send_message(chat_id, user_id, "❌ Не удалось озвучить.")

async def handle_phrase_with_confirmation(
    phrase: str,
    chat_id: Optional[int],
    user_id: int,
    client: MAXClient,
    player: AudioPlayer,
    auto_play: bool = False
):
    """Обработка выбранной фразы: либо сразу воспроизвести, либо запросить подтверждение."""
    filename = AUDIO_FILES_MAPPING.get(phrase)
    if not filename:
        await client.send_message(chat_id, user_id, "❌ Фраза не найдена.")
        return

    if auto_play:
        path = AudioFileManager.get_path(filename)
        if os.path.exists(path):
            await client.send_message(chat_id, user_id, f"🎵 Воспроизводится: {phrase}")
            if await player.play(path):
                await client.send_message(chat_id, user_id, "✅ Готово")
            else:
                await client.send_message(chat_id, user_id, "❌ Ошибка воспроизведения")
        else:
            await client.send_message(chat_id, user_id, f"❌ Файл не найден: {filename}")
        return

    # Запрос подтверждения
    message_text = AUDIO_TEXTS.get(phrase, "Текст сообщения не найден")
    # Определяем категорию
    category = None
    for cat_name, phrases in CATEGORIES.items():
        if phrase in phrases:
            category = cat_name
            break
    confirmation_states[user_id] = ConfirmationState(phrase, filename, category or "Общее")
    await client.send_message(
        chat_id, user_id,
        f"📝 Полный текст аудио:\n\n{message_text}\n\n---\nДля воспроизведения нажмите '✅ Я согласен'",
        attachments=make_confirmation_keyboard()
    )

async def process_text_message(
    text: str,
    chat_id: Optional[int],
    user_id: int,
    sender_name: str,
    client: MAXClient,
    whitelist,
    tts_provider: TTSProvider,
    player: AudioPlayer,
    auto_play: bool = False
):
    """Основной маршрутизатор входящего текста."""
    print(f"🔍 process_text_message: text='{text}', chat_id={chat_id}, user_id={user_id}, auto_play={auto_play}")
    if not whitelist.is_allowed(user_id):
        await client.send_message(chat_id, user_id, "❌ Доступ запрещён. Обратитесь к администратору.")
        return

    # Обработка команд (можно вынести в отдельный диспетчер, но для YAGNI пока оставим здесь)
    cmd_map = {
        "/start": lambda: cmd_start(client, chat_id, user_id),
        "/menu": lambda: cmd_start(client, chat_id, user_id),
        "/check_files": lambda: cmd_check_files(client, chat_id, user_id),
        "/phrases": lambda: cmd_phrases(client, chat_id, user_id),
        "/clean": lambda: cmd_clean(client, chat_id, user_id),
        "/myid": lambda: cmd_myid(client, chat_id, user_id, sender_name, whitelist),
        "/voices": lambda: cmd_voices(client, chat_id, user_id, tts_provider),
        "/test_tts": lambda: cmd_test_tts(client, chat_id, user_id, tts_provider, player),
    }
    # Проверка длинных команд с аргументами
    if text.lower().startswith("/setvoice "):
        await cmd_setvoice(client, chat_id, user_id, text[10:], tts_provider)
        return
    if text.lower().startswith("/wl_on"):
        whitelist.enable()
        await client.send_message(chat_id, user_id, "🔐 Белый список ВКЛЮЧЕН.")
        return
    if text.lower().startswith("/wl_off"):
        whitelist.disable()
        await client.send_message(chat_id, user_id, "🔓 Белый список ВЫКЛЮЧЕН.")
        return
    if text.lower().startswith("/wl_list"):
        users = whitelist.list()
        if not users:
            await client.send_message(chat_id, user_id, "📋 Белый список пуст.")
        else:
            await client.send_message(chat_id, user_id, "📋 Белый список:\n" + "\n".join(str(uid) for uid in users))
        return
    if text.lower().startswith("/wl_add "):
        parts = text.split()
        if len(parts) < 2:
            await client.send_message(chat_id, user_id, "Использование: /wl_add <user_id>")
        else:
            try:
                uid = int(parts[1])
                whitelist.add(uid)
                await client.send_message(chat_id, user_id, f"✅ Добавлено: {uid}")
            except ValueError:
                await client.send_message(chat_id, user_id, "❌ user_id должен быть числом.")
        return
    if text.lower().startswith("/wl_del "):
        parts = text.split()
        if len(parts) < 2:
            await client.send_message(chat_id, user_id, "Использование: /wl_del <user_id>")
        else:
            try:
                uid = int(parts[1])
                whitelist.remove(uid)
                await client.send_message(chat_id, user_id, f"🗑️ Удалено: {uid}")
            except ValueError:
                await client.send_message(chat_id, user_id, "❌ user_id должен быть числом.")
        return
    if text.lower() in cmd_map:
        await cmd_map[text.lower()]()
        return

    # Навигация
    if text == "🏠 Главное меню":
        if user_id in confirmation_states:
            del confirmation_states[user_id]
        await client.send_message(chat_id, user_id, "📂 Главное меню:", attachments=make_main_keyboard())
        return

    # Нажата категория
    if text in CATEGORIES:
        if user_id in confirmation_states:
            del confirmation_states[user_id]
        await client.send_message(chat_id, user_id, f"📁 {text} — выберите фразу:", attachments=make_category_keyboard(text))
        return

    # Фраза из списка
    if text in AUDIO_FILES_MAPPING:
        await handle_phrase_with_confirmation(text, chat_id, user_id, client, player, auto_play)
        return

    # Любой другой текст → TTS
    await generate_and_play_tts(text, chat_id, user_id, client, tts_provider, player)