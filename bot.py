"""Телеграм-бот для приёма заявок на конкурс красоты
«Мисс и Миссис Россия Земля 2026».

Бот проводит участницу по анкете, собирает данные и 5–7 фотографий,
показывает итог, а после подтверждения пересылает заявку организатору в
Telegram и добавляет участницу в накопительную таблицу Google Sheets.
"""

import asyncio
import logging
from datetime import datetime

from telegram import (
    InputMediaPhoto,
    KeyboardButton,
    LinkPreviewOptions,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import categories
import config
import sheets_export


def format_application(data: dict) -> str:
    """Формирует текст заявки на русском языке для отправки организатору."""
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
        f"🏆 Опыт участия в конкурсах: {data.get('experience', '—')}",
        f"📸 Фотографий: {data.get('photos_count', '—')}",
    ]
    if data.get("username"):
        lines.append(f"💬 Telegram: @{data['username']}")
    if data.get("telegram_id"):
        lines.append(f"🆔 Telegram ID: {data['telegram_id']}")
    if data.get("consent"):
        lines.append(f"✅ Согласие на обработку перс. данных: {data['consent']}")
    return "\n".join(lines)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Состояния диалога
CONSENT, NAME, CITY, AGE, HEIGHT, MARITAL, PHONE, EXPERIENCE, PHOTOS, CONFIRM = range(10)

# --- Клавиатуры ---
MARITAL_KEYBOARD = ReplyKeyboardMarkup(
    [[m] for m in categories.MARITAL_OPTIONS],
    resize_keyboard=True,
    one_time_keyboard=True,
)

