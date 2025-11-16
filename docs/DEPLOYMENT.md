# Deployment Guide

Руководство по развертыванию Business Consulting App в production.

## 📋 Содержание

- [Backend Deployment](#backend-deployment)
- [Mobile App Deployment](#mobile-app-deployment)
- [Database](#database)
- [Environment Variables](#environment-variables)
- [CI/CD](#cicd)

---

## Backend Deployment

### Option 1: Heroku

1. **Установите Heroku CLI:**
```bash
brew install heroku/brew/heroku
# или
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Создайте приложение:**
```bash
cd backend
heroku create your-app-name
```

3. **Добавьте PostgreSQL:**
```bash
heroku addons:create heroku-postgresql:mini
```

4. **Настройте environment variables:**
```bash
heroku config:set NODE_ENV=production
heroku config:set JWT_SECRET=your-production-secret
heroku config:set STRIPE_SECRET_KEY=sk_live_xxx
```

5. **Deploy:**
```bash
git push heroku main
```

6. **Примените миграции:**
```bash
heroku run npx prisma migrate deploy
heroku run npx prisma db seed
```

### Option 2: Railway

1. **Установите Railway CLI:**
```bash
npm i -g @railway/cli
```

2. **Войдите:**
```bash
railway login
```

3. **Инициализируйте проект:**
```bash
cd backend
railway init
```

4. **Добавьте PostgreSQL:**
```bash
railway add
# Выберите PostgreSQL
```

5. **Deploy:**
```bash
railway up
```

6. **Настройте environment:**
```bash
railway variables set NODE_ENV=production
railway variables set JWT_SECRET=your-secret
```

### Option 3: DigitalOcean App Platform

1. **Создайте app.yaml:**
```yaml
name: business-consulting-backend
services:
  - name: api
    source_dir: backend
    build_command: npm run build
    run_command: npm run start:prod
    envs:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        value: ${db.DATABASE_URL}
      - key: JWT_SECRET
        value: ${JWT_SECRET}

databases:
  - name: db
    engine: PG
    version: "15"
```

2. **Deploy через CLI:**
```bash
doctl apps create --spec app.yaml
```

### Option 4: Docker Production

1. **Build production image:**
```bash
cd backend
docker build -f Dockerfile.production -t business-consulting:latest .
```

2. **Run container:**
```bash
docker run -d \
  -p 3000:3000 \
  -e DATABASE_URL=your-db-url \
  -e JWT_SECRET=your-secret \
  --name business-consulting-api \
  business-consulting:latest
```

3. **Docker Compose для production:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: business_consulting
    volumes:
      - pg_data:/var/lib/postgresql/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    restart: always
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/business_consulting
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      - postgres

volumes:
  pg_data:
```

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 5: VPS (Ubuntu/Debian)

1. **Подключитесь к серверу:**
```bash
ssh user@your-server-ip
```

2. **Установите Node.js:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

3. **Установите PostgreSQL:**
```bash
sudo apt-get install postgresql postgresql-contrib
```

4. **Настройте PostgreSQL:**
```bash
sudo -u postgres psql
CREATE DATABASE business_consulting;
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE business_consulting TO app_user;
\q
```

5. **Клонируйте и настройте:**
```bash
git clone your-repo-url
cd Poop/backend
npm install
cp .env.example .env
# Отредактируйте .env
```

6. **Build и миграции:**
```bash
npm run build
npx prisma migrate deploy
npx prisma db seed
```

7. **Установите PM2:**
```bash
sudo npm install -g pm2
```

8. **Запустите приложение:**
```bash
pm2 start dist/main.js --name business-consulting-api
pm2 startup
pm2 save
```

9. **Настройте Nginx:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

10. **SSL с Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Mobile App Deployment

### iOS App Store

1. **Настройте EAS Build:**
```bash
cd mobile-app
npm install -g eas-cli
eas login
eas build:configure
```

2. **Создайте eas.json:**
```json
{
  "build": {
    "production": {
      "ios": {
        "bundleIdentifier": "com.businessconsulting.app",
        "distribution": "store"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@example.com",
        "ascAppId": "1234567890",
        "appleTeamId": "ABCDE12345"
      }
    }
  }
}
```

3. **Build для iOS:**
```bash
eas build --platform ios --profile production
```

4. **Submit в App Store:**
```bash
eas submit --platform ios --profile production
```

### Google Play Store

1. **Build для Android:**
```bash
eas build --platform android --profile production
```

2. **Submit в Play Store:**
```bash
eas submit --platform android --profile production
```

### Expo Updates (OTA)

Для обновлений без пересборки:

```bash
# Настройте updates
eas update:configure

# Publish update
eas update --branch production --message "Fix login bug"
```

---

## Database

### Managed Database Services

#### Heroku Postgres
```bash
heroku addons:create heroku-postgresql:standard-0
```

#### Railway PostgreSQL
```bash
railway add
# Выберите PostgreSQL
```

#### DigitalOcean Managed Database
- Создайте через веб-интерфейс
- Скопируйте connection string
- Добавьте в environment variables

#### AWS RDS
```bash
aws rds create-db-instance \
    --db-instance-identifier business-consulting-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password YourPassword \
    --allocated-storage 20
```

### Backup Strategy

1. **Автоматические бэкапы:**
```bash
# Cron job для daily backup
0 2 * * * pg_dump business_consulting > backup_$(date +\%Y\%m\%d).sql
```

2. **С Heroku:**
```bash
heroku pg:backups:schedule DATABASE_URL --at '02:00 UTC'
```

3. **Manual backup:**
```bash
pg_dump -h localhost -U postgres business_consulting > backup.sql
```

4. **Restore:**
```bash
psql -h localhost -U postgres business_consulting < backup.sql
```

---

## Environment Variables

### Production Backend .env

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db?ssl=true

# App
NODE_ENV=production
PORT=3000

# JWT
JWT_SECRET=your-very-secure-secret-key-min-32-chars
JWT_EXPIRATION=7d

# CORS
CORS_ORIGIN=https://your-app.com

# Stripe
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_PATH=./uploads

# Monitoring (optional)
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Mobile App Production Config

```typescript
// mobile-app/config.ts
export const config = {
  api: {
    baseUrl: 'https://api.your-domain.com/api',
    timeout: 10000,
  },
  socket: {
    url: 'https://api.your-domain.com',
  },
  stripe: {
    publishableKey: 'pk_live_xxxxx',
  },
};
```

---

## CI/CD

### GitHub Actions

Уже настроен в `.github/workflows/`:

- `ci.yml` - Тесты и проверки
- `deploy.yml` - Deployment

### Настройка Secrets

В GitHub Repository Settings → Secrets:

```
DATABASE_URL
JWT_SECRET
STRIPE_SECRET_KEY
EXPO_TOKEN
HEROKU_API_KEY (если используете Heroku)
RAILWAY_TOKEN (если используете Railway)
```

### Автоматический deploy

При push в `main` ветку:
1. Запускаются тесты
2. Build приложения
3. Deploy на production

---

## Monitoring

### Sentry (Error Tracking)

1. **Backend:**
```bash
npm install @sentry/node
```

```typescript
// main.ts
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
});
```

2. **Mobile App:**
```bash
npm install @sentry/react-native
```

```typescript
// App.tsx
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: 'your-dsn',
  environment: __DEV__ ? 'development' : 'production',
});
```

### Logging

**Production logging:**
```typescript
// Use Winston или Pino
import { Logger } from '@nestjs/common';

const logger = new Logger('AppName');
logger.log('Info message');
logger.error('Error message');
```

---

## Security Checklist

- [ ] HTTPS enabled
- [ ] Environment variables secured
- [ ] Database password strong
- [ ] JWT secret is random and long
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (Prisma handles this)
- [ ] XSS protection
- [ ] Helmet.js configured
- [ ] Regular dependency updates
- [ ] Security headers configured
- [ ] File upload limits set
- [ ] Stripe webhooks verified

---

## Performance Optimization

### Backend

1. **Enable compression:**
```typescript
app.use(compression());
```

2. **Add caching:**
```typescript
import { CacheModule } from '@nestjs/cache-manager';
```

3. **Database indexing:**
```prisma
model User {
  email String @unique @db.VarChar(255)
  @@index([email])
}
```

### Mobile App

1. **Code splitting**
2. **Image optimization**
3. **Lazy loading**
4. **Remove console.logs:**
```javascript
if (!__DEV__) {
  console.log = () => {};
}
```

---

## Post-Deployment

### Health Checks

```bash
curl https://your-api.com/health
```

### Monitoring

- Проверьте логи
- Настройте алерты
- Проверьте метрики
- Тестируйте критические пути

### Update Process

```bash
# 1. Pull latest
git pull origin main

# 2. Install dependencies
npm install

# 3. Run migrations
npx prisma migrate deploy

# 4. Build
npm run build

# 5. Restart
pm2 restart business-consulting-api

# 6. Health check
curl http://localhost:3000/health
```

---

**Good luck with deployment! 🚀**
