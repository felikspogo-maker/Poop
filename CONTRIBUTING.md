# Contributing to Business Consulting App

Спасибо за ваш интерес к проекту! Мы приветствуем вклад от сообщества.

## 🚀 Начало работы

### Требования

- Node.js >= 18.x
- npm или yarn
- PostgreSQL >= 14.x
- Docker и Docker Compose (опционально)
- Git

### Установка для разработки

1. **Форк репозитория**

2. **Клонируйте ваш форк:**
```bash
git clone https://github.com/your-username/Poop.git
cd Poop
```

3. **Настройте upstream:**
```bash
git remote add upstream https://github.com/original-owner/Poop.git
```

4. **Быстрый старт с Makefile:**
```bash
# Установите все зависимости
make setup

# Запустите Docker с базой данных и backend
make start

# Примените миграции
make migrate

# Заполните тестовыми данными
make seed

# Запустите мобильное приложение
make mobile
```

5. **Или используйте development скрипт:**
```bash
# Установка
./scripts/dev.sh setup

# Запуск
./scripts/dev.sh start

# Миграции
./scripts/dev.sh migrate

# Seed
./scripts/dev.sh seed
```

## 📝 Процесс разработки

### Workflow

1. **Создайте ветку для функции:**
```bash
git checkout -b feature/amazing-feature
# или
git checkout -b fix/bug-description
```

2. **Напишите код:**
   - Следуйте style guide проекта
   - Добавьте тесты для новой функциональности
   - Обновите документацию при необходимости

3. **Коммиты:**
```bash
git add .
git commit -m "feat: add amazing feature"
```

Используйте [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - новая функция
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг
- `test:` - добавление тестов
- `chore:` - изменения в build процессе

4. **Пуш изменений:**
```bash
git push origin feature/amazing-feature
```

5. **Создайте Pull Request**

## 🧪 Тестирование

### Backend

```bash
cd backend

# Запуск всех тестов
npm test

# Тесты с coverage
npm run test:cov

# E2E тесты
npm run test:e2e

# Lint
npm run lint
```

### Mobile App

```bash
cd mobile-app

# Type check
npm run type-check

# Lint
npm run lint
```

## 📐 Code Style

### TypeScript

- Используйте TypeScript для всего кода
- Избегайте `any` типов
- Используйте строгую типизацию

### Именование

- **Файлы**: kebab-case (`user-service.ts`)
- **Классы**: PascalCase (`UserService`)
- **Функции/переменные**: camelCase (`getUserById`)
- **Константы**: UPPER_SNAKE_CASE (`API_URL`)
- **Компоненты React**: PascalCase (`LoginScreen.tsx`)

### Backend (NestJS)

```typescript
// Хорошо
@Injectable()
export class UserService {
  async findById(id: string): Promise<User> {
    return this.prisma.user.findUnique({ where: { id } });
  }
}

// Плохо
export class UserService {
  findById(id: any) {
    return this.prisma.user.findUnique({ where: { id } });
  }
}
```

### Mobile App (React Native)

```typescript
// Хорошо
export const LoginScreen: React.FC = () => {
  const [email, setEmail] = useState<string>('');

  return (
    <View style={styles.container}>
      {/* ... */}
    </View>
  );
};

// Плохо
export const LoginScreen = () => {
  const [email, setEmail] = useState('');

  return <View>{/* ... */}</View>;
};
```

## 🗄️ База данных

### Изменения схемы

1. **Обновите Prisma schema:**
```prisma
// backend/prisma/schema.prisma
model NewModel {
  id   String @id @default(uuid())
  name String
}
```

2. **Создайте миграцию:**
```bash
cd backend
npx prisma migrate dev --name add_new_model
```

3. **Обновите seed данные:**
```typescript
// backend/prisma/seed.ts
await prisma.newModel.create({
  data: { name: 'Example' }
});
```

## 📚 Документация

### API Documentation

- Все эндпоинты должны быть документированы с Swagger
- Используйте декораторы NestJS Swagger

```typescript
@ApiTags('Users')
@ApiOperation({ summary: 'Get user by ID' })
@ApiResponse({ status: 200, description: 'User found' })
@ApiResponse({ status: 404, description: 'User not found' })
@Get(':id')
async findById(@Param('id') id: string) {
  // ...
}
```

### Code Comments

- Комментируйте сложную логику
- Используйте JSDoc для публичных методов

```typescript
/**
 * Создает новую консультацию
 * @param userId - ID клиента
 * @param data - Данные консультации
 * @returns Созданная консультация
 * @throws {BadRequestException} если дата в прошлом
 */
async create(userId: string, data: CreateConsultationDto) {
  // ...
}
```

## 🐛 Reporting Bugs

При создании issue для бага, включите:

1. **Описание проблемы**
2. **Шаги для воспроизведения**
3. **Ожидаемое поведение**
4. **Фактическое поведение**
5. **Скриншоты** (если применимо)
6. **Окружение:**
   - OS
   - Node.js версия
   - npm/yarn версия

## ✨ Feature Requests

При создании issue для новой функции:

1. **Описание функции**
2. **Use case**
3. **Почему это важно**
4. **Возможное решение** (опционально)
5. **Альтернативы** (опционально)

## 📋 Pull Request Guidelines

### Чеклист

Перед созданием PR убедитесь:

- [ ] Код соответствует style guide
- [ ] Все тесты проходят
- [ ] Добавлены новые тесты (если применимо)
- [ ] Документация обновлена
- [ ] Коммиты следуют Conventional Commits
- [ ] PR описание подробное и понятное
- [ ] Нет конфликтов с main веткой

### Описание PR

```markdown
## Описание
Краткое описание изменений

## Тип изменений
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Связанные issues
Closes #123

## Как протестировано
Опишите, как вы тестировали изменения

## Screenshots (если применимо)
```

## 🔒 Security

Если вы нашли уязвимость в безопасности, **НЕ создавайте публичный issue**.

Вместо этого:
1. Отправьте email на [security@example.com]
2. Опишите уязвимость
3. Шаги для воспроизведения
4. Возможное решение

## 💬 Вопросы?

- Создайте [Discussion](https://github.com/your-repo/discussions)
- Присоединяйтесь к нашему [Discord/Telegram]
- Напишите на [email]

## 📜 Лицензия

Внося вклад, вы соглашаетесь, что ваш код будет лицензирован под MIT License проекта.

---

**Спасибо за ваш вклад! 🎉**
