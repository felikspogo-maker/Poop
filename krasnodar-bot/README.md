# 👑 Бот анкет «Мисс и Миссис Краснодарский край 2027»

Телеграм-бот приёма анкет: собирает данные участницы, 5 фото и видео-визитку,
пересылает анкету организаторам в Telegram и дописывает строку в Google-таблицу.

## Анкета

Согласие на обработку данных → проживание в Краснодарском крае → ФИО → город →
возраст → категория → семейное положение → рост (от 165 см) → размер одежды
(40–46) → опыт в конкурсах → телефон → Telegram (если нет @ника) → 5 фото →
видео-визитка → проверка → отправка.

Категории (по возрасту; при пересечении участница выбирает сама):

| Категория | Возраст |
|---|---|
| Юная Мисс | 14–17 |
| Мисс | 18–35 |
| Миссис | 20–45 |

Приём анкет автоматически закрывается после 15 января 2027.

Все параметры (категории, рост, размеры, число фото, обязательность видео,
дедлайн) — в `config.py`.

## Команды

- `/start`, `/info` — о конкурсе
- `/apply` (кнопка «📝 Подать анкету») — заполнить анкету
- `/cancel` — отменить
- `/table` — ссылка на таблицу (только для организаторов)

## Деплой на сервер (Ubuntu 24.04)

```bash
apt update && apt -y install python3 python3-venv git
cd /opt
git clone -b claude/beauty-contest-telegram-bot-etabln \
  https://github.com/felikspogo-maker/Poop.git krasnodar-bot
cd krasnodar-bot/krasnodar-bot
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env
# + положить credentials.json в эту же папку (scp с мака)
cp deploy/krasnodar-bot.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now krasnodar-bot
```

Логи: `journalctl -u krasnodar-bot -f`. Обновление: `git pull && systemctl restart krasnodar-bot`.
