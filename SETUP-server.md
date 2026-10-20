# 🖥 Запуск бота на сервере (24/7)

Инструкция, как перенести бота с мака на сервер, чтобы он работал круглосуточно
и сам перезапускался после сбоев и перезагрузок.

Предполагается **VPS с Ubuntu 22.04/24.04** (Timeweb, Aeza, Beget, Hetzner и
т.п.). Все команды выполняются в терминале сервера — подключение по SSH.

---

## Часть 1. Арендуем сервер

1. Возьмите самый дешёвый VPS (1 CPU, 1 ГБ RAM — с запасом хватает) с
   **Ubuntu 24.04**. Провайдер пришлёт **IP-адрес**, логин (обычно `root`) и
   пароль.
2. Подключитесь к серверу с мака через Терминал:
   ```bash
   ssh root@IP_АДРЕС_СЕРВЕРА
   ```
   Введите пароль (при вводе он не отображается — это нормально).

---

## Часть 2. Ставим нужные программы

На сервере выполните по очереди:

```bash
apt update && apt -y upgrade
apt -y install python3 python3-venv python3-pip git
```

---

## Часть 3. Скачиваем код бота

```bash
cd /opt
git clone -b claude/beauty-contest-telegram-bot-etabln \
  https://github.com/felikspogo-maker/Poop.git russia-earth-bot
cd russia-earth-bot
```

> После слияния Pull request можно клонировать основную ветку без `-b ...`.

Создаём окружение и ставим зависимости:

```bash
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
```

---

## Часть 4. Переносим настройки и ключ Google

Файлы `.env` и `credentials.json` содержат секреты и в репозиторий не входят —
их нужно создать/загрузить на сервер вручную.

### 4.1. Файл `.env`

```bash
cp .env.example .env
nano .env
```
Заполните и сохраните (в nano: `Ctrl+O`, `Enter`, затем `Ctrl+X`):
```
BOT_TOKEN=токен_от_BotFather
ADMIN_CHAT_ID=id_организатора
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID=id_таблицы
WORKSHEET_NAME=Участницы
```

### 4.2. Ключ `credentials.json`

Самый простой способ — скопировать его **с мака** на сервер. Открой **на маке**
новое окно Терминала (не то, где подключён SSH) и выполни:

```bash
scp ~/Desktop/MSMRS/credentials.json root@IP_АДРЕС_СЕРВЕРА:/opt/russia-earth-bot/
```

Проверить, что файл на месте (в SSH-сессии сервера):
```bash
ls -l /opt/russia-earth-bot/credentials.json
```

---

## Часть 5. Настраиваем автозапуск (systemd)

Чтобы бот работал 24/7 и перезапускался сам:

```bash
cp /opt/russia-earth-bot/deploy/russia-earth-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now russia-earth-bot
```

Проверить статус:
```bash
systemctl status russia-earth-bot
```
Зелёная надпись **active (running)** — бот работает. Выйти из просмотра — `q`.

---

## Часть 6. Проверяем

1. Организатор пишет боту `/start` в Telegram.
2. Подайте тестовую заявку через `/apply`.
3. Убедитесь, что заявка пришла организатору и появилась строка в Google-таблице.

Теперь можно закрыть SSH и выключить мак — бот продолжит работать на сервере.

---

## Полезные команды на сервере

```bash
systemctl status russia-earth-bot     # статус
systemctl restart russia-earth-bot    # перезапустить
systemctl stop russia-earth-bot       # остановить
journalctl -u russia-earth-bot -f     # смотреть логи в реальном времени
```

## Как обновить бота после изменений в коде

```bash
cd /opt/russia-earth-bot
git pull
./venv/bin/pip install -r requirements.txt
systemctl restart russia-earth-bot
```

---

## Альтернатива: запуск через Docker

Если предпочитаете Docker (в репозитории есть `Dockerfile`):

```bash
cd /opt/russia-earth-bot
docker build -t russia-earth-bot .
docker run -d --name russia-earth-bot --restart always \
  --env-file .env \
  -v /opt/russia-earth-bot/credentials.json:/app/credentials.json:ro \
  russia-earth-bot
```

---

## Частые проблемы

| Симптом | Решение |
|---|---|
| `systemctl status` показывает `failed` | Смотрите логи: `journalctl -u russia-earth-bot -n 50` |
| `Не задан BOT_TOKEN / ADMIN_CHAT_ID` | Проверьте `.env` (Часть 4.1) |
| `FileNotFoundError: credentials.json` | Файл не загрузился на сервер (Часть 4.2) |
| Ошибка про event loop | На сервере ставьте Python из репозитория Ubuntu (3.12), не 3.14 |
| Нет доступа к Google-таблице | Дайте сервисному аккаунту права редактора (см. SETUP-macbook.md, Часть 4.3) |
