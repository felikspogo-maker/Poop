"""Телеграм-бот приёма анкет на конкурс «Мисс и Миссис Краснодарский край 2027».

Бот проводит участницу по анкете, собирает данные, 5 фото и видео-визитку,
показывает итог, а после подтверждения пересылает анкету организаторам
в Telegram и дописывает участницу в Google-таблицу.
"""

import asyncio
import logging
from datetime import date, datetime

from telegram import (
    InputMediaPhoto,
    InputMediaVideo,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import config
import sheets_export

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)  # не засорять логи опросами
logger = logging.getLogger(__name__)

(
    CONSENT,
    NAME,
    CITY,
    AGE,
    CATEGORY,
    MARITAL,
    HEIGHT,
    SIZE,
    EXPERIENCE,
    PHONE,
    TELEGRAM,
    PHOTOS,
    CONFIRM,
) = range(13)

# --- Кнопки ---
BTN_APPLY = "📝 Подать анкету"
BTN_INFO = "👑 О конкурсе"
BTN_AGREE = "✅ Согласна"
BTN_DISAGREE = "❌ Не согласна"
BTN_SEND = "✅ Отправить анкету"
BTN_CANCEL = "❌ Отменить"


def _kb(rows: list[list[str]], one_time: bool = True) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=one_time)


MAIN_MENU = _kb([[BTN_APPLY], [BTN_INFO]], one_time=False)
CONSENT_KB = _kb([[BTN_AGREE], [BTN_DISAGREE]])
MARITAL_KB = _kb([[m] for m in config.MARITAL_OPTIONS])
SIZE_KB = _kb([config.CLOTHING_SIZES])
PHONE_KB = _kb([[KeyboardButton("📞 Отправить мой номер", request_contact=True)]])
CONFIRM_KB = _kb([[BTN_SEND], [BTN_CANCEL]])


def _contact_line() -> str:
    return f"\n❓ Вопросы: {config.CONTACT_INFO}" if config.CONTACT_INFO else ""


def _categories_text() -> str:
    return "\n".join(
        f"• «{name}» — {lo}–{hi} лет" for name, lo, hi in config.CATEGORIES
    )


INFO_TEXT = (
    f"👑 <b>{config.CONTEST_NAME}</b> 👑\n\n"
    f"📅 Приём анкет до <b>{config.DEADLINE_TEXT}</b>\n\n"
    "<b>Категории:</b>\n"
    f"{_categories_text()}\n\n"
    "<b>Требования:</b>\n"
    f"• рост от {config.MIN_HEIGHT} см\n"
    f"• размер одежды {config.CLOTHING_SIZES[0]}–{config.CLOTHING_SIZES[-1]}\n"
    f"• {config.MEDIA_REQUIRED} фото (часть можно заменить видео)\n\n"
    f"Чтобы подать анкету — нажмите «{BTN_APPLY}»"
    f"{_contact_line()}"
)


def _deadline_passed() -> bool:
    return date.today() > config.DEADLINE


def format_application(data: dict) -> str:
    lines = [
        f"🌟 НОВАЯ АНКЕТА — {config.CONTEST_NAME} 🌟",
        "",
        f"👤 ФИО: {data.get('name', '—')}",
        f"🏙 Город: {data.get('city', '—')}",
        f"🎂 Возраст: {data.get('age', '—')}",
        f"🏷 Категория: {data.get('category', '—')}",
        f"💍 Семейное положение: {data.get('marital', '—')}",
        f"📏 Рост: {data.get('height', '—')} см",
        f"👗 Размер одежды: {data.get('size', '—')}",
        f"🏆 Опыт участия: {data.get('experience', '—')}",
        f"📞 Телефон: {data.get('phone', '—')}",
        f"💬 Telegram: {data.get('telegram', '—')}",
        f"📸 Фото: {data.get('photos_count', 0)} шт",
        f"🎬 Видео: {data.get('videos_count', 0)} шт",
    ]
    if data.get("telegram_id"):
        lines.append(f"🆔 Telegram ID: {data['telegram_id']}")
    if data.get("consent"):
        lines.append(f"✅ Согласие на обработку перс. данных: {data['consent']}")
    return "\n".join(lines)


