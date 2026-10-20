"""Настройки бота кастинга China Fashion Week 2027. Секреты — в .env."""

import os

from dotenv import load_dotenv

load_dotenv()


def _parse_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for part in raw.replace(";", ",").replace(" ", ",").split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            ids.append(int(part))
    return ids


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
# Кому приходят анкеты (Telegram ID через запятую)
ADMIN_CHAT_IDS: list[int] = _parse_ids(os.getenv("ADMIN_CHAT_ID", ""))
# Контакт для вопросов (необязательно)
CONTACT_INFO: str = os.getenv("CONTACT_INFO", "").strip()

EVENT_NAME = "China Fashion Week 2027"

# Разумные границы, чтобы отсеять опечатки (не требования кастинга)
AGE_MIN, AGE_MAX = 14, 60
HEIGHT_MIN, HEIGHT_MAX = 140, 210

CLOTHING_SIZES = ["XS (40)", "S (42)", "M (44)", "L (46)", "XL (48)"]

PHOTOS_MIN = 3
PHOTOS_MAX = 10

# Файл, где бот хранит черновики анкет и счётчик (переживает перезапуск)
PERSISTENCE_FILE = "bot_data.pickle"


def validate() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN — укажите токен от @BotFather в .env.")
    if not ADMIN_CHAT_IDS:
        raise RuntimeError("Не задан ADMIN_CHAT_ID — укажите ID получателей анкет в .env.")
