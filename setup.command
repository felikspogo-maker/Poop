#!/bin/bash
# Настройка бота в один клик — запускается двойным щелчком в Finder.

cd "$(dirname "$0")" || exit 1

echo "=========================================="
echo "  Настройка бота «Россия Земля 2026»"
echo "=========================================="
echo

# 1. Проверяем Python
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 не найден."
  echo "Установите его с https://www.python.org/downloads/ и запустите этот файл снова."
  echo
  read -n 1 -s -r -p "Нажмите любую клавишу для выхода..."
  exit 1
fi
echo "✅ Python найден: $(python3 --version)"
echo

# 2. Виртуальное окружение
if [ ! -d "venv" ]; then
  echo "📦 Создаю виртуальное окружение..."
  python3 -m venv venv
fi

# 3. Зависимости
echo "📥 Устанавливаю зависимости (может занять минуту)..."
./venv/bin/pip install --quiet --upgrade pip
./venv/bin/pip install --quiet -r requirements.txt
echo "✅ Зависимости установлены."
echo

# 4. Настройки .env
SKIP_ENV=""
if [ -f ".env" ]; then
  echo "⚠️  Файл настроек .env уже существует."
  read -r -p "Ввести настройки заново и перезаписать? (y/n): " ans
  if [ "$ans" != "y" ]; then
    echo "Оставляю текущие настройки."
    SKIP_ENV=1
  fi
  echo
fi

if [ -z "$SKIP_ENV" ]; then
  echo "Введите настройки бота (см. SETUP-macbook.md, если не знаете, где взять):"
  echo
  read -r -p "1) Токен бота (от @BotFather): " BOT_TOKEN
  read -r -p "2) ID организатора (от @userinfobot): " ADMIN_CHAT_ID
  read -r -p "3) ID Google-таблицы (из ссылки на таблицу): " GOOGLE_SHEET_ID

  cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_CHAT_ID=$ADMIN_CHAT_ID
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID=$GOOGLE_SHEET_ID
WORKSHEET_NAME=Участницы
EOF
  echo
  echo "✅ Настройки сохранены в файл .env"
fi
echo

# 5. Ключ Google
if [ -f "credentials.json" ]; then
  echo "✅ Ключ Google (credentials.json) на месте."
else
  echo "🔑 Файл credentials.json не найден."
  DL=$(ls -t "$HOME/Downloads"/*.json 2>/dev/null | head -n 1)
  if [ -n "$DL" ]; then
    echo "В папке «Загрузки» найден возможный ключ:"
    echo "   $DL"
    read -r -p "Скопировать его сюда как credentials.json? (y/n): " ans
    if [ "$ans" = "y" ]; then
      cp "$DL" credentials.json
      echo "✅ Скопировано."
    fi
  else
    echo "Скачайте ключ сервисного аккаунта из Google Cloud (SETUP-macbook.md, Часть 3)"
    echo "и положите файл в эту папку под именем credentials.json."
  fi
fi

echo
echo "=========================================="
echo "  Готово! Для запуска — файл start.command"
echo "=========================================="
echo
read -n 1 -s -r -p "Нажмите любую клавишу, чтобы закрыть..."