# --- Общие команды ---


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(INFO_TEXT, reply_markup=MAIN_MENU)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(INFO_TEXT, reply_markup=MAIN_MENU)


async def table_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ссылка на Google-таблицу — только для организаторов."""
    if update.effective_chat.id not in config.ADMIN_CHAT_IDS:
        return
    if not sheets_export.is_configured():
        await update.message.reply_text("Google-таблица пока не настроена.")
        return
    await update.message.reply_text(f"📊 Таблица участниц:\n{sheets_export.sheet_url()}")


# --- Анкета ---


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    if _deadline_passed():
        await update.message.reply_text(
            f"К сожалению, приём анкет завершён ({config.DEADLINE_TEXT})."
            f"{_contact_line()}",
            reply_markup=MAIN_MENU,
        )
        return ConversationHandler.END
    await update.message.reply_html(
        "📝 Начинаем анкету! Отменить можно в любой момент — /cancel\n\n"
        "Перед началом нужно <b>согласие на обработку персональных данных</b>.\n\n"
        "Отправляя анкету, вы даёте согласие на обработку ваших персональных "
        f"данных, фото и видео организаторами конкурса «{config.CONTEST_NAME}» "
        "в целях участия в кастинге и конкурсе (ФЗ-152 «О персональных данных»).\n"
        "Для участниц до 18 лет согласие даёт родитель или законный представитель.\n\n"
        "Вы согласны?",
        reply_markup=CONSENT_KB,
    )
    return CONSENT


async def get_consent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text != BTN_AGREE:
        context.user_data.clear()
        await update.message.reply_text(
            "Без согласия на обработку данных подать анкету нельзя. "
            "Если передумаете — нажмите «📝 Подать анкету».",
            reply_markup=MAIN_MENU,
        )
        return ConversationHandler.END
    context.user_data["consent"] = f"Дано {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    await update.message.reply_html(
        "1️⃣ Ваши <b>Фамилия, Имя, Отчество</b>:", reply_markup=ReplyKeyboardRemove()
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name.split()) < 2:
        await update.message.reply_text("Укажите, пожалуйста, ФИО полностью:")
        return NAME
    context.user_data["name"] = name
    await update.message.reply_html(
        "2️⃣ Ваш <b>город / населённый пункт</b>:"
    )
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["city"] = update.message.text.strip()
    await update.message.reply_html(
        f"3️⃣ Ваш <b>возраст</b> (от {config.MIN_AGE} до {config.MAX_AGE} лет):"
    )
    return AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Введите возраст числом, например 23:")
        return AGE
    age = int(text)
    fitting = config.categories_for_age(age)
    if not fitting:
        await update.message.reply_text(
            f"В конкурсе участвуют девушки от {config.MIN_AGE} до {config.MAX_AGE} лет. "
            "Проверьте возраст:"
        )
        return AGE
    context.user_data["age"] = age
    if len(fitting) == 1:
        context.user_data["category"] = fitting[0]
        await update.message.reply_html(
            f"Ваша категория: <b>«{fitting[0]}»</b> 👑\n\n"
            "4️⃣ Ваше <b>семейное положение</b>?",
            reply_markup=MARITAL_KB,
        )
        return MARITAL
    await update.message.reply_html(
        "4️⃣ Выберите <b>категорию</b>:",
        reply_markup=_kb([[f"«{c}»"] for c in fitting]),
    )
    return CATEGORY


async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.strip().strip("«»")
    fitting = config.categories_for_age(context.user_data["age"])
    if choice not in fitting:
        await update.message.reply_text(
            "Выберите категорию кнопкой ниже:",
            reply_markup=_kb([[f"«{c}»"] for c in fitting]),
        )
        return CATEGORY
    context.user_data["category"] = choice
    await update.message.reply_html(
        "Ваше <b>семейное положение</b>?", reply_markup=MARITAL_KB
    )
    return MARITAL


async def get_marital(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    marital = update.message.text.strip()
    if marital not in config.MARITAL_OPTIONS:
        await update.message.reply_text(
            "Выберите вариант кнопкой ниже:", reply_markup=MARITAL_KB
        )
        return MARITAL
    context.user_data["marital"] = marital
    await update.message.reply_html(
        f"5️⃣ Ваш <b>рост в см</b> (от {config.MIN_HEIGHT} см):",
        reply_markup=ReplyKeyboardRemove(),
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
            f"Для участия нужен рост от {config.MIN_HEIGHT} см. Проверьте значение:"
        )
        return HEIGHT
    context.user_data["height"] = height
    await update.message.reply_html("6️⃣ Ваш <b>размер одежды</b>:", reply_markup=SIZE_KB)
    return SIZE


async def get_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    size = update.message.text.strip()
    if size not in config.CLOTHING_SIZES:
        await update.message.reply_text(
            f"Для участия нужен размер одежды {config.CLOTHING_SIZES[0]}–"
            f"{config.CLOTHING_SIZES[-1]}. Выберите кнопкой:",
            reply_markup=SIZE_KB,
        )
        return SIZE
    context.user_data["size"] = size
    await update.message.reply_html(
        "7️⃣ Расскажите об <b>опыте участия в конкурсах</b> красоты.\n"
        "Если опыта нет — напишите «Нет».",
        reply_markup=ReplyKeyboardRemove(),
    )
    return EXPERIENCE


async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["experience"] = update.message.text.strip()
    await update.message.reply_html(
        "8️⃣ Ваш <b>номер телефона</b> — кнопкой ниже или вручную:",
        reply_markup=PHONE_KB,
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = (update.message.text or "").strip()
    if sum(c.isdigit() for c in phone) < 10:
        await update.message.reply_text("Похоже, номер неполный. Введите телефон ещё раз:")
        return PHONE
    context.user_data["phone"] = phone

    user = update.effective_user
    context.user_data["telegram_id"] = user.id
    if user.username:
        context.user_data["telegram"] = f"@{user.username}"
        return await _ask_photos(update, context)

    await update.message.reply_html(
        "9️⃣ У вашего Telegram нет имени пользователя (@ник). Напишите, как с вами "
        "связаться в Telegram — @ник или номер, привязанный к Telegram:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TELEGRAM


async def get_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["telegram"] = update.message.text.strip()
    return await _ask_photos(update, context)


async def _ask_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["media"] = []
    await update.message.reply_html(
        f"📸 Пришлите <b>{config.MEDIA_REQUIRED} фото или видео</b> хорошего качества — "
        "по одному или альбомом. Можно только фото, а можно часть заменить видео 🎬",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHOTOS


async def get_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Принимает фото или видео; после нужного количества — показывает итог."""
    msg = update.message
    media: list[tuple[str, str]] = context.user_data.setdefault("media", [])
    if len(media) >= config.MEDIA_REQUIRED:
        return PHOTOS  # лишнее из альбома игнорируем
    if msg.photo:
        media.append(("photo", msg.photo[-1].file_id))
    elif msg.video:
        media.append(("video", msg.video.file_id))
    else:
        return PHOTOS

    left = config.MEDIA_REQUIRED - len(media)
    if left > 0:
        await msg.reply_text(f"✅ Принято {len(media)}/{config.MEDIA_REQUIRED}. Ещё {left}.")
        return PHOTOS

    context.user_data["photos_count"] = sum(1 for k, _ in media if k == "photo")
    context.user_data["videos_count"] = sum(1 for k, _ in media if k == "video")
    await msg.reply_text(
        "Проверьте анкету:\n\n"
        f"{format_application(context.user_data)}\n\n"
        "Всё верно?",
        reply_markup=CONFIRM_KB,
    )
    return CONFIRM


