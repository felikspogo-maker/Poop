# 🏡 Бот бронирования — «Гостевой дом A-Home» (Сухум, Абхазия)

Телеграм-бот для бронирования домиков: собирает бронь, считает стоимость по
сезонным ценам, принимает предоплату за 1 сутки (перевод/СБП + скриншот чека)
и отправляет бронь менеджеру в Telegram. Интеграция с RealtyCalendar
подключается позже, когда будет получен API-токен.

## Как работает бронь

1. Гость выбирает даты заезда/выезда (минимум 2 ночи), число домиков (1–3)
   и гостей, отмечает питомца и трансфер, оставляет имя и телефон.
2. Бот считает стоимость по сезонам (по каждой ночи отдельно):

   | Сезон | Цена за домик/ночь |
   |---|---|
   | Октябрь – Май | 2700 ₽ |
   | Июнь – Июль | 3700 ₽ |
   | Август | 4200 ₽ |
   | Сентябрь | 3700 ₽ |

3. Предоплата = 1 ночь (по сезону даты заезда) × число домиков. Бот показывает
   реквизиты (Сбер/Т-Банк, СБП), гость переводит и присылает скриншот чека.
4. Бронь + чек уходят менеджеру в Telegram; менеджер подтверждает наличие
   и связывается с гостем. Остаток — при заселении, переводом или наличными.
5. Гостю показываются правила пересечения границы РФ–Абхазия (/border).

## Команды

- `/start`, `/help` — приветствие и список команд
- `/book` — забронировать
- `/photos` — фото домиков
- `/prices` — цены
- `/about` — о доме
- `/border` — граница РФ–Абхазия и предостережения
- `/tips` — куда съездить и памятка путешественнику
- `/cancel` — отменить оформление

### Команды администратора (фото домиков)

Доступны только тем, чьи ID указаны в `ADMIN_IDS`, а также менеджеру
(`OWNER_CHAT_ID`). Фото хранятся как Telegram file_id в `house_photos.json`
(не в git) — файлы на диск не скачиваются.

- `/addphotos` — включить режим загрузки, затем прислать фото (по одной или
  альбомом), в конце `/donephotos`
- `/clearphotos` — очистить галерею

## Структура

```
bot.py             — диалог бронирования и отправка менеджеру
config.py          — настройки (.env), реквизиты, параметры объекта
pricing.py         — сезонные цены и расчёт стоимости
info.py            — тексты: о доме, граница РФ–Абхазия
realty_calendar.py — интеграция с RealtyCalendar (заглушка до получения токена)
deploy/            — systemd-юнит для сервера
```

## Настройка

```bash
cd booking-bot
cp .env.example .env
# впишите BOT_TOKEN (от @BotFather) и OWNER_CHAT_ID (ID Оксаны из @userinfobot)
```

## Запуск локально

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python bot.py
```

## Деплой на сервер (рядом с первым ботом)

Оба бота спокойно живут на одном сервере — это разные процессы и разные токены.

```bash
cd /opt
git clone -b claude/beauty-contest-telegram-bot-etabln \
  https://github.com/felikspogo-maker/Poop.git abkhazia-booking-bot
cd abkhazia-booking-bot/booking-bot
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
nano .env   # BOT_TOKEN и OWNER_CHAT_ID

cp deploy/abkhazia-booking-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now abkhazia-booking-bot
systemctl status abkhazia-booking-bot
```

Логи: `journalctl -u abkhazia-booking-bot -f`

## RealtyCalendar (позже)

1. Запросите API-доступ у поддержки RealtyCalendar из кабинета
   («нужен API для интеграции с чат-ботом»).
2. Токен впишите в `.env`: `RC_API_TOKEN=...`
3. Реализация вызовов — в `realty_calendar.py` (create_booking), сейчас там
   подготовленная заглушка: без токена брони уходят только менеджеру.
