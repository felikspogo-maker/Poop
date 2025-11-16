# API Examples

Примеры использования Business Consulting API.

## Базовая URL

```
http://localhost:3000/api
```

## Аутентификация

Все защищенные эндпоинты требуют JWT токен в заголовке:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Authentication

### Регистрация

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "firstName": "Иван",
    "lastName": "Петров",
    "phone": "+79001234567"
  }'
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid-here",
    "email": "newuser@example.com",
    "firstName": "Иван",
    "lastName": "Петров",
    "phone": "+79001234567",
    "role": "CLIENT"
  }
}
```

### Вход

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client1@example.com",
    "password": "password123"
  }'
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid-here",
    "email": "client1@example.com",
    "firstName": "Иван",
    "lastName": "Петров",
    "role": "CLIENT"
  }
}
```

### Получить профиль

```bash
curl -X GET http://localhost:3000/api/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Consultants

### Получить всех консультантов

```bash
curl -X GET http://localhost:3000/api/consultants
```

Ответ:
```json
[
  {
    "id": "uuid-here",
    "userId": "uuid-here",
    "specialization": "Финансы",
    "bio": "Опытный финансовый консультант...",
    "hourlyRate": 5000,
    "rating": 4.8,
    "reviewsCount": 127,
    "skills": ["Финансовый анализ", "Инвестиции"],
    "user": {
      "id": "uuid-here",
      "firstName": "Дмитрий",
      "lastName": "Козлов",
      "email": "consultant1@example.com"
    }
  }
]
```

### Поиск по специализации

```bash
curl -X GET "http://localhost:3000/api/consultants?specialization=Финансы"
```

### Получить консультанта по ID

```bash
curl -X GET http://localhost:3000/api/consultants/CONSULTANT_ID
```

---

## Consultations

### Получить мои консультации

```bash
curl -X GET http://localhost:3000/api/consultations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Ответ:
```json
[
  {
    "id": "uuid-here",
    "userId": "uuid-here",
    "consultantId": "uuid-here",
    "date": "2024-12-20T10:00:00.000Z",
    "duration": 60,
    "description": "Консультация по финансовому планированию",
    "status": "SCHEDULED",
    "consultant": {
      "id": "uuid-here",
      "specialization": "Финансы",
      "user": {
        "firstName": "Дмитрий",
        "lastName": "Козлов"
      }
    }
  }
]
```

### Создать консультацию

```bash
curl -X POST http://localhost:3000/api/consultations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "consultantId": "CONSULTANT_ID",
    "date": "2024-12-20T10:00:00.000Z",
    "duration": 60,
    "description": "Хочу обсудить инвестиционную стратегию"
  }'
```

### Отменить консультацию

```bash
curl -X PATCH http://localhost:3000/api/consultations/CONSULTATION_ID/cancel \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Payments

### Создать платеж

```bash
curl -X POST http://localhost:3000/api/payments/create-intent \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "consultationId": "CONSULTATION_ID"
  }'
```

Ответ:
```json
{
  "clientSecret": "pi_xxx_secret_xxx",
  "paymentIntentId": "pi_xxx"
}
```

### Подтвердить платеж

```bash
curl -X POST http://localhost:3000/api/payments/confirm \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "paymentIntentId": "pi_xxx"
  }'
```

### История платежей

```bash
curl -X GET http://localhost:3000/api/payments/history \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Messages

### Получить чаты

```bash
curl -X GET http://localhost:3000/api/messages/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Ответ:
```json
[
  {
    "id": "conversation-uuid",
    "otherUser": {
      "id": "uuid",
      "firstName": "Дмитрий",
      "lastName": "Козлов",
      "avatar": null
    },
    "lastMessage": {
      "id": "message-uuid",
      "content": "Здравствуйте! Хочу проконсультироваться...",
      "createdAt": "2024-12-01T10:00:00.000Z"
    },
    "unreadCount": 2
  }
]
```

### Получить сообщения

```bash
curl -X GET http://localhost:3000/api/messages/CONVERSATION_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Отправить сообщение

```bash
curl -X POST http://localhost:3000/api/messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "CONVERSATION_ID",
    "receiverId": "USER_ID",
    "content": "Привет! Когда удобно созвониться?"
  }'
```

### Создать чат

```bash
curl -X POST http://localhost:3000/api/messages/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "participantId": "CONSULTANT_ID"
  }'
```

---

## Documents

### Получить документы

```bash
curl -X GET http://localhost:3000/api/documents \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Загрузить документ

```bash
curl -X POST http://localhost:3000/api/documents/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

Ответ:
```json
{
  "id": "uuid-here",
  "userId": "uuid-here",
  "name": "document.pdf",
  "type": "application/pdf",
  "size": 1024567,
  "url": "/uploads/xxx-document.pdf",
  "createdAt": "2024-12-01T10:00:00.000Z"
}
```

### Скачать документ

```bash
curl -X GET http://localhost:3000/api/documents/DOCUMENT_ID/download \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o downloaded-file.pdf
```

### Удалить документ

```bash
curl -X DELETE http://localhost:3000/api/documents/DOCUMENT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## WebSocket (Chat)

Подключение к WebSocket для real-time чата:

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:3000');

// Присоединиться к чату
socket.emit('joinConversation', conversationId);

// Отправить сообщение
socket.emit('sendMessage', {
  conversationId: 'uuid',
  senderId: 'uuid',
  receiverId: 'uuid',
  content: 'Hello!',
});

// Получить сообщение
socket.on('newMessage', (message) => {
  console.log('New message:', message);
});

// Typing индикатор
socket.emit('typing', {
  conversationId: 'uuid',
  userId: 'uuid',
});

socket.on('userTyping', (data) => {
  console.log('User is typing:', data);
});
```

---

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Internal Server Error |

### Примеры ошибок

```json
{
  "statusCode": 401,
  "message": "Unauthorized",
  "error": "Unauthorized"
}
```

```json
{
  "statusCode": 400,
  "message": ["email must be an email"],
  "error": "Bad Request"
}
```

---

## Rate Limiting

API имеет rate limiting:
- 100 запросов в минуту для аутентифицированных пользователей
- 20 запросов в минуту для неаутентифицированных

---

## Тестовые данные

После выполнения `npm run prisma:seed` доступны тестовые пользователи:

### Клиенты
- email: `client1@example.com` | password: `password123`
- email: `client2@example.com` | password: `password123`
- email: `client3@example.com` | password: `password123`

### Консультанты
- email: `consultant1@example.com` | password: `password123` (Финансы)
- email: `consultant2@example.com` | password: `password123` (Маркетинг)
- email: `consultant3@example.com` | password: `password123` (HR)
- email: `consultant4@example.com` | password: `password123` (IT)
- email: `consultant5@example.com` | password: `password123` (Стратегия)
- email: `consultant6@example.com` | password: `password123` (Юридические)

---

## Swagger Documentation

Интерактивная документация доступна по адресу:

```
http://localhost:3000/api/docs
```

Здесь вы можете:
- Просмотреть все эндпоинты
- Протестировать API прямо в браузере
- Посмотреть схемы запросов/ответов
- Скачать OpenAPI specification

---

## Postman Collection

Импортируйте готовую коллекцию запросов:

```bash
api-tests/Business-Consulting-API.postman_collection.json
```

Откройте Postman → Import → выберите файл

---

**Happy API Testing! 🚀**
