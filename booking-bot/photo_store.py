"""Хранилище фотографий домиков.

Фото хранятся не как файлы, а как их Telegram file_id — это ссылки на уже
загруженные в Telegram картинки. Админ присылает фото боту, бот запоминает
file_id в JSON-файле и потом показывает эти фото гостям. Файлы на диске не
занимают места, а показ работает мгновенно.
"""

import json
import logging
import os

import config

logger = logging.getLogger(__name__)


def load() -> list[str]:
    """Список file_id сохранённых фото (пустой, если их ещё нет)."""
    if not os.path.exists(config.PHOTOS_FILE):
        return []
    try:
        with open(config.PHOTOS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [str(x) for x in data]
    except Exception:
        logger.exception("Не удалось прочитать файл с фото")
    return []


def _save(file_ids: list[str]) -> None:
    with open(config.PHOTOS_FILE, "w", encoding="utf-8") as f:
        json.dump(file_ids, f, ensure_ascii=False, indent=2)


def add(file_id: str) -> int:
    """Добавляет фото. Возвращает новое количество фото."""
    file_ids = load()
    file_ids.append(file_id)
    _save(file_ids)
    return len(file_ids)


def clear() -> None:
    _save([])


def count() -> int:
    return len(load())
