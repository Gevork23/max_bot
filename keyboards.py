from constants import CATEGORIES

def make_main_keyboard():
    """Клавиатура главного меню (список категорий по 2 в ряд)."""
    buttons_rows = []
    row = []
    for cat in CATEGORIES.keys():
        row.append({"type": "message", "text": cat})
        if len(row) == 2:
            buttons_rows.append(row)
            row = []
    if row:
        buttons_rows.append(row)
    return [{
        "type": "inline_keyboard",
        "payload": {"buttons": buttons_rows}
    }]

def make_category_keyboard(category_name: str):
    """Клавиатура для конкретной категории (список фраз + кнопка назад)."""
    phrases = CATEGORIES.get(category_name, [])
    buttons_rows = []
    row = []
    for phrase in phrases:
        row.append({"type": "message", "text": phrase})
        if len(row) == 2:
            buttons_rows.append(row)
            row = []
    if row:
        buttons_rows.append(row)
    buttons_rows.append([{"type": "message", "text": "🏠 Главное меню"}])
    return [{
        "type": "inline_keyboard",
        "payload": {"buttons": buttons_rows}
    }]

def make_confirmation_keyboard():
    """Клавиатура для подтверждения воспроизведения."""
    return [{
        "type": "inline_keyboard",
        "payload": {
            "buttons": [
                [{"type": "message", "text": "✅ Я согласен"}, {"type": "message", "text": "❌ Отменить"}],
                [{"type": "message", "text": "🏠 Главное меню"}]
            ]
        }
    }]