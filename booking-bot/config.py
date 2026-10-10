"""Конфигурация бота бронирования. Значения читаются из .env."""

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
# Токен бота от @BotFather
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

# ID личного чата Оксаны (менеджера), куда приходят брони и чеки.
# Узнать: написать @userinfobot.
OWNER_CHAT_ID: int | None = _get_int("OWNER_CHAT_ID")


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


# Кто может управлять фотографиями домиков (добавлять/удалять) — через запятую.
# Менеджер (OWNER_CHAT_ID) тоже всегда может.
ADMIN_IDS: list[int] = _parse_ids(os.getenv("ADMIN_IDS", ""))

# Файл, где хранятся фото домиков (их file_id в Telegram).
PHOTOS_FILE: str = os.getenv("PHOTOS_FILE", "house_photos.json").strip()


def admin_ids() -> set[int]:
    ids = set(ADMIN_IDS)
    if OWNER_CHAT_ID:
        ids.add(OWNER_CHAT_ID)
    return ids

# --- RealtyCalendar (появится позже) ---
# API-токен RealtyCalendar. Пока пусто — брони уходят только менеджеру,
# а в календарь их вносит менеджер вручную.
RC_API_TOKEN: str = os.getenv("RC_API_TOKEN", "").strip()

# --- Объект ---
GUESTHOUSE_NAME = "Гостевой дом A-Home"
ADDRESS = "Абхазия, г. Сухум, ул. Семерджиева, д. 21"
PHONE_FOR_GUESTS = "+7 940 903 15 06"
CHECKIN_TIME = "14:00"
CHECKOUT_TIME = "12:00"
TOTAL_HOUSES = 3

# --- Правила бронирования ---
MIN_NIGHTS = 2               # минимальный срок — от двух ночей
MAX_NIGHTS = 90             # разумный потолок, защита от опечаток в датах
MAX_GUESTS_PER_HOUSE = 4    # максимум гостей на один домик

# --- Реквизиты для предоплаты ---
PAYMENT_DETAILS = os.getenv("PAYMENT_DETAILS", "").strip() or (
    "💳 <b>Реквизиты для предоплаты</b>\n\n"
    "<b>Сбербанк</b> (Оксана К.):\n"
    "Карта: <code>2202 2083 8189 2083</code>\n"
    "СБП по номеру: <code>+7 928 850 82 32</code>\n\n"
    "<b>Т-Банк</b>:\n"
    "Карта: <code>2200 7001 2880 3912</code>\n"
    "СБП по номеру: <code>+7 940 903 15 06</code>"
)


def validate() -> None:
    """Проверяет обязательные настройки перед запуском."""
    if not BOT_TOKEN:
        raise RuntimeError(
            "Не задан BOT_TOKEN. Создайте файл .env (см. .env.example) "
            "и укажите токен бота от @BotFather."
        )
    if not OWNER_CHAT_ID:
        raise RuntimeError(
            "Не задан OWNER_CHAT_ID — некуда отправлять брони. "
            "Узнайте ID менеджера у @userinfobot и укажите его в .env."
        )
