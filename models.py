from typing import Dict, Optional

class ConfirmationState:
    """Состояние ожидания подтверждения воспроизведения фразы."""
    def __init__(self, phrase: str, filename: str, category: str):
        self.phrase = phrase
        self.filename = filename
        self.category = category

class WhiteList:
    """Управление белым списком пользователей."""
    def __init__(self):
        self.enabled = False
        self.allowed_users = set()

    def is_allowed(self, user_id: int) -> bool:
        if not self.enabled:
            return True
        return user_id in self.allowed_users

    def add(self, user_id: int):
        self.allowed_users.add(user_id)

    def remove(self, user_id: int):
        self.allowed_users.discard(user_id)

    def list(self):
        return self.allowed_users.copy()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False