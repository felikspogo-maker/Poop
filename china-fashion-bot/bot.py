"""Телеграм-бот кастинга моделей China Fashion Week 2027.

Бот проводит кандидата по анкете (с прогрессом и возможностью исправить любой
пункт перед отправкой), собирает фото и пересылает анкету организаторам.
Организаторы прямо под анкетой отмечают решение; при одобрении кандидат
получает уведомление. Черновики анкет переживают перезапуск бота.
"""

import asyncio
import html
import logging
import warnings
from datetime import datetime

from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)
from telegram.warnings import PTBUserWarning

import config

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=PTBUserWarning)  # смешанные кнопки в анкете — так и задумано
logger = logging.getLogger(__name__)

(CONSENT, NAME, AGE, CITY, HEIGHT, SIZE, EXPERIENCE, INSTAGRAM, TELEGRAM, PHONE, PHOTOS, REVIEW, EDIT_PICK) = range(13)

# --- Кнопки ---
BTN_APPLY = "📝 Подать анкету"
BTN_ABOUT = "✨ О кастинге"
BTN_SNAPS = "📸 Как сделать фото"
BTN_STATUS = "📋 Моя анкета"
BTN_CONTACT = "💬 Связаться"
BTN_AGREE = "✅ Согласен(на)"
BTN_DISAGREE = "❌ Не согласен(на)"
BTN_NO_EXP = "Нет опыта — хочу начать"
BTN_NO_INSTA = "Нет Instagram"
BTN_DONE = "✅ Готово"
BTN_CANCEL = "❌ Отменить анкету"


def _kb(rows: list[list], one_time: bool = True) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=one_time)


MAIN_MENU = _kb([[BTN_APPLY], [BTN_ABOUT, BTN_SNAPS], [BTN_STATUS, BTN_CONTACT]], one_time=False)
CONSENT_KB = _kb([[BTN_AGREE], [BTN_DISAGREE]])
SIZE_KB = _kb([config.CLOTHING_SIZES[:3], config.CLOTHING_SIZES[3:]])
EXP_KB = _kb([[BTN_NO_EXP]])
INSTA_KB = _kb([[BTN_NO_INSTA]])
PHONE_KB = _kb([[KeyboardButton("📞 Отправить мой номер", request_contact=True)]])
PHOTOS_KB = _kb([[BTN_DONE], [BTN_CANCEL]], one_time=False)

TOTAL_STEPS = 10
# Ключ поля → (номер шага, подпись в анкете, состояние)
FIELDS = {
    "name": (1, "ФИО", NAME),
    "age": (2, "Возраст", AGE),
    "city": (3, "Город", CITY),
    "height": (4, "Рост", HEIGHT),
    "size": (5, "Размер одежды", SIZE),
    "experience": (6, "Опыт показов", EXPERIENCE),
    "instagram": (7, "Instagram", INSTAGRAM),
    "telegram": (8, "Telegram", TELEGRAM),
    "phone": (9, "Телефон", PHONE),
    "photos": (10, "Фото", PHOTOS),
}
ORDER = list(FIELDS)

# Задержка, после которой бот отвечает на пачку фото (альбом приходит частями)
_photo_tasks: dict[int, asyncio.Task] = {}


def _progress(step: int) -> str:
    return f"<i>Шаг {step} из {TOTAL_STEPS}</i>  {'▰' * step}{'▱' * (TOTAL_STEPS - step)}\n\n"


def _contact_line() -> str:
    return f"\n\n💬 Вопросы: {config.CONTACT_INFO}" if config.CONTACT_INFO else ""


WELCOME = (
    f"🇨🇳 <b>{config.EVENT_NAME}</b> — кастинг моделей\n\n"
    f"📅 <b>{config.EVENT_DATES}</b> · 📍 <b>{config.EVENT_PLACE}</b>\n\n"
    "Тропический остров, шикарный отель, подиум и <b>дизайнеры мирового уровня</b> — "
    "и, возможно, именно вы выйдете на их показ.\n\n"
    "Анкета занимает около <b>5 минут</b>: 10 коротких шагов и несколько фото. "
    "Перед отправкой можно проверить и исправить любой пункт.\n\n"
    f"Нажмите «{BTN_APPLY}», чтобы начать."
)

