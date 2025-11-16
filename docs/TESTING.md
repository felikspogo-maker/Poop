# Testing Guide

Руководство по тестированию Business Consulting App.

## 📋 Содержание

- [Backend Testing](#backend-testing)
- [Mobile App Testing](#mobile-app-testing)
- [E2E Testing](#e2e-testing)
- [Test Coverage](#test-coverage)

---

## Backend Testing

### Running Tests

```bash
cd backend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:cov

# Run E2E tests
npm run test:e2e
```

### Writing Unit Tests

Пример теста для сервиса:

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { YourService } from './your.service';

describe('YourService', () => {
  let service: YourService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [YourService],
    }).compile();

    service = module.get<YourService>(YourService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  it('should do something', () => {
    const result = service.doSomething();
    expect(result).toBe(expectedValue);
  });
});
```

### Testing with Mocks

```typescript
const mockRepository = {
  find: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  save: jest.fn(),
  delete: jest.fn(),
};

beforeEach(async () => {
  const module: TestingModule = await Test.createTestingModule({
    providers: [
      YourService,
      {
        provide: getRepositoryToken(YourEntity),
        useValue: mockRepository,
      },
    ],
  }).compile();

  service = module.get<YourService>(YourService);
});
```

### Testing Controllers

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { YourController } from './your.controller';
import { YourService } from './your.service';

describe('YourController', () => {
  let controller: YourController;
  let service: YourService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [YourController],
      providers: [
        {
          provide: YourService,
          useValue: {
            findAll: jest.fn(),
            findOne: jest.fn(),
            create: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<YourController>(YourController);
    service = module.get<YourService>(YourService);
  });

  it('should return an array of items', async () => {
    const result = ['item1', 'item2'];
    jest.spyOn(service, 'findAll').mockResolvedValue(result);

    expect(await controller.findAll()).toBe(result);
  });
});
```

### Testing with Database

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { PrismaService } from '../prisma/prisma.service';

describe('Integration Tests', () => {
  let prisma: PrismaService;

  beforeAll(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [PrismaService],
    }).compile();

    prisma = module.get<PrismaService>(PrismaService);
  });

  beforeEach(async () => {
    // Clean database before each test
    await prisma.user.deleteMany();
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  it('should create a user', async () => {
    const user = await prisma.user.create({
      data: {
        email: 'test@example.com',
        password: 'hashedpassword',
        firstName: 'Test',
        lastName: 'User',
        phone: '+79001234567',
      },
    });

    expect(user).toHaveProperty('id');
    expect(user.email).toBe('test@example.com');
  });
});
```

---

## Mobile App Testing

### Running Tests

```bash
cd mobile-app

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:cov
```

### Testing Components

```typescript
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { LoginScreen } from './LoginScreen';

describe('LoginScreen', () => {
  it('should render login form', () => {
    const { getByPlaceholderText } = render(<LoginScreen />);

    expect(getByPlaceholderText('Email')).toBeTruthy();
    expect(getByPlaceholderText('Password')).toBeTruthy();
  });

  it('should handle form submission', () => {
    const mockOnSubmit = jest.fn();
    const { getByText, getByPlaceholderText } = render(
      <LoginScreen onSubmit={mockOnSubmit} />
    );

    fireEvent.changeText(getByPlaceholderText('Email'), 'test@example.com');
    fireEvent.changeText(getByPlaceholderText('Password'), 'password');
    fireEvent.press(getByText('Login'));

    expect(mockOnSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password',
    });
  });
});
```

### Testing Utilities

```typescript
import { formatCurrency, formatDate } from '../utils/formatters';

describe('Formatters', () => {
  describe('formatCurrency', () => {
    it('should format currency correctly', () => {
      expect(formatCurrency(5000)).toBe('5 000 ₽');
      expect(formatCurrency(1000000)).toBe('1 000 000 ₽');
    });
  });

  describe('formatDate', () => {
    it('should format date correctly', () => {
      const date = new Date('2024-12-25');
      expect(formatDate(date)).toBe('25 декабря 2024 г.');
    });
  });
});
```

### Testing Hooks

```typescript
import { renderHook, act } from '@testing-library/react-hooks';
import { useAuth } from '../contexts/AuthContext';

describe('useAuth', () => {
  it('should login user', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.signIn('test@example.com', 'password');
    });

    expect(result.current.user).toBeTruthy();
    expect(result.current.user.email).toBe('test@example.com');
  });
});
```

---

## E2E Testing

### Backend E2E Tests

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './../src/app.module';

describe('AppController (e2e)', () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterEach(async () => {
    await app.close();
  });

  it('/health (GET)', () => {
    return request(app.getHttpServer())
      .get('/health')
      .expect(200)
      .expect({
        status: 'ok',
      });
  });

  it('/api/auth/login (POST)', () => {
    return request(app.getHttpServer())
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'password',
      })
      .expect(200)
      .expect((res) => {
        expect(res.body).toHaveProperty('access_token');
      });
  });
});
```

