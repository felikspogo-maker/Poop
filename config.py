"""Конфигурация бота. Все значения читаются из переменных окружения (файл .env)."""

import os

from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int | None = None) -> int | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


# --- Обязательные настройки ---
# Токен бота, полученный у @BotFather
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

# --- Приём заявок ---
# ID чатов организаторов, куда бот пересылает готовые заявки.
# Можно указать несколько через запятую: ADMIN_CHAT_ID=111111,222222
# Узнать свой ID можно, написав боту @userinfobot.


def _parse_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for part in raw.replace(";", ",").replace(" ", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            continue
    return ids


ADMIN_CHAT_IDS: list[int] = _parse_ids(os.getenv("ADMIN_CHAT_ID", ""))

# --- Параметры конкурса ---
CONTEST_NAME = "Мисс и Миссис Россия Земля 2026"
DEADLINE = "10 сентября 2026"
FINAL_DATE = "26 сентября 2026"
FINAL_PLACE = "г. Москва, МТС Live — Театр на Цветном"
CONTACT = "@mrs_russia_earth"
INSTAGRAM_URL = "https://www.instagram.com/mrs_russia_earth/"
# Слово «директ» как ссылка на Instagram (для сообщений с parse_mode=HTML)
CONTACT_LINK = f'<a href="{INSTAGRAM_URL}">директ</a>'

# Ограничения анкеты
MIN_AGE = 14
MAX_AGE = 60
MIN_HEIGHT = 160
MIN_PHOTOS = 5
MAX_PHOTOS = 7

# --- Google Sheets (накопительная таблица участниц) ---
# Путь к файлу с ключом сервисного аккаунта Google
GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json").strip()
# ID таблицы (из ссылки .../spreadsheets/d/<ЭТОТ_ID>/edit)
GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "").strip()
# Название листа внутри таблицы
WORKSHEET_NAME: str = os.getenv("WORKSHEET_NAME", "Участницы").strip()


def validate() -> None:
    """Проверяет, что заданы обязательные настройки."""
    if not BOT_TOKEN:
        raise RuntimeError(
            "Не задан BOT_TOKEN. Создайте файл .env (см. .env.example) "
            "и укажите токен бота от @BotFather."
        )
    if not ADMIN_CHAT_IDS:
        raise RuntimeError(
            "Не задан ADMIN_CHAT_ID — некуда пересылать заявки. "
            "Узнайте свой ID у @userinfobot и укажите его в .env "
            "(несколько получателей — через запятую)."
        )