ABOUT = (
    f"✨ <b>{config.EVENT_NAME}</b>\n\n"
    f"📅 <b>Когда:</b> {config.EVENT_DATES}\n"
    f"📍 <b>Где:</b> {config.EVENT_PLACE}, в шикарном отеле\n"
    "👗 <b>Кто:</b> дизайнеры мирового уровня и их коллекции\n\n"
    "Мы ищем моделей для показов недели моды: девушек и парней, "
    "с опытом и без — главное, желание работать на подиуме.\n\n"
    "<b>Как проходит отбор</b>\n"
    "1. Вы заполняете анкету и присылаете фото\n"
    "2. Организаторы смотрят анкеты\n"
    "3. Подходящих кандидатов приглашают на кастинг — бот пришлёт уведомление, "
    "а организаторы свяжутся с вами\n\n"
    "Опыт показов не обязателен — новые лица тоже приветствуются."
    f"{_contact_line()}"
)

SNAPS = (
    "📸 <b>Как сделать фото для кастинга (снепы)</b>\n\n"
    "Модельные агентства смотрят не на обработку, а на вас настоящих:\n\n"
    "• <b>Дневной свет</b> — у окна или на улице, без вспышки\n"
    "• <b>Минимум макияжа</b>, волосы собраны или аккуратно распущены\n"
    "• <b>Простая облегающая одежда</b> — чёрная или белая, без принтов\n"
    "• <b>Без фильтров</b> и ретуши, без солнцезащитных очков\n"
    "• <b>Однотонный фон</b> — стена, дверь\n\n"
    "<b>Какие кадры нужны</b>\n"
    "1. Портрет анфас\n"
    "2. Портрет в профиль\n"
    "3. В полный рост анфас\n"
    "4. В полный рост в профиль\n"
    "5. Любое ваше лучшее фото — с показа или съёмки\n\n"
    f"Пришлите от {config.PHOTOS_MIN} до {config.PHOTOS_MAX} фото."
)


# =====================================================================
# Общие команды
# =====================================================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(WELCOME, reply_markup=MAIN_MENU)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(ABOUT, reply_markup=MAIN_MENU)


async def snaps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(SNAPS, reply_markup=MAIN_MENU)


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        f"💬 По всем вопросам: {config.CONTACT_INFO}"
        if config.CONTACT_INFO
        else "💬 Напишите ваш вопрос прямо сюда, в анкете — организаторы увидят его вместе с заявкой. "
        "А если анкета уже отправлена, организаторы сами свяжутся с вами."
    )
    await update.message.reply_text(text, reply_markup=MAIN_MENU)