async def media_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    left = config.MEDIA_REQUIRED - len(context.user_data.get("media", []))
    await update.message.reply_text(
        f"Пришлите, пожалуйста, фото 📸 или видео 🎬 (осталось {left}). "
        "Видео отправляйте как видео, а не файлом."
    )
    return PHOTOS


async def _ignore_extra_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Лишние фото/видео из альбома (сверх нужного) пропускаем."""
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == BTN_CANCEL:
        return await cancel(update, context)
    if text != BTN_SEND:
        await update.message.reply_text("Используйте кнопки ниже.", reply_markup=CONFIRM_KB)
        return CONFIRM

    data = dict(context.user_data)
    data["submitted_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")

    delivered = await _forward_to_admins(context, data)
    table_ok = await asyncio.to_thread(sheets_export.append_participant, data)
    if not table_ok and sheets_export.is_configured():
        await _notify_admins(
            context,
            f"⚠️ Анкету «{data.get('name')}» не удалось добавить в Google-таблицу "
            "(см. логи бота). Сама анкета выше.",
        )

    if delivered:
        await update.message.reply_text(
            "🎉 Спасибо! Ваша анкета принята.\n\n"
            "Организаторы свяжутся с вами. Желаем удачи! 👑"
            f"{_contact_line()}",
            reply_markup=MAIN_MENU,
        )
    else:
        await update.message.reply_text(
            "⚠️ Не удалось отправить анкету автоматически. Попробуйте позже"
            + (f" или напишите организаторам: {config.CONTACT_INFO}" if config.CONTACT_INFO else ".")
            ,
            reply_markup=MAIN_MENU,
        )
    context.user_data.clear()
    return ConversationHandler.END


async def _forward_to_admins(context: ContextTypes.DEFAULT_TYPE, data: dict) -> bool:
    """Отправляет анкету и альбом фото/видео всем организаторам.

    True — если анкету получил хотя бы один из них.
    """
    body = format_application(data)
    album = [
        InputMediaPhoto(fid) if kind == "photo" else InputMediaVideo(fid)
        for kind, fid in data.get("media", [])
    ]
    delivered = False
    for chat_id in config.ADMIN_CHAT_IDS:
        try:
            await context.bot.send_message(chat_id=chat_id, text=body)
            if album:
                await context.bot.send_media_group(chat_id=chat_id, media=album)
            delivered = True
        except Exception:
            logger.exception("Не удалось отправить анкету организатору %s", chat_id)
    return delivered


async def _notify_admins(context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    for chat_id in config.ADMIN_CHAT_IDS:
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception:
            logger.exception("Не удалось уведомить организатора %s", chat_id)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        f"Анкета отменена. Начать заново — «{BTN_APPLY}».", reply_markup=MAIN_MENU
    )
    return ConversationHandler.END


async def _post_init(application: Application) -> None:
    from telegram import BotCommand

    await application.bot.set_my_commands(
        [
            BotCommand("apply", "📝 Подать анкету"),
            BotCommand("info", "👑 О конкурсе"),
            BotCommand("cancel", "❌ Отменить анкету"),
        ]
    )


def build_application() -> Application:
    application = Application.builder().token(config.BOT_TOKEN).post_init(_post_init).build()

    text = filters.TEXT & ~filters.COMMAND
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("apply", apply),
            MessageHandler(filters.Text([BTN_APPLY]), apply),
        ],
        states={
            CONSENT: [MessageHandler(text, get_consent)],
            NAME: [MessageHandler(text, get_name)],
            CITY: [MessageHandler(text, get_city)],
            AGE: [MessageHandler(text, get_age)],
            CATEGORY: [MessageHandler(text, get_category)],
            MARITAL: [MessageHandler(text, get_marital)],
            HEIGHT: [MessageHandler(text, get_height)],
            SIZE: [MessageHandler(text, get_size)],
            EXPERIENCE: [MessageHandler(text, get_experience)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(text, get_phone),
            ],
            TELEGRAM: [MessageHandler(text, get_telegram)],
            PHOTOS: [
                MessageHandler(filters.PHOTO | filters.VIDEO, get_media),
                MessageHandler(~filters.COMMAND, media_other),
            ],
            CONFIRM: [
                MessageHandler(text, confirm),
                MessageHandler(filters.PHOTO | filters.VIDEO, _ignore_extra_media),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("help", info))
    application.add_handler(CommandHandler("table", table_command))
    application.add_handler(MessageHandler(filters.Text([BTN_INFO]), info))
    application.add_handler(conv)
    return application


def main() -> None:
    config.validate()
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    application = build_application()
    logger.info("Бот «%s» запущен.", config.CONTEST_NAME)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