PHONE_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("📞 Отправить мой номер", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

CONFIRM_KEYBOARD = ReplyKeyboardMarkup(
    [["✅ Отправить заявку"], ["❌ Отменить"]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

CONSENT_KEYBOARD = ReplyKeyboardMarkup(
    [["✅ Согласна"], ["❌ Не согласна"]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


WELCOME = (
    "👑 <b>Кастинг «Мисс и Миссис Россия Земля 2026»</b> 👑\n"
    "🌟 Юбилей — 10 лет! 🌟\n\n"
    f"📅 Приём заявок до <b>{config.DEADLINE}</b>\n"
    f"🎭 Финал <b>{config.FINAL_DATE}</b> — {config.FINAL_PLACE}\n\n"
    "💎 Участницы от 14 до 60 лет, рост от 160 см.\n"
    "✅ Все регионы РФ и дружественные страны.\n"
    "✅ Не замужем, разведены, замужем.\n\n"
    "<b>Категории:</b>\n"
    "• Young Miss Russia Earth 👑 (14–18 лет)\n"
    "• Ms Russia Earth 👑 (18–40 лет)\n"
    "• Mrs Russia Earth 👑 (18–45 лет)\n"
    "• Classic Mrs Russia Earth 👑 (45–60 лет)\n\n"
    "Чтобы подать заявку, нажмите /apply\n"
    f"❓ Вопросы — пишите в {config.CONTACT_LINK}"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        WELCOME, link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data["photos"] = []
    await update.message.reply_text(
        "📝 Начинаем анкету!\n\n"
        "Перед началом необходимо <b>согласие на обработку персональных данных</b>.\n\n"
        "Отправляя заявку, вы даёте согласие на обработку ваших персональных данных "
        "и фотографий организаторами конкурса "
        f"«{config.CONTEST_NAME}» в целях участия в кастинге и конкурсе "
        "(в соответствии с ФЗ-152 «О персональных данных»).\n\n"
        "Вы согласны?",
        parse_mode=ParseMode.HTML,
        reply_markup=CONSENT_KEYBOARD,
    )
    return CONSENT


async def get_consent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()
    if text.startswith("✅") or ("соглас" in text and "не" not in text):
        context.user_data["consent"] = (
            f"Дано {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        await update.message.reply_text(
            "Спасибо! В любой момент можно отменить командой /cancel.\n\n"
            "1️⃣ Напишите вашу <b>Фамилию и Имя</b>:",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(),
        )
        return NAME

    await update.message.reply_text(
        "Без согласия на обработку персональных данных подать заявку нельзя. "
        "Если передумаете — нажмите /apply.",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name) < 3:
        await update.message.reply_text(
            "Пожалуйста, укажите Фамилию и Имя (не менее 3 символов):"
        )
        return NAME
    context.user_data["name"] = name
    await update.message.reply_text("2️⃣ Из какого вы <b>города</b>?", parse_mode=ParseMode.HTML)
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["city"] = update.message.text.strip()
    await update.message.reply_text(
        f"3️⃣ Укажите ваш <b>возраст</b> (от {config.MIN_AGE} до {config.MAX_AGE} лет):",
        parse_mode=ParseMode.HTML,
    )
    return AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Введите возраст числом, например 25:")
        return AGE
    age = int(text)
    if not (config.MIN_AGE <= age <= config.MAX_AGE):
        await update.message.reply_text(
            f"К участию приглашаются от {config.MIN_AGE} до {config.MAX_AGE} лет. "
            "Пожалуйста, проверьте возраст:"
        )
        return AGE
    context.user_data["age"] = age
    await update.message.reply_text(
        f"4️⃣ Укажите ваш <b>рост в см</b> (от {config.MIN_HEIGHT} см):",
        parse_mode=ParseMode.HTML,
    )
    return HEIGHT


async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().replace(",", ".")
    try:
        height = int(float(text))
    except ValueError:
        await update.message.reply_text("Введите рост числом в сантиметрах, например 170:")
        return HEIGHT
    if height < config.MIN_HEIGHT or height > 220:
        await update.message.reply_text(
            f"Требуется рост от {config.MIN_HEIGHT} см. Пожалуйста, проверьте значение:"
        )
        return HEIGHT
    context.user_data["height"] = height
    await update.message.reply_text(
        "5️⃣ Ваше <b>семейное положение</b>?",
        parse_mode=ParseMode.HTML,
        reply_markup=MARITAL_KEYBOARD,
    )
    return MARITAL


async def get_marital(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    marital = update.message.text.strip()
    if marital not in categories.MARITAL_OPTIONS:
        await update.message.reply_text(
            "Пожалуйста, выберите вариант с помощью кнопок ниже.",
            reply_markup=MARITAL_KEYBOARD,
        )
        return MARITAL
    context.user_data["marital"] = marital
    context.user_data["category"] = categories.suggest_category(
        context.user_data["age"], marital
    )
    await update.message.reply_text(
        "6️⃣ Укажите ваш <b>контактный телефон</b>.\n"
        "Можно отправить кнопкой ниже или написать вручную:",
        parse_mode=ParseMode.HTML,
        reply_markup=PHONE_KEYBOARD,
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
    digits = sum(c.isdigit() for c in phone)
    if digits < 7:
        await update.message.reply_text(
            "Похоже, номер указан не полностью. Введите контактный телефон ещё раз:"
        )
        return PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text(
        "7️⃣ Расскажите о вашем <b>опыте участия в конкурсах красоты</b>.\n"
        "Если опыта нет — напишите «Нет».",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )
    return EXPERIENCE


async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["experience"] = update.message.text.strip()
    await update.message.reply_text(
        f"8️⃣ Пришлите <b>{config.MIN_PHOTOS}–{config.MAX_PHOTOS} фотографий</b> "
        "хорошего профессионального качества.\n\n"
        "Отправляйте по одному фото. Когда закончите — нажмите /done.",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHOTOS


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photos = context.user_data.setdefault("photos", [])
    if len(photos) >= config.MAX_PHOTOS:
        await update.message.reply_text(
            f"Уже загружено максимум ({config.MAX_PHOTOS}) фото. Нажмите /done."
        )
        return PHOTOS

    # Берём фото максимального размера
    photo_file = await update.message.photo[-1].get_file()
    data = bytes(await photo_file.download_as_bytearray())
    photos.append(data)

    count = len(photos)
    if count < config.MIN_PHOTOS:
        await update.message.reply_text(
            f"📸 Принято фото {count}/{config.MIN_PHOTOS}. "
            f"Нужно ещё минимум {config.MIN_PHOTOS - count}."
        )
    else:
        await update.message.reply_text(
            f"📸 Принято фото {count}/{config.MAX_PHOTOS}. "
            "Можно прислать ещё или нажать /done для завершения."
        )
    return PHOTOS


async def photos_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photos = context.user_data.get("photos", [])
    if len(photos) < config.MIN_PHOTOS:
        await update.message.reply_text(
            f"Нужно минимум {config.MIN_PHOTOS} фото. Сейчас загружено {len(photos)}. "
            "Пришлите ещё."
        )
        return PHOTOS

    context.user_data["photos_count"] = len(photos)
    user = update.effective_user
    context.user_data["username"] = user.username
    context.user_data["telegram_id"] = user.id

    summary = format_application(context.user_data)
    await update.message.reply_text(
        "Проверьте вашу заявку:\n\n"
        f"{summary}\n\n"
        "Всё верно? Нажмите «✅ Отправить заявку» для отправки.",
        reply_markup=CONFIRM_KEYBOARD,
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.startswith("❌") or text.lower() == "отменить":
        return await cancel(update, context)
    if not (text.startswith("✅") or text.lower() == "отправить"):
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки ниже.", reply_markup=CONFIRM_KEYBOARD
        )
        return CONFIRM

    data = dict(context.user_data)
    photos = data.pop("photos", [])
    data["photos_count"] = len(photos)

    data["submitted_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")
    body = format_application(data)

    # Пересылка заявки лично организатору в Telegram
    delivered = await _forward_to_admin(context, photos, body)
    # Автоматический перенос участницы в Google-таблицу
    await _update_table(context, data)

    if delivered:
        await update.message.reply_text(
            "🎉 Спасибо! Ваша заявка принята.\n\n"
            f"Организаторы свяжутся с вами. По всем вопросам пишите в {config.CONTACT_LINK}\n\n"
            "Желаем удачи! 👑",
            parse_mode=ParseMode.HTML,
            link_preview_options=LinkPreviewOptions(is_disabled=True),
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            "⚠️ Не удалось отправить заявку автоматически. "
            f"Пожалуйста, напишите организаторам напрямую — {config.CONTACT}",
            reply_markup=ReplyKeyboardRemove(),
        )
    context.user_data.clear()
    return ConversationHandler.END


async def _forward_to_admin(context, photos, body) -> bool:
    """Пересылает заявку организатору. Возвращает True при успехе."""
    try:
        await context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=body)
        if photos:
            media = [InputMediaPhoto(p) for p in photos[:10]]
            await context.bot.send_media_group(chat_id=config.ADMIN_CHAT_ID, media=media)
        return True
    except Exception:
        logger.exception("Не удалось переслать заявку организатору")
        return False


async def _update_table(context, data) -> None:
    """Дописывает участницу в Google-таблицу; при ошибке уведомляет организатора."""
    if sheets_export.append_participant(data):
        return
    try:
        await context.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=(
                "⚠️ Участницу не удалось добавить в Google-таблицу. "
                "Проверьте настройки Google Sheets (см. логи бота)."
            ),
        )
    except Exception:
        logger.exception("Не удалось уведомить организатора об ошибке таблицы")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Заявка отменена. Чтобы начать заново — /apply",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def table_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Присылает организатору ссылку на Google-таблицу участниц."""
    if update.effective_chat.id != config.ADMIN_CHAT_ID:
        return
    if not sheets_export.is_configured():
        await update.message.reply_text(
            "Google-таблица пока не настроена (см. README)."
        )
        return
    await update.message.reply_text(
        f"📊 Таблица участниц:\n{sheets_export.sheet_url()}"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Команды бота:\n"
        "/start — информация о конкурсе\n"
        "/apply — подать заявку\n"
        "/cancel — отменить заполнение\n"
        f"❓ Вопросы — {config.CONTACT}"
    )


async def fallback_in_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Пришлите фотографию 📸 или нажмите /done "
        f"(нужно {config.MIN_PHOTOS}–{config.MAX_PHOTOS} фото)."
    )
    return PHOTOS


def build_application() -> Application:
    application = Application.builder().token(config.BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("apply", apply)],
        states={
            CONSENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_consent)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_height)],
            MARITAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_marital)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
            PHOTOS: [
                MessageHandler(filters.PHOTO, get_photo),
                CommandHandler("done", photos_done),
                MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_in_photos),
            ],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("table", table_command))
    application.add_handler(conv)
    return application


def main() -> None:
    config.validate()

    # На новых версиях Python (3.12+, особенно 3.14) в главном потоке может
    # отсутствовать событийный цикл asyncio, который ожидает run_polling.
    # Создаём его явно, иначе запуск падает с RuntimeError.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    application = build_application()
    logger.info("Бот запущен. Ожидание сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
