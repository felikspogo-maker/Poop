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
# ID чата администратора/группы, куда бот пересылает готовые заявки.
# Можно узнать, написав боту @userinfobot. Для группы ID отрицательный.
ADMIN_CHAT_ID: int | None = _get_int("ADMIN_CHAT_ID")

# --- Отправка заявок на почту (необязательно) ---
# Если SMTP не настроен — заявки всё равно сохраняются и пересылаются админу.
TARGET_EMAIL: str = os.getenv("TARGET_EMAIL", "6408844@gmail.com").strip()
SMTP_HOST: str = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT: int = _get_int("SMTP_PORT", 587) or 587
SMTP_USER: str = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM: str = os.getenv("SMTP_FROM", SMTP_USER).strip()

# --- Параметры конкурса ---
CONTEST_NAME = "Мисс и Миссис Россия Земля 2026"
DEADLINE = "10 сентября 2026"
FINAL_DATE = "26 сентября 2026"
FINAL_PLACE = "г. Москва, МТС Live — Театр на Цветном"
CONTACT = "@mrs_russia_earth"

# Ограничения анкеты
MIN_AGE = 14
MAX_AGE = 60
MIN_HEIGHT = 160
MIN_PHOTOS = 5
MAX_PHOTOS = 7

# Куда складывать сохранённые заявки
SUBMISSIONS_DIR = os.getenv("SUBMISSIONS_DIR", "submissions").strip()


def validate() -> None:
    """Проверяет, что заданы обязательные настройки."""
    if not BOT_TOKEN:
        raise RuntimeError(
            "Не задан BOT_TOKEN. Создайте файл .env (см. .env.example) "
            "и укажите токен бота от @BotFather."
        )