async def my_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rec = context.bot_data.get("applicants", {}).get(update.effective_user.id)
    if not rec:
        await update.message.reply_text(
            f"Вы ещё не отправляли анкету. Нажмите «{BTN_APPLY}», чтобы начать.", reply_markup=MAIN_MENU
        )
        return
    status = {"new": "⏳ на рассмотрении", "ok": "✅ вы приглашены на кастинг", "no": "⏳ на рассмотрении"}
    await update.message.reply_html(
        f"📋 Ваша анкета <b>№{rec['num']:04d}</b> от {rec['date']}\n"
        f"Статус: {status.get(rec['status'], '⏳ на рассмотрении')}",
        reply_markup=MAIN_MENU,
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Статистика — только для организаторов."""
    if update.effective_user.id not in config.ADMIN_CHAT_IDS:
        return
    apps = context.bot_data.get("applicants", {})
    ok = sum(1 for r in apps.values() if r["status"] == "ok")
    no = sum(1 for r in apps.values() if r["status"] == "no")
    await update.message.reply_html(
        f"📊 <b>Анкеты {config.EVENT_NAME}</b>\n\n"
        f"Всего: <b>{context.bot_data.get('counter', 0)}</b> (от {len(apps)} человек)\n"
        f"✅ Приглашены: {ok}\n❌ Отклонены: {no}\n⏳ Без решения: {len(apps) - ok - no}"
    )


# =====================================================================
# Анкета
# =====================================================================


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    prev = context.bot_data.get("applicants", {}).get(update.effective_user.id)
    note = (
        f"\n\nℹ️ Вы уже отправляли анкету №{prev['num']:04d}. Новая анкета дополнит её — "
        "организаторы увидят обе."
        if prev
        else ""
    )
    await update.message.reply_html(
        f"📝 <b>Начинаем!</b> Отменить можно в любой момент — /cancel{note}\n\n"
        "Сначала нужно ваше <b>согласие на обработку персональных данных</b>: "
        f"анкета и фото передаются организаторам {config.EVENT_NAME} только для отбора на кастинг "
        "(ФЗ-152 «О персональных данных»). Если вам меньше 18 лет, согласие даёт родитель "
        "или законный представитель.\n\nВы согласны?",
        reply_markup=CONSENT_KB,
    )
    return CONSENT


async def get_consent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text != BTN_AGREE:
        context.user_data.clear()
        await update.message.reply_text(
            "Без согласия анкету отправить нельзя. Если передумаете — нажмите «📝 Подать анкету».",
            reply_markup=MAIN_MENU,
        )
        return ConversationHandler.END
    context.user_data["consent"] = datetime.now().strftime("%d.%m.%Y %H:%M")
    return await ask("name", update, context)


async def ask(key: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Задаёт вопрос по полю анкеты и возвращает его состояние."""
    step, _, state = FIELDS[key]
    msg = update.effective_message
    p = _progress(step)
    if key == "name":
        await msg.reply_html(p + "👤 Ваши <b>фамилия, имя и отчество</b>:", reply_markup=ReplyKeyboardRemove())
    elif key == "age":
        await msg.reply_html(p + "🎂 Сколько вам <b>полных лет</b>?", reply_markup=ReplyKeyboardRemove())
    elif key == "city":
        await msg.reply_html(p + "🏙 Из какого вы <b>города</b>?", reply_markup=ReplyKeyboardRemove())
    elif key == "height":
        await msg.reply_html(p + "📏 Ваш <b>рост</b> в сантиметрах (например, 176):", reply_markup=ReplyKeyboardRemove())
    elif key == "size":
        await msg.reply_html(p + "👗 Ваш <b>размер одежды</b> — выберите или напишите свой:", reply_markup=SIZE_KB)
    elif key == "experience":
        await msg.reply_html(
            p + "🌟 Расскажите об <b>опыте дефиле и участия в показах</b>: где, когда, с какими брендами "
            "или агентствами работали.\n\nЕсли опыта нет — нажмите кнопку ниже, это не помешает.",
            reply_markup=EXP_KB,
        )
    elif key == "instagram":
        await msg.reply_html(p + "📷 Ваш <b>Instagram</b> — ник или ссылка:", reply_markup=INSTA_KB)
    elif key == "telegram":
        user = update.effective_user
        if user and user.username and not context.user_data.get("editing"):
            context.user_data["telegram"] = f"@{user.username}"   # ник есть — не спрашиваем
            return await advance("telegram", update, context)
        await msg.reply_html(
            p + "💬 Ваш <b>Telegram</b> для связи — @ник или номер, к которому привязан Telegram:",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif key == "phone":
        await msg.reply_html(p + "📞 Ваш <b>номер телефона</b> — кнопкой ниже или вручную:", reply_markup=PHONE_KB)
    elif key == "photos":
        context.user_data["photos"] = []
        await msg.reply_html(
            p + f"📸 Пришлите <b>от {config.PHOTOS_MIN} до {config.PHOTOS_MAX} фото</b> — можно сразу альбомом.\n\n"
            "Лучше всего: портрет анфас и в профиль, в полный рост анфас и в профиль, дневной свет, "
            f"без фильтров. Подробнее — «{BTN_SNAPS}» в меню.\n\n"
            f"Когда закончите — нажмите «{BTN_DONE}».",
            reply_markup=PHOTOS_KB,
        )
    return state


async def advance(key: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """После ответа: к следующему вопросу или, если исправляли пункт, — обратно к проверке."""
    if context.user_data.pop("editing", False):
        return await show_review(update, context)
    nxt = ORDER.index(key) + 1
    return await ask(ORDER[nxt], update, context) if nxt < len(ORDER) else await show_review(update, context)


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = " ".join(update.message.text.split())
    if len(name.split()) < 2 or any(ch.isdigit() for ch in name):
        await update.message.reply_text("Укажите, пожалуйста, фамилию и имя полностью (лучше и отчество):")
        return NAME
    context.user_data["name"] = name.title() if name.islower() else name
    return await advance("name", update, context)


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.isdigit() or not config.AGE_MIN <= int(text) <= config.AGE_MAX:
        await update.message.reply_text(f"Напишите возраст числом, например 21 (от {config.AGE_MIN} до {config.AGE_MAX}):")
        return AGE
    context.user_data["age"] = int(text)
    return await advance("age", update, context)


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["city"] = update.message.text.strip()
    return await advance("city", update, context)


async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    digits = "".join(ch for ch in update.message.text if ch.isdigit())
    if not digits or not config.HEIGHT_MIN <= int(digits) <= config.HEIGHT_MAX:
        await update.message.reply_text("Напишите рост в сантиметрах числом, например 176:")
        return HEIGHT
    context.user_data["height"] = int(digits)
    return await advance("height", update, context)


async def get_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["size"] = update.message.text.strip()
    return await advance("size", update, context)


async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["experience"] = "Нет опыта" if text == BTN_NO_EXP else text
    return await advance("experience", update, context)


async def get_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == BTN_NO_INSTA:
        context.user_data["instagram"] = "—"
    else:
        nick = text.split("instagram.com/")[-1].split("?")[0].strip("/ @")
        context.user_data["instagram"] = f"@{nick}" if nick and " " not in nick else text
    return await advance("instagram", update, context)


async def get_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["telegram"] = text if text.startswith(("@", "+")) or text[:1].isdigit() else f"@{text}"
    return await advance("telegram", update, context)


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = (update.message.text or "").strip()
        if sum(ch.isdigit() for ch in phone) < 10:
            await update.message.reply_text("Похоже, номер неполный. Пришлите его кнопкой или вручную, например +7 900 123-45-67:")
            return PHONE
    context.user_data["phone"] = phone if phone.startswith("+") or not phone[:1].isdigit() else f"+{phone}"
    return await advance("phone", update, context)


async def _photo_ack(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отвечает один раз на всю пачку фото, а не на каждое."""
    await asyncio.sleep(1.5)
    n = len(context.user_data.get("photos", []))
    if n >= config.PHOTOS_MAX:
        text = f"📸 Получено {n} фото — это максимум. Нажмите «{BTN_DONE}»."
    elif n >= config.PHOTOS_MIN:
        text = f"📸 Получено фото: {n}. Можно прислать ещё (до {config.PHOTOS_MAX}) или нажать «{BTN_DONE}»."
    else:
        text = f"📸 Получено фото: {n}. Нужно ещё минимум {config.PHOTOS_MIN - n}."
    await context.bot.send_message(chat_id, text, reply_markup=PHOTOS_KB)


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photos: list[str] = context.user_data.setdefault("photos", [])
    msg = update.message
    if msg.photo:
        fid = msg.photo[-1].file_id
    elif msg.document and (msg.document.mime_type or "").startswith("image/"):
        fid = msg.document.file_id
        context.user_data.setdefault("doc_photos", []).append(fid)
    else:
        await msg.reply_text("Нужны именно фотографии 🙂")
        return PHOTOS
    if len(photos) < config.PHOTOS_MAX:
        photos.append(fid)
    uid = update.effective_user.id
    if (t := _photo_tasks.get(uid)) and not t.done():
        t.cancel()
    _photo_tasks[uid] = asyncio.create_task(_photo_ack(update.effective_chat.id, context))
    return PHOTOS


async def photos_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    n = len(context.user_data.get("photos", []))
    if n < config.PHOTOS_MIN:
        await update.message.reply_text(f"Пока {n} фото — пришлите ещё минимум {config.PHOTOS_MIN - n}.", reply_markup=PHOTOS_KB)
        return PHOTOS
    if (t := _photo_tasks.pop(update.effective_user.id, None)) and not t.done():
        t.cancel()
    context.user_data.pop("editing", None)
    return await show_review(update, context)


async def photos_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f"Пришлите фото или нажмите «{BTN_DONE}», когда закончите.", reply_markup=PHOTOS_KB)
    return PHOTOS


# --- Проверка и исправления ---


def _age(n) -> str:
    if not isinstance(n, int):
        return "—"
    word = "год" if n % 10 == 1 and n % 100 != 11 else "года" if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else "лет"
    return f"{n} {word}"


def _summary(d: dict, header: str) -> str:
    e = lambda v: html.escape(str(v))
    return (
        f"{header}\n\n"
        f"👤 <b>{e(d.get('name', '—'))}</b>\n"
        f"🎂 {e(_age(d.get('age')))} · 🏙 {e(d.get('city', '—'))}\n"
        f"📏 Рост: {e(d.get('height', '—'))} см · 👗 Размер: {e(d.get('size', '—'))}\n"
        f"🌟 Опыт: {e(d.get('experience', '—'))}\n"
        f"📷 Instagram: {e(d.get('instagram', '—'))}\n"
        f"💬 Telegram: {e(d.get('telegram', '—'))}\n"
        f"📞 Телефон: {e(d.get('phone', '—'))}\n"
        f"📸 Фото: {len(d.get('photos', []))} шт"
    )


REVIEW_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Всё верно — отправить", callback_data="rv:send")],
    [InlineKeyboardButton("✏️ Исправить пункт", callback_data="rv:edit"),
     InlineKeyboardButton("🔄 Заново", callback_data="rv:restart")],
])


async def show_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.effective_message.reply_text("Почти готово!", reply_markup=ReplyKeyboardRemove())
    await update.effective_message.reply_html(
        _summary(context.user_data, "🔎 <b>Проверьте анкету</b>"), reply_markup=REVIEW_KB
    )
    return REVIEW


async def review_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    action = q.data.split(":")[1]
    if action == "send":
        await q.edit_message_reply_markup(None)
        return await submit(update, context)
    if action == "restart":
        await q.edit_message_reply_markup(None)
        consent = context.user_data.get("consent")
        context.user_data.clear()
        context.user_data["consent"] = consent
        return await ask("name", update, context)
    rows, row = [], []
    for key, (_, label, _) in FIELDS.items():
        row.append(InlineKeyboardButton(label, callback_data=f"ed:{key}"))
        if len(row) == 2:
            rows.append(row); row = []
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="ed:back")])
    await q.edit_message_reply_markup(InlineKeyboardMarkup(rows))
    return EDIT_PICK


async def edit_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    key = q.data.split(":")[1]
    if key == "back":
        await q.edit_message_reply_markup(REVIEW_KB)
        return REVIEW
    await q.edit_message_reply_markup(None)
    context.user_data["editing"] = True
    return await ask(key, update, context)


# --- Отправка ---


def _admin_kb(uid: int, num: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Пригласить на кастинг", callback_data=f"adm:ok:{uid}:{num}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"adm:no:{uid}:{num}"),
    ]])


async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    d = context.user_data
    user = update.effective_user
    bd = context.bot_data
    bd["counter"] = num = bd.get("counter", 0) + 1
    prev = bd.setdefault("applicants", {}).get(user.id)
    bd["applicants"][user.id] = {"num": num, "date": datetime.now().strftime("%d.%m.%Y"), "status": "new", "name": d.get("name")}

    header = f"🌟 <b>Новая анкета №{num:04d}</b> — {html.escape(config.EVENT_NAME)}"
    if prev:
        header += f"\n<i>Повторная: ранее анкета №{prev['num']:04d}</i>"
    text = _summary(d, header) + (
        f"\n\n🆔 <a href=\"tg://user?id={user.id}\">открыть профиль</a> · ID {user.id}\n"
        f"✅ Согласие на обработку данных: {d.get('consent')}"
    )

    cards: list[tuple[int, int]] = []
    photos = d.get("photos", [])
    docs = set(d.get("doc_photos", []))
    for chat_id in config.ADMIN_CHAT_IDS:
        try:
            album = [InputMediaPhoto(fid) for fid in photos if fid not in docs]
            for i in range(0, len(album), 10):
                await context.bot.send_media_group(chat_id, album[i:i + 10])
            for fid in [f for f in photos if f in docs]:
                await context.bot.send_document(chat_id, fid)
            m = await context.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=_admin_kb(user.id, num))
            cards.append((chat_id, m.message_id))
        except TelegramError:
            logger.exception("Не удалось отправить анкету №%s администратору %s", num, chat_id)
    bd.setdefault("cards", {})[num] = cards

    if not cards:
        await update.effective_message.reply_text(
            "😔 Не получилось передать анкету организаторам. Попробуйте ещё раз чуть позже.", reply_markup=MAIN_MENU
        )
        if prev:
            bd["applicants"][user.id] = prev
        else:
            bd["applicants"].pop(user.id, None)
        return ConversationHandler.END

    await update.effective_message.reply_html(
        f"🎉 <b>Анкета №{num:04d} отправлена!</b>\n\n"
        "Организаторы посмотрят её и, если ваш типаж подойдёт, пригласят на кастинг — "
        "уведомление придёт сюда, в бот.\n\n"
        f"Статус всегда можно проверить кнопкой «{BTN_STATUS}». Удачи на подиуме! ✨"
        f"{_contact_line()}",
        reply_markup=MAIN_MENU,
    )
    context.user_data.clear()
    return ConversationHandler.END


async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Решение организатора по анкете: отмечается у всех организаторов, при одобрении — уведомление кандидату."""
    q = update.callback_query
    if q.from_user.id not in config.ADMIN_CHAT_IDS:
        await q.answer("Только для организаторов", show_alert=True)
        return
    _, action, uid, num = q.data.split(":")
    uid, num = int(uid), int(num)
    rec = context.bot_data.get("applicants", {}).get(uid)
    who = html.escape(q.from_user.first_name or "организатор")
    if rec and rec["num"] == num and rec["status"] != "new":
        await q.answer("Решение по этой анкете уже принято", show_alert=True)
        return
    if rec and rec["num"] == num:
        rec["status"] = action

    label = f"✅ Приглашена(ён) на кастинг — {who}" if action == "ok" else f"❌ Отклонена — {who}"
    mark = InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data="adm:noop")]])
    for chat_id, msg_id in context.bot_data.get("cards", {}).get(num, []):
        try:
            await context.bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=mark)
        except TelegramError:
            pass

    if action == "ok":
        try:
            await context.bot.send_message(
                uid,
                f"🎉 <b>Поздравляем!</b>\n\nВаша анкета №{num:04d} одобрена — вы приглашены на кастинг "
                f"<b>{html.escape(config.EVENT_NAME)}</b> — {config.EVENT_DATES}, {config.EVENT_PLACE}.\n\n"
                f"Организаторы свяжутся с вами в ближайшее время и расскажут все детали. "
                f"Держите телефон рядом! ✨{_contact_line()}",
                parse_mode="HTML",
            )
            await q.answer("Кандидат получил приглашение")
        except TelegramError:
            await q.answer("Отмечено, но кандидат закрыл бота — свяжитесь с ним по телефону", show_alert=True)
    else:
        await q.answer("Отмечено")


