#!/bin/bash
# Запуск бота в один клик — запускается двойным щелчком в Finder.

cd "$(dirname "$0")" || exit 1

if [ ! -d "venv" ]; then
  echo "❌ Бот ещё не настроен. Сначала запустите setup.command."
  echo
  read -n 1 -s -r -p "Нажмите любую клавишу, чтобы закрыть..."
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "❌ Нет файла настроек .env. Запустите setup.command."
  echo
  read -n 1 -s -r -p "Нажмите любую клавишу, чтобы закрыть..."
  exit 1
fi

echo "🚀 Бот запускается..."
echo "   Чтобы остановить — закройте это окно или нажмите Ctrl+C."
echo

./venv/bin/python bot.py

echo
echo "Бот остановлен."
read -n 1 -s -r -p "Нажмите любую клавишу, чтобы закрыть..."
