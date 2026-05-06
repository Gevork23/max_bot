from typing import Optional
from max_api.client import MAXClient
from audio.player import AudioPlayer
from audio.manager import AudioFileManager
from keyboards import make_main_keyboard
from handlers.messages import confirmation_states
import os

async def handle_confirmation_response(
    text: str,
    user_id: int,
    chat_id: Optional[int],
    client: MAXClient,
    player: AudioPlayer
) -> bool:
    """Возвращает True, если это был ответ на подтверждение и он обработан."""
    if user_id not in confirmation_states:
        return False

    state = confirmation_states[user_id]
    if text == "✅ Я согласен":
        path = AudioFileManager.get_path(state.filename)
        if os.path.exists(path):
            await client.send_message(chat_id, user_id, f"🎵 Воспроизводится: {state.phrase}")
            if await player.play(path):
                await client.send_message(chat_id, user_id, "✅ Воспроизведение завершено")
            else:
                await client.send_message(chat_id, user_id, "❌ Ошибка воспроизведения")
        else:
            await client.send_message(chat_id, user_id, f"❌ Файл не найден: {state.filename}")
        del confirmation_states[user_id]
        await client.send_message(chat_id, user_id, "🏠 Главное меню:", attachments=make_main_keyboard())
        return True
    elif text == "❌ Отменить":
        await client.send_message(chat_id, user_id, "❌ Воспроизведение отменено")
        del confirmation_states[user_id]
        await client.send_message(chat_id, user_id, "🏠 Главное меню:", attachments=make_main_keyboard())
        return True
    elif text == "🏠 Главное меню":
        del confirmation_states[user_id]
        await client.send_message(chat_id, user_id, "🏠 Главное меню:", attachments=make_main_keyboard())
        return True
    return False