async def admin_noop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer("Решение уже принято")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.effective_message.reply_text(
        "Анкета отменена. Вернуться можно в любой момент — «📝 Подать анкету».", reply_markup=MAIN_MENU
    )
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Ошибка при обработке обновления", exc_info=context.error)


async def post_init(app: Application) -> None:
    """Меню команд и описание бота — видно до нажатия «Старт»."""
    try:
        await app.bot.set_my_commands([
            BotCommand("start", "Главное меню"),
            BotCommand("apply", "Подать анкету"),
            BotCommand("cancel", "Отменить анкету"),
        ])
        await app.bot.set_my_short_description(
            f"Кастинг моделей {config.EVENT_NAME} · {config.EVENT_DATES}, Санья. Анкета за 5 минут."
        )
        await app.bot.set_my_description(
            f"🇨🇳 Кастинг моделей {config.EVENT_NAME}\n"
            f"📅 {config.EVENT_DATES} · 📍 {config.EVENT_PLACE}\n"
            "Шикарный отель и дизайнеры мирового уровня.\n\n"
            "Заполните короткую анкету и пришлите фото — организаторы рассмотрят её "
            "и пригласят подходящих кандидатов на кастинг. Нажмите «Старт»."
        )
    except TelegramError:
        logger.warning("Не удалось обновить описание бота", exc_info=True)


