from typing import Optional
from max_api.client import MAXClient
from audio.manager import AudioFileManager
from audio.tts import TTSFactory
import config
from models import WhiteList
from keyboards import make_main_keyboard

async def cmd_start(client: MAXClient, chat_id: Optional[int], user_id: Optional[int]):
    missing = AudioFileManager.check_missing()
    if missing:
        msg = "⚠️ Отсутствуют файлы:\n"
        for display_name, filename in missing[:5]:
            msg += f"• {display_name} ({filename})\n"
        if len(missing) > 5:
            msg += f"... и ещё {len(missing)-5} файлов\n"
        await client.send_message(chat_id, user_id, msg)
    await client.send_message(chat_id, user_id, "📂 Выберите категорию:", attachments=make_main_keyboard())

async def cmd_check_files(client: MAXClient, chat_id: Optional[int], user_id: Optional[int]):
    missing = AudioFileManager.check_missing()
    if not missing:
        await client.send_message(chat_id, user_id, "✅ Все аудиофайлы присутствуют!")
        return
    text = "❌ Отсутствующие файлы:\n\n"
    for display_name, fname in missing:
        text += f"• {display_name}\n  Файл: {fname}\n\n"
    text += f"Всего отсутствует: {len(missing)}"
    await client.send_message(chat_id, user_id, text)

async def cmd_phrases(client: MAXClient, chat_id: Optional[int], user_id: Optional[int]):
    from constants import CATEGORIES, AUDIO_FILES_MAPPING
    import os, config
    text = "📋 Доступные фразы по категориям:\n\n"
    for category, phrases in CATEGORIES.items():
        text += f"{category}:\n"
        for phrase in phrases:
            fname = AUDIO_FILES_MAPPING.get(phrase, "")
            path = os.path.join(config.AUDIO_DIR, fname)
            status = "✅" if os.path.exists(path) else "❌"
            text += f"  • {phrase} {status}\n"
        text += "\n"
    await client.send_message(chat_id, user_id, text)

async def cmd_clean(client: MAXClient, chat_id: Optional[int], user_id: Optional[int]):
    cnt = AudioFileManager.cleanup_temp_files()
    await client.send_message(chat_id, user_id, f"✅ Удалено {cnt} временных файлов.")

async def cmd_myid(client: MAXClient, chat_id: Optional[int], user_id: Optional[int], sender_name: str, whitelist):
    status = "✅ Разрешен" if whitelist.is_allowed(user_id) else "❌ Запрещен"
    text = f"👤 Ваши данные:\nID: {user_id}\nИмя: {sender_name}\n📋 Статус доступа: {status}"
    await client.send_message(chat_id, user_id, text)

async def cmd_voices(client: MAXClient, chat_id: Optional[int], user_id: Optional[int], tts_provider):
    await client.send_message(chat_id, user_id, "Получаю список голосов...")
    voices = await tts_provider.get_supported_voices()
    if voices:
        lines = [f"{v['ShortName']} — {v['Locale']}" for v in voices[:200]]
        text = "\n".join(lines)
        if len(voices) > 200:
            text += f"\n...всего {len(voices)} голосов (показано 200)."
        await client.send_message(chat_id, user_id, text)
    else:
        await client.send_message(chat_id, user_id, "Не удалось получить список голосов.")

async def cmd_setvoice(client: MAXClient, chat_id: Optional[int], user_id: Optional[int], args: str, tts_provider):
    # args - строка после команды
    if not args:
        await client.send_message(chat_id, user_id, "Использование: /setvoice <ShortName>")
        return
    shortname = args.strip()
    voices = await tts_provider.get_supported_voices()
    for v in voices:
        if v.get("ShortName", "").lower() == shortname.lower():
            if hasattr(tts_provider, 'set_voice'):
                tts_provider.set_voice(v.get("ShortName"))
                await client.send_message(chat_id, user_id, f"✅ Голос установлен: {v['ShortName']}")
            else:
                await client.send_message(chat_id, user_id, "❌ Этот TTS движок не поддерживает смену голоса.")
            return
    await client.send_message(chat_id, user_id, "❌ Голос не найден. Сначала используйте /voices.")

async def cmd_test_tts(client: MAXClient, chat_id: Optional[int], user_id: Optional[int], tts_provider, audio_player):
    test_text = "Привет, это тест голосового синтеза."
    await client.send_message(chat_id, user_id, f"🧪 Тестирую TTS: '{test_text}'")
    # Генерация через TTS и воспроизведение – но это сложная логика, вынесем в tts_handler
    # Для простоты сейчас вызовем общую функцию, определённую в messages.py
    from handlers.messages import generate_and_play_tts
    await generate_and_play_tts(test_text, chat_id, user_id, client, tts_provider, audio_player)

# Импорт клавиатур из keyboards (временно)
from keyboards import make_main_keyboard