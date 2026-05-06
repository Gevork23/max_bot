from typing import List
import config

def split_text_to_chunks(text: str, max_len: int = config.CHUNK_MAX) -> List[str]:
    """Разбивает текст на части, не разрывая слова."""
    words = text.split()
    chunks = []
    cur = ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_len:
            cur += " " + w
        else:
            chunks.append(cur)
            cur = w
    if cur:
        chunks.append(cur)
    return chunks

def truncate_text(text: str, max_chars: int = config.MAX_TOTAL_CHARS) -> tuple[str, bool]:
    """Обрезает текст до max_chars символов, возвращает (обрезанный_текст, был_ли_обрез)."""
    if len(text) > max_chars:
        return text[:max_chars], True
    return text, False