def build_application() -> Application:
    app = (
        Application.builder()
        .token(config.BOT_TOKEN)
        .persistence(PicklePersistence(filepath=config.PERSISTENCE_FILE))
        .post_init(post_init)
        .build()
    )
    text = filters.TEXT & ~filters.COMMAND & ~filters.Regex(f"^{BTN_CANCEL}$")
    form = ConversationHandler(
        entry_points=[CommandHandler("apply", apply), MessageHandler(filters.Regex(f"^{BTN_APPLY}$"), apply)],
        states={
            CONSENT: [MessageHandler(text, get_consent)],
            NAME: [MessageHandler(text, get_name)],
            AGE: [MessageHandler(text, get_age)],
            CITY: [MessageHandler(text, get_city)],
            HEIGHT: [MessageHandler(text, get_height)],
            SIZE: [MessageHandler(text, get_size)],
            EXPERIENCE: [MessageHandler(text, get_experience)],
            INSTAGRAM: [MessageHandler(text, get_instagram)],
            TELEGRAM: [MessageHandler(text, get_telegram)],
            PHONE: [MessageHandler(filters.CONTACT, get_phone), MessageHandler(text, get_phone)],
            PHOTOS: [
                MessageHandler(filters.Regex(f"^{BTN_DONE}$"), photos_done),
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, get_photo),
                MessageHandler(text, photos_text),
            ],
            REVIEW: [CallbackQueryHandler(review_action, pattern=r"^rv:")],
            EDIT_PICK: [CallbackQueryHandler(edit_pick, pattern=r"^ed:")],
        },
        fallbacks=[CommandHandler("cancel", cancel), MessageHandler(filters.Regex(f"^{BTN_CANCEL}$"), cancel)],
        name="form",
        persistent=True,
        allow_reentry=True,
    )
    app.add_handler(form)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ABOUT}$"), about))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_SNAPS}$"), snaps))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_CONTACT}$"), contact))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_STATUS}$"), my_status))
    app.add_handler(CallbackQueryHandler(admin_noop, pattern=r"^adm:noop$"))
    app.add_handler(CallbackQueryHandler(admin_decision, pattern=r"^adm:(ok|no):"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))  # любой другой текст — меню
    app.add_error_handler(error_handler)
    return app


def main() -> None:
    config.validate()
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    app = build_application()
    logger.info("Бот «%s» запущен.", config.EVENT_NAME)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
