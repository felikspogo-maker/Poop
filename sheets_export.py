"""Накопительная таблица участниц в Google Sheets.

Каждая новая заявка дописывается отдельной строкой в облачную таблицу, так что
организаторы видят единый список всех участниц прямо в браузере.

Требуется сервисный аккаунт Google (файл с ключом) и доступ к таблице —
подробности в README.
"""

import logging
import os

import gspread
from google.oauth2.service_account import Credentials

import config

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Заголовки столбцов и соответствующие ключи из данных заявки
COLUMNS: list[tuple[str, str]] = [
    ("Дата заявки", "submitted_at"),
    ("ФИ", "name"),
    ("Город", "city"),
    ("Возраст", "age"),
    ("Рост, см", "height"),
    ("Семейное положение", "marital"),
    ("Категория", "category"),
    ("Телефон", "phone"),
    ("Опыт участия", "experience"),
    ("Фото, шт", "photos_count"),
    ("Telegram", "username"),
    ("Telegram ID", "telegram_id"),
    ("Согласие", "consent"),
]
HEADER = [title for title, _ in COLUMNS]

_worksheet = None  # кэш листа таблицы на время работы процесса


def is_configured() -> bool:
    """Google Sheets настроен, если задан ID таблицы и есть файл с ключом."""
    return bool(config.GOOGLE_SHEET_ID and os.path.exists(config.GOOGLE_CREDENTIALS_FILE))


def sheet_url() -> str:
    return f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEET_ID}"


def _get_worksheet():
    global _worksheet
    if _worksheet is not None:
        return _worksheet

    creds = Credentials.from_service_account_file(
        config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID)

    try:
        ws = spreadsheet.worksheet(config.WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(
            title=config.WORKSHEET_NAME, rows=1000, cols=len(COLUMNS)
        )

    # Добавляем строку заголовков, если лист пустой
    if not ws.acell("A1").value:
        ws.append_row(HEADER, value_input_option="USER_ENTERED")

    _worksheet = ws
    return ws


def append_participant(data: dict) -> bool:
    """Дописывает участницу в таблицу. Возвращает True при успехе."""
    if not is_configured():
        logger.warning("Google Sheets не настроен — участница не добавлена в таблицу.")
        return False

    try:
        ws = _get_worksheet()
        username = data.get("username")
        row = []
        for _, key in COLUMNS:
            if key == "username":
                row.append(f"@{username}" if username else "")
            else:
                row.append(data.get(key, ""))
        ws.append_row(row, value_input_option="USER_ENTERED")
        logger.info("Участница добавлена в Google-таблицу")
        return True
    except Exception:
        logger.exception("Не удалось добавить участницу в Google Sheets")
        # сбрасываем кэш — при следующей заявке попробуем переподключиться
        global _worksheet
        _worksheet = None
        return False
