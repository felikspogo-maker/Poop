# Business Consulting Mobile Application

Полнофункциональное мобильное приложение для бизнес-консалтинга с React Native и NestJS backend.

## 📋 Содержание

- [Технологии](#технологии)
- [Возможности](#возможности)
- [Структура проекта](#структура-проекта)
- [Установка](#установка)
- [Запуск](#запуск)
- [Конфигурация](#конфигурация)
- [Production Deployment](#production-deployment)
- [API Documentation](#api-documentation)

## 🚀 Технологии

### Frontend (Mobile App)
- **React Native** с Expo
- **TypeScript**
- **React Navigation** - навигация
- **React Native Paper** - UI компоненты
- **Socket.io Client** - real-time чат
- **Axios** - HTTP запросы
- **Formik + Yup** - формы и валидация
- **Stripe React Native** - платежи

### Backend (API)
- **NestJS** - Node.js фреймворк
- **TypeScript**
- **Prisma ORM** - работа с БД
- **PostgreSQL** - база данных
- **JWT** - аутентификация
- **bcrypt** - хеширование паролей
- **Socket.io** - WebSocket для чата
- **Stripe** - платежная система
- **Multer** - загрузка файлов
- **Swagger** - API документация

## ✨ Возможности

### Для клиентов
- ✅ Регистрация и авторизация
- 👥 Поиск консультантов по специализации
- 📅 Бронирование консультаций
- 💳 Онлайн оплата через Stripe
- 💬 Чат в реальном времени с консультантами
- 📄 Загрузка и управление документами
- 📊 История консультаций и платежей
- 🔔 Уведомления

### Для консультантов (расширяется)
- 📋 Профиль консультанта
- ⭐ Рейтинг и отзывы
- 📅 Управление расписанием
- 💰 Финансовая аналитика

## 📁 Структура проекта

```
.
├── mobile-app/          # React Native приложение
│   ├── src/
│   │   ├── screens/     # Экраны приложения
│   │   ├── components/  # Переиспользуемые компоненты
│   │   ├── navigation/  # Навигация
│   │   ├── services/    # API сервисы
│   │   ├── contexts/    # React контексты
│   │   └── utils/       # Утилиты и темы
│   └── package.json
│
├── backend/             # NestJS API
│   ├── src/
│   │   ├── auth/        # Модуль аутентификации
│   │   ├── users/       # Модуль пользователей
│   │   ├── consultants/ # Модуль консультантов
│   │   ├── consultations/ # Модуль консультаций
│   │   ├── payments/    # Модуль платежей
│   │   ├── messages/    # Модуль сообщений
│   │   ├── documents/   # Модуль документов
│   │   └── common/      # Общие модули (Prisma)
│   ├── prisma/
│   │   └── schema.prisma # Схема базы данных
│   └── package.json
│
├── shared/              # Общие типы TypeScript
│   └── src/
│       └── types.ts
│
└── package.json         # Root package.json (workspace)
```

## 🔧 Установка

### Требования
- Node.js >= 18.x
- npm или yarn
- PostgreSQL >= 14.x
- Expo CLI (для мобильного приложения)
- Expo Go приложение на телефоне (для тестирования)

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd Poop
```

### 2. Установка зависимостей

```bash
# Установить все зависимости для всех workspace
npm run install:all

# Или устанавливать отдельно:
npm install                    # Root dependencies
cd mobile-app && npm install   # Mobile app
cd ../backend && npm install   # Backend
cd ../shared && npm install    # Shared
```

### 3. Настройка базы данных

#### Создайте PostgreSQL базу данных:

```bash
# Войдите в PostgreSQL
psql -U postgres

# Создайте базу данных
CREATE DATABASE business_consulting;

# Выйдите
\q
```

#### Настройте переменные окружения:

```bash
# Backend
cd backend
cp .env.example .env
```

Отредактируйте `backend/.env`:

```env
DATABASE_URL="postgresql://postgres:password@localhost:5432/business_consulting?schema=public"
JWT_SECRET="your-super-secret-jwt-key-change-in-production"
JWT_EXPIRATION="7d"
STRIPE_SECRET_KEY="sk_test_your_stripe_key"
STRIPE_PUBLISHABLE_KEY="pk_test_your_stripe_key"
PORT=3000
NODE_ENV=development
CORS_ORIGIN="http://localhost:19006,exp://localhost:19000"
```

#### Примените миграции Prisma:

```bash
cd backend
npm run prisma:generate
npm run prisma:migrate
```

## 🚀 Запуск

### Backend (API)

```bash
# Development mode с hot-reload
cd backend
npm run start:dev

# Production mode
npm run start:prod

# API будет доступен на http://localhost:3000
# Swagger документация: http://localhost:3000/api/docs
```

### Mobile App

```bash
cd mobile-app
npm start

# Или запустить на конкретной платформе:
npm run android  # Android
npm run ios      # iOS (только на macOS)
npm run web      # Web версия
```

Отсканируйте QR код в Expo Go приложении на телефоне.

### Запуск всего проекта одновременно

Вы можете использовать терминал с разделением:

**Терминал 1 - Backend:**
```bash
npm run backend
```

**Терминал 2 - Mobile App:**
```bash
npm run mobile
```

## ⚙️ Конфигурация

### Backend конфигурация

Все настройки backend в файле `backend/.env`:

- `DATABASE_URL` - Строка подключения к PostgreSQL
- `JWT_SECRET` - Секретный ключ для JWT токенов
- `JWT_EXPIRATION` - Время жизни токена
- `STRIPE_SECRET_KEY` - Stripe секретный ключ
- `PORT` - Порт сервера (по умолчанию 3000)

### Mobile App конфигурация

API URL настраивается в `mobile-app/src/services/api.ts`:

```typescript
const API_URL = __DEV__
  ? 'http://localhost:3000/api'  // Development
  : 'https://your-api.com/api';  // Production
```

## 🚀 Production Deployment

### Quick Production Deployment

Полное руководство: [PRODUCTION-README.md](PRODUCTION-README.md) | [docs/PRODUCTION.md](docs/PRODUCTION.md)

```bash
# 1. Clone repository
git clone <your-repo>
cd Poop

# 2. Create production config
cp backend/.env.production.example .env.production

# 3. Edit .env.production (replace all placeholders)
# Generate secrets:
openssl rand -base64 32  # JWT_SECRET
openssl rand -base64 24  # POSTGRES_PASSWORD

# 4. Setup SSL certificates (Let's Encrypt recommended)
mkdir -p nginx/ssl
# Copy cert.pem and key.pem to nginx/ssl/

# 5. Initialize and deploy
chmod +x scripts/*.sh
./scripts/init-prod.sh
./scripts/deploy-prod.sh
```

### Production Features

✅ **Docker-based deployment** with multi-stage builds
✅ **Health checks** for backend and database
✅ **Automated database migrations**
✅ **SSL/TLS support** via Nginx reverse proxy
✅ **Persistent volumes** for database and uploads
✅ **Rate limiting** and security headers
✅ **Automated backups** scripts included
✅ **Zero-downtime deployments**

### Production Scripts

```bash
./scripts/init-prod.sh      # Initialize production environment
./scripts/deploy-prod.sh     # Deploy/update application
./scripts/migrate-prod.sh    # Run database migrations
```

### Monitoring

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check health
curl https://yourdomain.com/health

# Container stats
docker stats
```

## 📚 API Documentation

После запуска backend, Swagger документация доступна по адресу:

```
http://localhost:3000/api/docs
```

### Основные эндпоинты:

#### Authentication
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `GET /api/auth/profile` - Получить профиль

#### Consultants
- `GET /api/consultants` - Список консультантов
- `GET /api/consultants/:id` - Консультант по ID

#### Consultations
- `GET /api/consultations` - Мои консультации
- `POST /api/consultations` - Создать консультацию
- `PATCH /api/consultations/:id/cancel` - Отменить

#### Payments
- `POST /api/payments/create-intent` - Создать платеж
- `GET /api/payments/history` - История платежей

#### Messages
- `GET /api/messages/conversations` - Список чатов
- `GET /api/messages/:id` - Сообщения чата
- `POST /api/messages` - Отправить сообщение

#### Documents
- `GET /api/documents` - Список документов
- `POST /api/documents/upload` - Загрузить документ
- `DELETE /api/documents/:id` - Удалить документ

## 🗄️ База данных

Схема базы данных включает следующие таблицы:

- **users** - Пользователи
- **consultants** - Консультанты
- **consultations** - Консультации
- **payments** - Платежи
- **conversations** - Чаты
- **messages** - Сообщения
- **documents** - Документы

### Prisma команды

```bash
# Генерация Prisma Client
npm run prisma:generate

# Создание миграции
npm run prisma:migrate

# Открыть Prisma Studio (GUI для БД)
npm run prisma:studio

# Сброс БД (ОСТОРОЖНО!)
npx prisma migrate reset
```

## 🔐 Аутентификация

Приложение использует JWT (JSON Web Tokens) для аутентификации:

1. Пользователь регистрируется или входит
2. Сервер возвращает JWT токен
3. Токен сохраняется в AsyncStorage
4. Все запросы отправляются с заголовком `Authorization: Bearer <token>`
5. Backend проверяет токен через JwtAuthGuard

## 💳 Платежи

Интеграция со Stripe для обработки платежей:

1. Получите Stripe ключи на https://stripe.com
2. Добавьте их в `backend/.env`
3. Клиент создает payment intent
4. Использует Stripe SDK для оплаты
5. Backend подтверждает платеж

## 💬 Real-time чат

WebSocket чат на Socket.io:

1. Клиент подключается к Socket.io серверу
2. Присоединяется к комнате (conversation)
3. Отправляет/получает сообщения в реальном времени
4. События: `joinConversation`, `sendMessage`, `newMessage`, `typing`

## 📱 Разработка

### Добавление новой функции

1. **Backend:**
   - Создайте модуль: `nest g module feature`
   - Создайте сервис: `nest g service feature`
   - Создайте контроллер: `nest g controller feature`
   - Добавьте в Prisma схему
   - Создайте миграцию

2. **Mobile App:**
   - Создайте экран в `src/screens/`
   - Добавьте в навигацию
   - Создайте API методы в `src/services/`
   - Добавьте UI компоненты

### Тестирование

```bash
# Backend тесты
cd backend
npm run test
npm run test:e2e

# Lint
npm run lint
```

## 🚢 Деплой

### Backend

Рекомендуемые платформы:
- Heroku
- Railway
- Render
- DigitalOcean

### Mobile App

```bash
# Build для production
cd mobile-app
eas build --platform android
eas build --platform ios

# Или использовать Expo Application Services
eas submit
```

## 📄 Лицензия

MIT

## 👥 Автор

Ваше имя

## 🤝 Поддержка

Если у вас есть вопросы или проблемы, создайте issue в репозитории.

---

**Happy Coding! 🎉**
