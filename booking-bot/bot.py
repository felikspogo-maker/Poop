"""Телеграм-бот бронирования домиков — «Гостевой дом A-Home», Сухум, Абхазия.

Бот проводит гостя по брони: даты, количество домиков и гостей, питомец,
трансфер, контакты. Считает стоимость по сезонным ценам, берёт предоплату
за одни сутки (перевод/СБП + скриншот чека) и отправляет бронь менеджеру.
Когда появится API-токен RealtyCalendar — брони будут добавляться в календарь
автоматически (см. realty_calendar.py).
"""

import asyncio
import logging
from datetime import date, datetime, timedelta

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

import config
import info
import photo_store
import pricing
import realty_calendar

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Состояния диалога бронирования
(
    CHECKIN,
    CHECKOUT,
    HOUSES,
    GUESTS,
    PET,
    TRANSFER,
    NAME,
    PHONE,
    CONFIRM,
    SCREENSHOT,
) = range(10)

YES_NO_KEYBOARD = ReplyKeyboardMarkup(
    [["Да", "Нет"]], resize_keyboard=True, one_time_keyboard=True
)

HOUSES_KEYBOARD = ReplyKeyboardMarkup(
    [["1", "2", "3"]], resize_keyboard=True, one_time_keyboard=True
)

PHONE_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("📞 Отправить мой номер", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

CONFIRM_KEYBOARD = ReplyKeyboardMarkup(
    [["✅ Перейти к оплате"], ["❌ Отменить"]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# Кнопки главного меню (постоянная клавиатура)
BTN_BOOK = "🔑 Забронировать домик"
BTN_PHOTOS = "📷 Фото домиков"
BTN_PRICES = "💰 Цены"
BTN_ABOUT = "🏡 О доме"
BTN_BORDER = "🛂 Граница РФ–Абхазия"
BTN_TIPS = "🗺 Советы путешественнику"

MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [[BTN_BOOK], [BTN_PHOTOS, BTN_PRICES], [BTN_ABOUT, BTN_BORDER], [BTN_TIPS]],
    resize_keyboard=True,
)

# Состояние админского режима загрузки фото
ADDING_PHOTOS = 100

WELCOME = (
    f"🏡 Добро пожаловать в <b>{config.GUESTHOUSE_NAME}</b>!\n"
    f"📍 {config.ADDRESS}\n\n"
    "Здесь можно забронировать уютный домик у моря в Сухуме.\n\n"
    "Пользуйтесь кнопками меню внизу 👇 или командами:\n"
    "• /book — забронировать домик 🔑\n"
    "• /photos — фото домиков 📷\n"
    "• /prices — цены 💰\n"
    "• /about — о доме и удобствах 🏡\n"
    "• /border — правила пересечения границы РФ–Абхазия 🛂\n"
    "• /tips — куда съездить и памятка путешественнику 🗺\n"
    "• /cancel — отменить оформление\n\n"
    "Минимальный срок — 2 ночи. Для подтверждения брони вносится "
    "предоплата за 1 сутки."
)


def parse_date(text: str) -> date | None:
    """Разбирает дату в форматах ДД.ММ.ГГГГ или ДД.ММ.ГГ."""
    text = text.strip().replace("/", ".").replace("-", ".").replace(" ", "")
    for fmt in ("%d.%m.%Y", "%d.%m.%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def format_booking(data: dict) -> str:
    """Текст брони для менеджера и для проверки гостем."""
    checkin: date = data["checkin"]
    checkout: date = data["checkout"]
    nights = pricing.nights_between(checkin, checkout)
    lines = [
        "🏡 НОВАЯ БРОНЬ — Гостевой дом A-Home",
        "",
        f"📅 Заезд: {checkin.strftime('%d.%m.%Y')} (с {config.CHECKIN_TIME})",
        f"📅 Выезд: {checkout.strftime('%d.%m.%Y')} (до {config.CHECKOUT_TIME})",
        f"🌙 Ночей: {nights}",
        f"🏠 Домиков: {data['houses']}",
        f"👥 Гостей: {data['guests']}",
        f"🐾 С питомцем: {data['pet']}",
        f"🚕 Нужен трансфер: {data['transfer']}",
        f"👤 Имя: {data['name']}",
        f"📞 Телефон: {data['phone']}",
        "",
        f"💰 Стоимость проживания: {data['total']} ₽",
        f"💳 Предоплата (1 сутки): {data['prepay']} ₽",
        f"💵 Остаток при заселении: {data['total'] - data['prepay']} ₽ "
        "(перевод или наличные)",
    ]
    if data.get("username"):
        lines.append(f"💬 Telegram: @{data['username']}")
    if data.get("telegram_id"):
        lines.append(f"🆔 Telegram ID: {data['telegram_id']}")
    return "\n".join(lines)


# --- Команды ---


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(WELCOME, reply_markup=MAIN_MENU_KEYBOARD)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(info.ABOUT_TEXT, reply_markup=MAIN_MENU_KEYBOARD)


async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        pricing.price_list_text(), reply_markup=MAIN_MENU_KEYBOARD
    )


async def border(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        info.BORDER_TEXT,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=MAIN_MENU_KEYBOARD,
    )


async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Места (туристические и «для своих») + памятка путешественнику."""
    await update.message.reply_html(
        info.PLACES_TEXT,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
    await update.message.reply_html(
        info.MEMO_TEXT,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=MAIN_MENU_KEYBOARD,
    )


async def show_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает гостю фотографии домиков (альбомом)."""
    file_ids = photo_store.load()
    if not file_ids:
        await update.message.reply_text(
            "📷 Фотографии домиков скоро появятся. "
            f"Пока их можно запросить у менеджера: {config.PHONE_FOR_GUESTS}",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return
    await update.message.reply_text("📷 Наши домики:")
    for i in range(0, len(file_ids), 10):  # альбом — максимум 10 фото
        media = [InputMediaPhoto(fid) for fid in file_ids[i : i + 10]]
        try:
            await context.bot.send_media_group(
                chat_id=update.effective_chat.id, media=media
            )
        except Exception:
            logger.exception("Не удалось отправить фото домиков")
    await update.message.reply_text(
        "Понравилось? Жмите «🔑 Забронировать домик» 🌊",
        reply_markup=MAIN_MENU_KEYBOARD,
    )


# --- Админский режим: загрузка фотографий домиков ---


def _is_admin(update: Update) -> bool:
    return update.effective_chat.id in config.admin_ids()


async def add_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not _is_admin(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "🖼 Режим добавления фото.\n\n"
        "Пришлите фотографии домиков — по одной или альбомом. Каждая добавится "
        "в галерею для гостей.\n\n"
        "Когда закончите — /donephotos. Отмена — /cancel.\n"
        f"Сейчас в галерее: {photo_store.count()} фото.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ADDING_PHOTOS


async def receive_admin_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    file_id = update.message.photo[-1].file_id
    total = photo_store.add(file_id)
    await update.message.reply_text(
        f"✅ Добавлено (всего в галерее: {total}). Присылайте ещё или /donephotos."
    )
    return ADDING_PHOTOS


async def done_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Готово! В галерее {photo_store.count()} фото. "
        f"Гости увидят их по кнопке «{BTN_PHOTOS}».",
        reply_markup=MAIN_MENU_KEYBOARD,
    )
    return ConversationHandler.END


async def clear_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    photo_store.clear()
    await update.message.reply_text(
        "🗑 Галерея фото очищена. Добавить заново — /addphotos",
        reply_markup=MAIN_MENU_KEYBOARD,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(WELCOME, reply_markup=MAIN_MENU_KEYBOARD)


# --- Диалог бронирования ---


async def book(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "🔑 Начинаем бронирование! Отменить можно в любой момент — /cancel\n\n"
        "1️⃣ Дата заезда (в формате ДД.ММ.ГГГГ, например 15.08.2026):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CHECKIN


async def get_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    checkin = parse_date(update.message.text)
    if checkin is None:
        await update.message.reply_text(
            "Не получилось разобрать дату. Введите в формате ДД.ММ.ГГГГ, "
            "например 15.08.2026:"
        )
        return CHECKIN
    if checkin < date.today():
        await update.message.reply_text(
            "Эта дата уже в прошлом 🙂 Введите дату заезда ещё раз:"
        )
        return CHECKIN
    context.user_data["checkin"] = checkin
    await update.message.reply_text(
        f"2️⃣ Дата выезда (минимум {config.MIN_NIGHTS} ночи, формат ДД.ММ.ГГГГ):"
    )
    return CHECKOUT


async def get_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    checkout = parse_date(update.message.text)
    checkin: date = context.user_data["checkin"]
    if checkout is None:
        await update.message.reply_text(
            "Не получилось разобрать дату. Введите в формате ДД.ММ.ГГГГ:"
        )
        return CHECKOUT
    nights = pricing.nights_between(checkin, checkout)
    if nights < config.MIN_NIGHTS:
        min_checkout = checkin + timedelta(days=config.MIN_NIGHTS)
        await update.message.reply_text(
            f"Минимальный срок бронирования — {config.MIN_NIGHTS} ночи. "
            f"Введите дату выезда не раньше {min_checkout.strftime('%d.%m.%Y')}:"
        )
        return CHECKOUT
    if nights > config.MAX_NIGHTS:
        await update.message.reply_text(
            "Получился слишком долгий срок — проверьте дату выезда:"
        )
        return CHECKOUT
    context.user_data["checkout"] = checkout
    await update.message.reply_text(
        f"3️⃣ Сколько домиков бронируем? (всего их {config.TOTAL_HOUSES})",
        reply_markup=HOUSES_KEYBOARD,
    )
    return HOUSES


async def get_houses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.isdigit() or not (1 <= int(text) <= config.TOTAL_HOUSES):
        await update.message.reply_text(
            f"Выберите от 1 до {config.TOTAL_HOUSES} — кнопками ниже:",
            reply_markup=HOUSES_KEYBOARD,
        )
        return HOUSES
    houses = int(text)
    context.user_data["houses"] = houses
    max_guests = houses * config.MAX_GUESTS_PER_HOUSE
    await update.message.reply_text(
        f"4️⃣ Сколько всего гостей приедет? "
        f"(до {config.MAX_GUESTS_PER_HOUSE} на домик — значит, максимум {max_guests})",
        reply_markup=ReplyKeyboardRemove(),
    )
    return GUESTS


async def get_guests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    houses = context.user_data.get("houses", 1)
    max_guests = houses * config.MAX_GUESTS_PER_HOUSE
    if not text.isdigit() or int(text) < 1:
        await update.message.reply_text("Введите число гостей, например 4:")
        return GUESTS
    if int(text) > max_guests:
        await update.message.reply_text(
            f"В один домик заселяется максимум {config.MAX_GUESTS_PER_HOUSE} гостя. "
            f"Для {houses} домик(ов) это до {max_guests} гостей.\n"
            "Введите число гостей ещё раз (или вернитесь и увеличьте число "
            "домиков — /book):"
        )
        return GUESTS
    context.user_data["guests"] = int(text)
    await update.message.reply_text(
        "5️⃣ Едете с питомцем? 🐾", reply_markup=YES_NO_KEYBOARD
    )
    return PET


async def get_pet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip().capitalize()
    if answer not in ("Да", "Нет"):
        await update.message.reply_text(
            "Ответьте кнопками «Да» или «Нет»:", reply_markup=YES_NO_KEYBOARD
        )
        return PET
    context.user_data["pet"] = answer
    await update.message.reply_text(
        "6️⃣ Нужен ли трансфер? 🚕", reply_markup=YES_NO_KEYBOARD
    )
    return TRANSFER


async def get_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip().capitalize()
    if answer not in ("Да", "Нет"):
        await update.message.reply_text(
            "Ответьте кнопками «Да» или «Нет»:", reply_markup=YES_NO_KEYBOARD
        )
        return TRANSFER
    context.user_data["transfer"] = answer
    await update.message.reply_text(
        "7️⃣ Ваше имя и фамилия:", reply_markup=ReplyKeyboardRemove()
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("Пожалуйста, укажите имя и фамилию:")
        return NAME
    context.user_data["name"] = name
    await update.message.reply_text(
        "8️⃣ Контактный телефон — кнопкой ниже или вручную:",
        reply_markup=PHONE_KEYBOARD,
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
    if sum(c.isdigit() for c in phone) < 7:
        await update.message.reply_text(
            "Похоже, номер неполный. Введите телефон ещё раз:"
        )
        return PHONE
    context.user_data["phone"] = phone

    # Считаем стоимость
    checkin: date = context.user_data["checkin"]
    checkout: date = context.user_data["checkout"]
    houses: int = context.user_data["houses"]
    context.user_data["total"] = pricing.calc_total(checkin, checkout, houses)
    context.user_data["prepay"] = pricing.calc_prepayment(checkin, houses)

    user = update.effective_user
    context.user_data["username"] = user.username
    context.user_data["telegram_id"] = user.id

    summary = format_booking(context.user_data)
    await update.message.reply_text(
        "Проверьте бронь:\n\n"
        f"{summary}\n\n"
        "⚠️ Наличие свободных домиков подтвердит менеджер после предоплаты.\n\n"
        "Для подтверждения нужна предоплата за 1 сутки — "
        f"{context.user_data['prepay']} ₽. Продолжаем?",
        reply_markup=CONFIRM_KEYBOARD,
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.startswith("❌"):
        return await cancel(update, context)
    if not text.startswith("✅"):
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки ниже.", reply_markup=CONFIRM_KEYBOARD
        )
        return CONFIRM

    prepay = context.user_data["prepay"]
    await update.message.reply_html(
        f"{config.PAYMENT_DETAILS}\n\n"
        f"💳 Сумма предоплаты: <b>{prepay} ₽</b>\n\n"
        "После перевода пришлите сюда <b>скриншот чека</b> 📸 — "
        "и бронь уйдёт менеджеру на подтверждение.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return SCREENSHOT


async def get_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    if message.photo:
        file_id = message.photo[-1].file_id
        is_photo = True
    elif message.document and (message.document.mime_type or "").startswith("image/"):
        file_id = message.document.file_id
        is_photo = False
    else:
        await update.message.reply_text(
            "Пришлите, пожалуйста, скриншот чека картинкой 📸"
        )
        return SCREENSHOT

    data = dict(context.user_data)
    data["submitted_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")
    body = format_booking(data)

    delivered = True
    try:
        await context.bot.send_message(chat_id=config.OWNER_CHAT_ID, text=body)
        if is_photo:
            await context.bot.send_photo(
                chat_id=config.OWNER_CHAT_ID,
                photo=file_id,
                caption="📸 Чек предоплаты",
            )
        else:
            await context.bot.send_document(
                chat_id=config.OWNER_CHAT_ID,
                document=file_id,
                caption="📸 Чек предоплаты",
            )
    except Exception:
        logger.exception("Не удалось отправить бронь менеджеру")
        delivered = False

    # Автодобавление в RealtyCalendar (заработает после получения API-токена)
    realty_calendar.create_booking(data)

    if delivered:
        await update.message.reply_html(
            "🎉 Спасибо! Бронь и чек отправлены менеджеру.\n\n"
            "Менеджер проверит оплату и наличие свободных домиков и свяжется "
            "с вами для подтверждения.\n"
            f"📞 Связь: {config.PHONE_FOR_GUESTS}\n\n"
            "🛂 Обязательно посмотрите правила пересечения границы РФ–Абхазия "
            "и советы путешественникам — кнопка внизу 👇\n\n"
            "Хорошего отдыха! 🌊",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
    else:
        await update.message.reply_text(
            "⚠️ Не удалось отправить бронь автоматически. Пожалуйста, "
            f"позвоните менеджеру напрямую: {config.PHONE_FOR_GUESTS}",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Бронирование отменено. Начать заново — кнопка внизу 👇",
        reply_markup=MAIN_MENU_KEYBOARD,
    )
    return ConversationHandler.END


async def _post_init(application: Application) -> None:
    """Заполняет синее меню команд Telegram (кнопка «Меню» слева от поля ввода)."""
    from telegram import BotCommand

    await application.bot.set_my_commands(
        [
            BotCommand("book", "🔑 Забронировать домик"),
            BotCommand("photos", "📷 Фото домиков"),
            BotCommand("prices", "💰 Цены"),
            BotCommand("about", "🏡 О доме"),
            BotCommand("border", "🛂 Граница РФ–Абхазия"),
            BotCommand("tips", "🗺 Советы путешественнику"),
            BotCommand("cancel", "❌ Отменить оформление"),
        ]
    )


def build_application() -> Application:
    application = (
        Application.builder().token(config.BOT_TOKEN).post_init(_post_init).build()
    )

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("book", book),
            MessageHandler(filters.Text([BTN_BOOK]), book),
        ],
        states={
            CHECKIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_checkin)],
            CHECKOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_checkout)],
            HOUSES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_houses)],
            GUESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_guests)],
            PET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pet)],
            TRANSFER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_transfer)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
            SCREENSHOT: [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, get_screenshot),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_screenshot),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    # Админский режим загрузки фото (только для админов/менеджера)
    photos_conv = ConversationHandler(
        entry_points=[CommandHandler("addphotos", add_photos)],
        states={
            ADDING_PHOTOS: [
                MessageHandler(filters.PHOTO, receive_admin_photo),
                CommandHandler("donephotos", done_photos),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", done_photos),
            CommandHandler("donephotos", done_photos),
        ],
        allow_reentry=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("prices", prices))
    application.add_handler(CommandHandler("border", border))
    application.add_handler(CommandHandler("tips", tips))
    application.add_handler(CommandHandler("photos", show_photos))
    application.add_handler(CommandHandler("clearphotos", clear_photos))
    # Кнопки меню — регистрируются до диалога, чтобы работать в любой момент
    application.add_handler(MessageHandler(filters.Text([BTN_PHOTOS]), show_photos))
    application.add_handler(MessageHandler(filters.Text([BTN_PRICES]), prices))
    application.add_handler(MessageHandler(filters.Text([BTN_ABOUT]), about))
    application.add_handler(MessageHandler(filters.Text([BTN_BORDER]), border))
    application.add_handler(MessageHandler(filters.Text([BTN_TIPS]), tips))
    application.add_handler(photos_conv)
    application.add_handler(conv)
    return application


def main() -> None:
    config.validate()

    # На новых версиях Python (3.12+/3.14) событийный цикл в главном потоке
    # может отсутствовать — создаём явно, иначе run_polling падает.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    application = build_application()
    logger.info("Бот бронирования запущен. Ожидание сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
