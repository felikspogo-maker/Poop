# Changelog

Все важные изменения в проекте будут документированы в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Добавлено
- Prettier и ESLint конфигурация для backend и mobile-app
- VS Code workspace settings с рекомендуемыми расширениями
- Security middleware (Helmet, Rate Limiting)
- Logger service для структурированного логирования
- Utility functions:
  - Date utils (работа с датами)
  - String utils (форматирование строк)
  - Validation utils (валидация данных)
  - Formatters для mobile app
  - Validators для mobile app
- Unit tests examples для backend
- Testing guide documentation

### Изменено
- Обновлен backend/package.json с новыми зависимостями (helmet, @nestjs/throttler)
- Улучшен main.ts с security features
- Добавлен ThrottlerModule в app.module.ts

---

## [0.2.0] - 2024-12-XX

### Добавлено
- Database seeding с тестовыми данными
  - 6 консультантов разных специализаций
  - 3 клиента
  - Примеры консультаций и сообщений
- Docker & Docker Compose конфигурация
- Makefile с удобными командами
- Development helper script (./scripts/dev.sh)
- Environment configuration system
- Production-ready Dockerfiles
- Postman API collection для тестирования
- GitHub Actions CI/CD workflows
  - Автоматическое тестирование
  - Backend build & lint
  - Mobile app type checking
  - Docker build tests
  - Security audits
- Comprehensive documentation:
  - CONTRIBUTING.md - руководство по вкладу
  - QUICK-START.md - быстрый старт
  - API-EXAMPLES.md - примеры API
  - DEPLOYMENT.md - руководство по deployment

### Изменено
- Обновлена структура проекта для лучшей организации
- Улучшен README.md с дополнительной информацией

---

## [0.1.0] - 2024-12-XX

### Добавлено
- Initial setup полнофункционального приложения для бизнес-консалтинга
- Mobile App (React Native + Expo):
  - Authentication (login/register)
  - Consultants browsing и фильтрация
  - Consultation booking system
  - Real-time chat (Socket.io)
  - Payment integration (Stripe)
  - Document management
  - User profile management
  - Responsive UI (React Native Paper)
- Backend (NestJS + PostgreSQL):
  - RESTful API с Swagger документацией
  - JWT authentication
  - Prisma ORM
  - WebSocket support (Socket.io)
  - Stripe payment processing
  - File upload/download
  - CRUD операции для всех модулей
- Database schema (Prisma):
  - Users, Consultants, Consultations
  - Payments, Messages, Conversations
  - Documents
- Project structure:
  - /mobile-app - React Native приложение
  - /backend - NestJS API
  - /shared - Shared TypeScript types
- Базовая документация в README.md

### Технологии
- **Frontend**: React Native, TypeScript, Expo
- **Backend**: NestJS, TypeScript, Prisma
- **Database**: PostgreSQL
- **Real-time**: Socket.io
- **Payments**: Stripe
- **Auth**: JWT + bcrypt

---

## Типы изменений

- `Added` - новые функции
- `Changed` - изменения в существующей функциональности
- `Deprecated` - функции, которые скоро будут удалены
- `Removed` - удаленные функции
- `Fixed` - исправления багов
- `Security` - исправления уязвимостей

---

[Unreleased]: https://github.com/your-repo/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/your-repo/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/your-repo/releases/tag/v0.1.0
