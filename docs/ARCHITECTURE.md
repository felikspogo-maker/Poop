# Architecture Guide

Архитектура Business Consulting Application.

## 📋 Содержание

- [Обзор](#обзор)
- [Backend Architecture](#backend-architecture)
- [Mobile App Architecture](#mobile-app-architecture)
- [Data Flow](#data-flow)
- [Security](#security)
- [Scalability](#scalability)

---

## Обзор

Business Consulting App - это full-stack приложение для бизнес-консалтинга, состоящее из:
- **Mobile App**: React Native (iOS/Android)
- **Backend API**: NestJS REST API
- **Database**: PostgreSQL с Prisma ORM
- **Real-time**: WebSocket (Socket.io)
- **Payments**: Stripe

```
┌─────────────────┐
│   Mobile App    │
│  (React Native) │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│   NestJS API    │
│  (TypeScript)   │
└────────┬────────┘
         │ Prisma ORM
         ▼
┌─────────────────┐
│   PostgreSQL    │
│    Database     │
└─────────────────┘
```

---

## Backend Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│  (Controllers, DTOs, Validation)    │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│         Business Logic Layer        │
│      (Services, Use Cases)          │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│         Data Access Layer           │
│     (Prisma, Repositories)          │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│            Database                 │
│          (PostgreSQL)               │
└─────────────────────────────────────┘
```

### Module Structure

```
backend/src/
├── auth/                 # Authentication & Authorization
│   ├── auth.controller.ts
│   ├── auth.service.ts
│   ├── auth.module.ts
│   ├── strategies/       # JWT, Local strategies
│   ├── guards/           # Auth guards
│   └── dto/              # Login, Register DTOs
│
├── users/                # User management
├── consultants/          # Consultant profiles
├── consultations/        # Consultation booking
├── payments/             # Payment processing
├── messages/             # Chat messaging
│   └── messages.gateway.ts  # WebSocket gateway
├── documents/            # Document management
├── health/               # Health checks
│
├── common/               # Shared utilities
│   ├── filters/          # Exception filters
│   ├── interceptors/     # Request/Response interceptors
│   ├── guards/           # Custom guards
│   ├── middleware/       # Custom middleware
│   ├── utils/            # Utility functions
│   ├── logger/           # Logging service
│   └── prisma/           # Prisma service
│
└── config/               # Configuration
    ├── configuration.ts  # App config
    └── env.validation.ts # Env validation
```

### Request Lifecycle

```
1. HTTP Request arrives
   ↓
2. Security Middleware (Helmet)
   ↓
3. CORS Middleware
   ↓
4. Logging Interceptor (logs request)
   ↓
5. Timeout Interceptor (30s timeout)
   ↓
6. Rate Limiting Guard (100 req/min)
   ↓
7. Auth Guard (JWT validation) [if protected]
   ↓
8. Validation Pipe (DTO validation)
   ↓
9. Controller Handler
   ↓
10. Service Layer
    ↓
11. Data Access (Prisma)
    ↓
12. Response
    ↓
13. Logging Interceptor (logs response)
    ↓
14. Exception Filter (if error)
    ↓
15. HTTP Response sent
```

### Error Handling

```typescript
// Global Exception Filter
try {
  // Business logic
} catch (error) {
  // Caught by HttpExceptionFilter
  // Logged by LoggerService
  // Formatted response sent
}
```

Структура ошибки:
```json
{
  "statusCode": 400,
  "timestamp": "2024-12-15T10:00:00.000Z",
  "path": "/api/consultations",
  "method": "POST",
  "message": "Validation failed",
  "error": "Bad Request"
}
```

### Interceptors

**1. LoggingInterceptor**
- Логирует все HTTP запросы
- Измеряет время выполнения
- Логирует ошибки

**2. TimeoutInterceptor**
- Автоматический timeout 30 секунд
- Предотвращает долгие запросы

**3. TransformInterceptor** (optional)
- Стандартизирует формат ответов
- Добавляет metadata

### Validation

```typescript
// DTO с валидацией
export class CreateConsultationDto {
  @IsNotEmpty()
  @IsString()
  consultantId: string;

  @IsDateString()
  date: string;

  @IsInt()
  @Min(30)
  @Max(240)
  duration: number;
}

// Автоматическая валидация через ValidationPipe
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,
  transform: true,
  forbidNonWhitelisted: true,
}));
```

---

## Mobile App Architecture

### Component Hierarchy

```
App
├── AuthProvider (Context)
│   └── NavigationContainer
│       ├── AuthNavigator (if not logged in)
│       │   ├── LoginScreen
│       │   └── RegisterScreen
│       │
│       └── MainNavigator (if logged in)
│           ├── HomeStack
│           │   └── HomeScreen
│           ├── ConsultantsStack
│           │   ├── ConsultantsScreen
│           │   ├── ConsultantDetailScreen
│           │   └── BookingScreen
│           ├── ConsultationsStack
│           │   ├── ConsultationsScreen
│           │   └── ConsultationDetailScreen
│           ├── ChatStack
│           │   ├── ChatScreen
│           │   └── ConversationScreen
│           └── ProfileStack
│               ├── ProfileScreen
│               └── DocumentsScreen
```

### State Management

**Global State (Context API):**
```typescript
// AuthContext
{
  user: User | null,
  loading: boolean,
  signIn: (email, password) => Promise<void>,
  signUp: (data) => Promise<void>,
  signOut: () => Promise<void>,
}
```

**Local State (useState/useEffect):**
- Component-specific data
- Form inputs
- UI state

**Persistent State (AsyncStorage):**
- access_token
- user data

### Data Flow

```
Screen
  ↓ (call API function)
API Service (axios)
  ↓ (HTTP request)
Backend API
  ↓ (response)
API Service
  ↓ (update state)
Screen (re-render)
```

### Navigation Flow

```
App Launch
  ↓
Check AsyncStorage
  ├─ Has token? → MainNavigator
  └─ No token? → AuthNavigator
      ↓ (login/register)
      Save token to AsyncStorage
      ↓
      MainNavigator
```

---

## Data Flow

### Authentication Flow

```
1. User enters credentials
   ↓
2. Mobile app → POST /api/auth/login
   ↓
3. Backend validates credentials (bcrypt)
   ↓
4. Backend generates JWT token
   ↓
5. Mobile app stores token in AsyncStorage
   ↓
6. All subsequent requests include token
   Authorization: Bearer <token>
```

### Consultation Booking Flow

```
1. User selects consultant
   ↓
2. User chooses date/time
   ↓
3. Mobile app → POST /api/consultations
   {consultantId, date, duration, description}
   ↓
4. Backend validates:
   - Date is in future
   - Consultant exists
   - Time slot available
   ↓
5. Create consultation in DB
   ↓
6. Return consultation details
   ↓
7. User proceeds to payment
```

### Payment Flow

```
1. Create payment intent
   Mobile app → POST /api/payments/create-intent
   ↓
2. Backend → Stripe API (create payment intent)
   ↓
3. Mobile app receives client_secret
   ↓
4. Mobile app → Stripe SDK (payment UI)
   ↓
5. User enters card details
   ↓
6. Stripe processes payment
   ↓
7. Mobile app → POST /api/payments/confirm
   ↓
8. Backend updates payment status
```

### Real-time Chat Flow

```
WebSocket Connection:
1. User opens chat
   ↓
2. Socket.io connection established
   ↓
3. Join conversation room
   socket.emit('joinConversation', conversationId)
   ↓
4. Send message
   socket.emit('sendMessage', {content, ...})
   ↓
5. Server broadcasts to room
   socket.to(conversationId).emit('newMessage', message)
   ↓
6. All participants receive message
   socket.on('newMessage', (message) => {...})
```

---

## Security

### Authentication & Authorization

**JWT Tokens:**
```typescript
{
  sub: userId,        // Subject
  email: userEmail,
  role: userRole,
  iat: issuedAt,     // Issued at
  exp: expiresAt,    // Expires at
}
```

**Guards:**
- JwtAuthGuard - validates JWT token
- ThrottlerGuard - rate limiting

### Data Protection

**Password Storage:**
```typescript
// Hashing with bcrypt (10 rounds)
const hashedPassword = await bcrypt.hash(password, 10);

// Verification
const isValid = await bcrypt.compare(password, hashedPassword);
```

**Environment Variables:**
- Stored in `.env` (gitignored)
- Validated on startup
- Type-safe access through ConfigService

### API Security

**Helmet Middleware:**
- XSS Protection
- Content Security Policy
- X-Frame-Options (clickjacking protection)
- HSTS (HTTP Strict Transport Security)

**Rate Limiting:**
- 100 requests/minute for authenticated users
- Per-user tracking

**CORS:**
```typescript
{
  origin: ['http://localhost:19006', 'exp://localhost:19000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
}
```

**Input Validation:**
- DTO validation with class-validator
- Whitelist unknown properties
- Transform types automatically

### WebSocket Security

```typescript
// TODO: Add JWT auth for WebSocket
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  // Verify token
  next();
});
```

---

## Scalability

### Horizontal Scaling

**Backend API:**
```
Load Balancer
    ├─ API Instance 1
    ├─ API Instance 2
    └─ API Instance 3
         ↓
    Database (shared)
```

**Considerations:**
- Stateless API (JWT tokens)
- Shared PostgreSQL database
- Session management in database

### Database Optimization

**Indexes:**
```prisma
model User {
  email String @unique @db.VarChar(255)
  @@index([email])
}
```

**Connection Pooling:**
- Prisma manages connection pool
- Configure based on load

**Query Optimization:**
- Use `select` to fetch only needed fields
- Use `include` carefully to avoid N+1 queries

### Caching Strategy

**Future improvements:**
- Redis for session storage
- Cache frequently accessed data
- Cache invalidation strategy

### File Storage

**Current:**
- Local file system (`/uploads`)

**Production:**
- AWS S3 / Google Cloud Storage
- CDN for static assets

### Monitoring

**Health Checks:**
- `/health` - comprehensive check
- `/health/live` - liveness probe
- `/health/ready` - readiness probe

**Metrics to monitor:**
- Response times
- Error rates
- Database connection pool
- Memory usage
- CPU usage

---

## Best Practices

### Code Organization

1. **Module per feature**: Each feature is a self-contained module
2. **Dependency Injection**: Use NestJS DI container
3. **Interface Segregation**: DTOs for data validation
4. **Single Responsibility**: Each service has one purpose

### Error Handling

1. **Use proper HTTP status codes**
2. **Provide meaningful error messages**
3. **Log errors with context**
4. **Don't expose sensitive information**

### Testing

1. **Unit tests** for services and utilities
2. **Integration tests** for controllers
3. **E2E tests** for critical flows
4. **Test coverage** >= 80%

### Performance

1. **Lazy loading** in mobile app
2. **Pagination** for large lists
3. **Debounce** search inputs
4. **Image optimization**
5. **Code splitting**

---

## Future Improvements

1. **Microservices Architecture**
   - Split into separate services
   - API Gateway
   - Service mesh

2. **Event-Driven Architecture**
   - Message queue (RabbitMQ/Kafka)
   - Event sourcing
   - CQRS pattern

3. **GraphQL**
   - Alternative to REST
   - Better mobile performance
   - Type-safe queries

4. **Admin Panel**
   - Web-based admin interface
   - User management
   - Analytics dashboard

5. **Advanced Features**
   - Video consultations (WebRTC)
   - AI-powered recommendations
   - Multi-language support
   - Push notifications

---

**Happy Building! 🏗️**