---

## Test Coverage

### Генерация отчета

```bash
# Backend
cd backend
npm run test:cov

# Открыть HTML отчет
open coverage/lcov-report/index.html
```

### Цели coverage

- **Statements**: >= 80%
- **Branches**: >= 75%
- **Functions**: >= 80%
- **Lines**: >= 80%

### Coverage Configuration

```json
// package.json
{
  "jest": {
    "coverageThreshold": {
      "global": {
        "branches": 75,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

---

## Best Practices

### 1. Test Structure

Используйте AAA pattern:
- **Arrange**: Подготовка тестовых данных
- **Act**: Выполнение действия
- **Assert**: Проверка результата

```typescript
it('should create a user', async () => {
  // Arrange
  const userData = { email: 'test@example.com', password: 'password' };

  // Act
  const user = await service.create(userData);

  // Assert
  expect(user).toHaveProperty('id');
  expect(user.email).toBe(userData.email);
});
```

### 2. Test Naming

Используйте описательные названия:

```typescript
// Good
it('should throw error when email is invalid', () => {});

// Bad
it('test email', () => {});
```

### 3. Один тест - одна проверка

```typescript
// Good
it('should return user', () => {
  expect(user).toBeDefined();
});

it('should have correct email', () => {
  expect(user.email).toBe('test@example.com');
});

// Bad
it('should work', () => {
  expect(user).toBeDefined();
  expect(user.email).toBe('test@example.com');
  expect(user.role).toBe('CLIENT');
});
```

### 4. Mock внешние зависимости

```typescript
jest.mock('../services/external-api');

beforeEach(() => {
  jest.clearAllMocks();
});
```

### 5. Тестируйте edge cases

```typescript
describe('divide', () => {
  it('should divide two numbers', () => {
    expect(divide(10, 2)).toBe(5);
  });

  it('should throw error when dividing by zero', () => {
    expect(() => divide(10, 0)).toThrow();
  });

  it('should handle negative numbers', () => {
    expect(divide(-10, 2)).toBe(-5);
  });
});
```

---

## CI/CD Integration

Тесты автоматически запускаются в GitHub Actions:

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: npm test

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/lcov.info
```

---

## Debugging Tests

### VS Code Debug Configuration

```json
{
  "type": "node",
  "request": "launch",
  "name": "Jest Debug",
  "program": "${workspaceFolder}/node_modules/.bin/jest",
  "args": ["--runInBand", "--no-cache", "--watchAll=false"],
  "console": "integratedTerminal",
  "internalConsoleOptions": "neverOpen"
}
```

### Debug Single Test

```bash
# Run specific test file
npm test -- path/to/test.spec.ts

# Run tests matching pattern
npm test -- --testNamePattern="should login user"
```

---

**Happy Testing! 🧪**
