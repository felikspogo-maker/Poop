# Quick Start Guide

Быстрый старт для разработки Business Consulting App.

## 🚀 Самый быстрый способ

### С Docker (Рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone <repo-url>
cd Poop

# 2. Запустите все с помощью Makefile
make setup        # Установить зависимости
make start        # Запустить Docker (PostgreSQL + Backend)
make migrate      # Применить миграции
make seed         # Заполнить тестовыми данными

# 3. В новом терминале запустите mobile app
make mobile
```

Готово! 🎉

- Backend API: http://localhost:3000
- API Docs: http://localhost:3000/api/docs
- Mobile App: откроется Expo DevTools

## 📱 Без Docker

### Требования

- Node.js 18+
- PostgreSQL 14+

### Шаги

```bash
# 1. Установка зависимостей
npm install
cd backend && npm install && cd ..
cd mobile-app && npm install && cd ..

# 2. Настройка базы данных
# Создайте PostgreSQL базу:
createdb business_consulting

# 3. Настройка environment
cp backend/.env.example backend/.env
# Отредактируйте backend/.env с вашими настройками

# 4. Миграции и seed
cd backend
npm run prisma:generate
npm run prisma:migrate
npm run prisma:seed
cd ..

# 5. Запуск backend
cd backend && npm run start:dev

# 6. В новом терминале - mobile app
cd mobile-app && npm start
```

## 📖 Первые шаги

### 1. Откройте мобильное приложение

- Установите Expo Go на телефон
- Отсканируйте QR код из терминала
- Или нажмите `w` для web версии

### 2. Войдите с тестовым аккаунтом

```
Email: client1@example.com
Password: password123
```

### 3. Изучите функционал

- Просмотрите список консультантов
- Забронируйте консультацию
- Попробуйте чат
- Загрузите документ

### 4. Изучите API

Откройте Swagger документацию:
```
http://localhost:3000/api/docs
```

## 🛠️ Полезные команды

### Makefile команды

```bash
make help          # Показать все команды
make start         # Запустить Docker
make stop          # Остановить Docker
make restart       # Перезапустить Docker
make logs          # Показать логи
make clean         # Очистить проект
make mobile        # Запустить mobile app
make backend       # Запустить backend (без Docker)
make prisma-studio # Открыть Prisma Studio
```

### Backend команды

```bash
cd backend

npm run start:dev      # Development mode
npm run start:prod     # Production mode
npm run build          # Build
npm test               # Run tests
npm run lint           # Lint code
npm run prisma:studio  # Open Prisma Studio
npm run prisma:seed    # Seed database
```

### Mobile App команды

```bash
cd mobile-app

npm start           # Start Expo
npm run android     # Run on Android
npm run ios         # Run on iOS
npm run web         # Run in browser
npm run type-check  # TypeScript check
```

## 📊 Структура проекта

```
Poop/
├── mobile-app/           # React Native приложение
│   ├── src/
│   │   ├── screens/      # Экраны
│   │   ├── navigation/   # Навигация
│   │   ├── services/     # API сервисы
│   │   └── contexts/     # React контексты
│   └── App.tsx
│
├── backend/              # NestJS API
│   ├── src/
│   │   ├── auth/         # Аутентификация
│   │   ├── users/        # Пользователи
│   │   ├── consultants/  # Консультанты
│   │   ├── consultations/# Консультации
│   │   ├── payments/     # Платежи
│   │   ├── messages/     # Чат
│   │   └── documents/    # Документы
│   └── prisma/
│       └── schema.prisma
│
├── shared/               # Общие типы
├── scripts/              # Скрипты разработки
├── docs/                 # Документация
└── docker-compose.yml    # Docker конфигурация
```

## 🔐 Тестовые пользователи

После seed у вас есть:

**Клиенты:**
- client1@example.com : password123
- client2@example.com : password123
- client3@example.com : password123

**Консультанты:**
- consultant1@example.com : password123 (Финансы)
- consultant2@example.com : password123 (Маркетинг)
- consultant3@example.com : password123 (HR)
- consultant4@example.com : password123 (IT)
- consultant5@example.com : password123 (Стратегия)
- consultant6@example.com : password123 (Юридические)

## 🐛 Частые проблемы

### База данных не подключается

```bash
# Проверьте, что PostgreSQL запущен
pg_isready

# Или с Docker:
docker ps | grep postgres
```

### Порт 3000 занят

```bash
# Найдите процесс
lsof -i :3000

# Убейте процесс
kill -9 <PID>

# Или измените PORT в backend/.env
```

### Expo не подключается

```bash
# Очистите кэш
cd mobile-app
rm -rf .expo node_modules
npm install
```

### Ошибки Prisma

```bash
cd backend

# Сгенерируйте заново
npm run prisma:generate

# Сбросьте БД (ОСТОРОЖНО - удалит данные!)
npx prisma migrate reset
```

## 📚 Дальнейшее чтение

- [Полный README](../README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [API Examples](./API-EXAMPLES.md)
- [Deployment Guide](./DEPLOYMENT.md)

## 🆘 Нужна помощь?

- Проверьте [Issues](https://github.com/your-repo/issues)
- Создайте [Discussion](https://github.com/your-repo/discussions)
- Напишите на [email]

---

**Приятной разработки! 🚀**
