"""Отправка заявки на электронную почту организаторов через SMTP."""

import logging
import smtplib
from email.message import EmailMessage

import config

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    """SMTP считается настроенным, если заданы хост, пользователь и пароль."""
    return bool(config.SMTP_HOST and config.SMTP_USER and config.SMTP_PASSWORD)


def send_application(subject: str, body: str, photos: list[bytes]) -> bool:
    """Отправляет письмо с анкетой и вложенными фото. Возвращает True при успехе."""
    if not is_configured():
        logger.info("SMTP не настроен — письмо не отправляется.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.SMTP_FROM or config.SMTP_USER
    msg["To"] = config.TARGET_EMAIL
    msg.set_content(body)

    for i, photo in enumerate(photos, start=1):
        msg.add_attachment(
            photo, maintype="image", subtype="jpeg", filename=f"photo_{i}.jpg"
        )

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Заявка отправлена на почту %s", config.TARGET_EMAIL)
        return True
    except Exception:  # noqa: BLE001 — не роняем бота из-за проблем с почтой
        logger.exception("Не удалось отправить письмо на почту")
        return False
