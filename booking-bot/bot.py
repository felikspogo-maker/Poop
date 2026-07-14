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

WELCOME = (
    f"🏡 Добро пожаловать в <b>{config.GUESTHOUSE_NAME}</b>!\n"
    f"📍 {config.ADDRESS}\n\n"
    "Здесь можно забронировать уютный домик у моря в Сухуме.\n\n"
    "Команды:\n"
    "• /book — забронировать домик 🔑\n"
    "• /prices — цены 💰\n"
    "• /about — о доме и удобствах 🏡\n"
    "• /border — правила пересечения границы РФ–Абхазия 🛂\n"
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
    await update.message.reply_html(WELCOME)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(info.ABOUT_TEXT)


async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(pricing.price_list_text())


async def border(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        info.BORDER_TEXT, link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(WELCOME)


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
    context.user_data["houses"] = int(text)
    await update.message.reply_text(
        "4️⃣ Сколько всего гостей приедет?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return GUESTS


async def get_guests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.isdigit() or not (1 <= int(text) <= config.MAX_GUESTS):
        await update.message.reply_text("Введите число гостей, например 4:")
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
            "и советы путешественникам — команда /border\n\n"
            "Хорошего отдыха! 🌊"
        )
    else:
        await update.message.reply_text(
            "⚠️ Не удалось отправить бронь автоматически. Пожалуйста, "
            f"позвоните менеджеру напрямую: {config.PHONE_FOR_GUESTS}"
        )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Бронирование отменено. Начать заново — /book",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def build_application() -> Application:
    application = Application.builder().token(config.BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("book", book)],
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

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("prices", prices))
    application.add_handler(CommandHandler("border", border))
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
