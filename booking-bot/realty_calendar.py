"""Интеграция с RealtyCalendar (автодобавление броней в календарь).

Пока API-токен не получен от поддержки RealtyCalendar, модуль работает как
заглушка: сообщает, что интеграция не настроена, и бронь уходит только
менеджеру в Telegram (менеджер вносит её в календарь вручную).

Когда токен появится:
  1. Впишите его в .env: RC_API_TOKEN=...
  2. Реализуйте create_booking() по документации RealtyCalendar
     (у них есть песочница и интерактивная документация API).
"""

import logging

import config

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(config.RC_API_TOKEN)


def create_booking(data: dict) -> bool:
    """Создаёт бронь в RealtyCalendar. Возвращает True при успехе.

    Пока не реализовано — ждём API-токен и документацию.
    """
    if not is_configured():
        logger.info("RealtyCalendar не настроен — бронь передана только менеджеру.")
        return False

    # TODO: реализовать вызов API RealtyCalendar, когда будет токен:
    #   POST https://api.realtycalendar.ru/... (создание брони)
    #   заголовок авторизации с RC_API_TOKEN, даты, объект, данные гостя.
    logger.warning("RealtyCalendar: create_booking ещё не реализован.")
    return False
