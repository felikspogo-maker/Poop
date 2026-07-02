"""Сохранение заявок на диск (JSON + фотографии)."""

import json
import os
from datetime import datetime

import config


def _safe_name(text: str) -> str:
    keep = [c if c.isalnum() or c in " _-" else "_" for c in text]
    return "".join(keep).strip().replace(" ", "_")[:60] or "zayavka"


def save_submission(data: dict, photos: list[bytes]) -> str:
    """Сохраняет анкету и фото в отдельную папку. Возвращает путь к папке."""
    os.makedirs(config.SUBMISSIONS_DIR, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{stamp}_{_safe_name(data.get('name', ''))}"
    folder = os.path.join(config.SUBMISSIONS_DIR, folder_name)
    os.makedirs(folder, exist_ok=True)

    record = dict(data)
    record["submitted_at"] = datetime.now().isoformat(timespec="seconds")
    record["photos_count"] = len(photos)

    with open(os.path.join(folder, "anketa.json"), "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    # Человекочитаемая версия
    with open(os.path.join(folder, "anketa.txt"), "w", encoding="utf-8") as f:
        f.write(format_application(data))

    for i, photo in enumerate(photos, start=1):
        with open(os.path.join(folder, f"photo_{i}.jpg"), "wb") as f:
            f.write(photo)

    return folder


def format_application(data: dict) -> str:
    """Формирует текст заявки на русском языке."""
    lines = [
        "🌟 НОВАЯ ЗАЯВКА — Мисс и Миссис Россия Земля 2026 🌟",
        "",
        f"👤 ФИ: {data.get('name', '—')}",
        f"🏙 Город: {data.get('city', '—')}",
        f"🎂 Возраст: {data.get('age', '—')}",
        f"📏 Рост: {data.get('height', '—')} см",
        f"💍 Семейное положение: {data.get('marital', '—')}",
        f"📞 Телефон: {data.get('phone', '—')}",
        f"🏷 Категория: {data.get('category', '—')}",
        f"📸 Фотографий: {data.get('photos_count', '—')}",
    ]
    if data.get("username"):
        lines.append(f"💬 Telegram: @{data['username']}")
    if data.get("telegram_id"):
        lines.append(f"🆔 Telegram ID: {data['telegram_id']}")
    return "\n".join(lines)
