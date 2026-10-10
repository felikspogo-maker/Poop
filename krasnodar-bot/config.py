"""Настройки бота «Мисс и Миссис Краснодарский край 2027». Секреты — в .env."""

import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()


def _parse_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for part in raw.replace(";", ",").replace(" ", ",").split(","):
        part = part.strip()
        if part:
            try:
                ids.append(int(part))
            except ValueError:
                continue
    return ids


# --- Обязательные настройки ---
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

# Кому приходят анкеты (Telegram ID через запятую). Узнать ID — @userinfobot.
ADMIN_CHAT_IDS: list[int] = _parse_ids(os.getenv("ADMIN_CHAT_ID", ""))

# --- Google-таблица (необязательно) ---
GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json").strip()
GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "").strip()
WORKSHEET_NAME: str = os.getenv("WORKSHEET_NAME", "Участницы").strip()

# Контакт для вопросов (показывается участницам). Например: @orgname или телефон.
CONTACT_INFO: str = os.getenv("CONTACT_INFO", "").strip()

# --- Параметры конкурса ---
CONTEST_NAME = "Мисс и Миссис Краснодарский край 2027"
DEADLINE = date(2027, 1, 15)          # последний день приёма анкет (включительно)
DEADLINE_TEXT = "15 января 2027"

# Категории: (название, мин. возраст, макс. возраст)
CATEGORIES: list[tuple[str, int, int]] = [
    ("Юная Мисс", 14, 17),
    ("Мисс", 18, 35),
    ("Миссис", 20, 45),
]
MIN_AGE = min(c[1] for c in CATEGORIES)
MAX_AGE = max(c[2] for c in CATEGORIES)

MIN_HEIGHT = 165
CLOTHING_SIZES = ["40", "42", "44", "46"]
MARITAL_OPTIONS = ["Не замужем", "Замужем", "Разведена"]

# Сколько фото/видео прислать (в любом сочетании: можно только фото,
# можно часть заменить видео)
MEDIA_REQUIRED = 5


def categories_for_age(age: int) -> list[str]:
    return [name for name, lo, hi in CATEGORIES if lo <= age <= hi]


def validate() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN — укажите токен от @BotFather в .env.")
    if not ADMIN_CHAT_IDS:
        raise RuntimeError(
            "Не задан ADMIN_CHAT_ID — некуда отправлять анкеты. "
            "Укажите ID получателей через запятую в .env."
        )
