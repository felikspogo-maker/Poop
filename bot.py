"""Телеграм-бот для приёма заявок на конкурс красоты
«Мисс и Миссис Россия Земля 2026».

Бот проводит участницу по анкете, собирает данные и 5–7 фотографий,
показывает итог, а после подтверждения сохраняет заявку, пересылает её
администратору и (если настроен SMTP) отправляет на почту организаторов.
"""

import logging

from telegram import (
    KeyboardButton,
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
import mailer
import storage

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Состояния диалога
NAME, CITY, AGE, HEIGHT, MARITAL, PHONE, PHOTOS, CONFIRM = range(8)

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
    f"❓ Вопросы — в директ {config.CONTACT}"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(WELCOME)


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data["photos"] = []
    await update.message.reply_text(
        "📝 Начинаем анкету!\n\n"
        "В любой момент можно отменить командой /cancel.\n\n"
        "1️⃣ Напишите вашу <b>Фамилию и Имя</b>:",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


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
        f"7️⃣ Пришлите <b>{config.MIN_PHOTOS}–{config.MAX_PHOTOS} фотографий</b> "
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

    summary = storage.format_application(context.user_data)
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

    # 1. Сохраняем на диск
    try:
        folder = storage.save_submission(data, photos)
        logger.info("Заявка сохранена: %s", folder)
    except Exception:
        logger.exception("Ошибка сохранения заявки на диск")

    body = storage.format_application(data)

    # 2. Пересылаем администратору
    await _forward_to_admin(context, data, photos, body)

    # 3. Отправляем на почту (если настроено)
    mailer.send_application(
        subject=f"Заявка на конкурс — {data.get('name', '')}",
        body=body,
        photos=photos,
    )

    await update.message.reply_text(
        "🎉 Спасибо! Ваша заявка принята.\n\n"
        f"Организаторы свяжутся с вами. По всем вопросам — {config.CONTACT}\n\n"
        "Желаем удачи! 👑",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def _forward_to_admin(context, data, photos, body) -> None:
    if not config.ADMIN_CHAT_ID:
        return
    try:
        from telegram import InputMediaPhoto

        await context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=body)
        if photos:
            media = [InputMediaPhoto(p) for p in photos[:10]]
            await context.bot.send_media_group(chat_id=config.ADMIN_CHAT_ID, media=media)
    except Exception:
        logger.exception("Не удалось переслать заявку администратору")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Заявка отменена. Чтобы начать заново — /apply",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


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
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_height)],
            MARITAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_marital)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
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
    application.add_handler(conv)
    return application


def main() -> None:
    config.validate()
    application = build_application()
    logger.info("Бот запущен. Ожидание сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
