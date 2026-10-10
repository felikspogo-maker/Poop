"""Сезонные цены и расчёт стоимости проживания.

Цена за ночь зависит от месяца, в который приходится эта ночь:
  • октябрь–май  — 2700 ₽
  • июнь–июль    — 3700 ₽
  • август       — 4200 ₽
  • сентябрь     — 3700 ₽

Итог считается по каждой ночи отдельно, поэтому заезды «на стыке сезонов»
считаются честно (часть ночей по одной цене, часть — по другой).
"""

from datetime import date, timedelta

SEASON_PRICES = {
    "октябрь–май": 2700,
    "июнь–июль": 3700,
    "август": 4200,
    "сентябрь": 3700,
}


def price_for_night(night: date) -> int:
    """Цена одной ночи (ночь датируется днём заезда в неё)."""
    month = night.month
    if month in (6, 7):
        return 3700
    if month == 8:
        return 4200
    if month == 9:
        return 3700
    return 2700  # октябрь–май


def nights_between(checkin: date, checkout: date) -> int:
    return (checkout - checkin).days


def calc_total(checkin: date, checkout: date, houses: int) -> int:
    """Полная стоимость проживания за все ночи и все домики."""
    total = 0
    night = checkin
    while night < checkout:
        total += price_for_night(night)
        night += timedelta(days=1)
    return total * houses


def calc_prepayment(checkin: date, houses: int) -> int:
    """Предоплата — одна ночь по сезону даты заезда, за каждый домик."""
    return price_for_night(checkin) * houses


def price_list_text() -> str:
    """Прайс для команды /prices."""
    return (
        "💰 <b>Цены за домик за ночь</b>\n\n"
        "• Октябрь – Май: <b>2700 ₽</b>\n"
        "• Июнь – Июль: <b>3700 ₽</b>\n"
        "• Август: <b>4200 ₽</b>\n"
        "• Сентябрь: <b>3700 ₽</b>\n\n"
        "Минимальный срок бронирования — 2 ночи.\n"
        "Для подтверждения брони вносится предоплата за 1 сутки.\n"
        "Остальная оплата — при заселении: переводом или наличными."
    )
