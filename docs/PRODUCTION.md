# Production Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Database Migrations](#database-migrations)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Docker (v20.10+)
- Docker Compose (v2.0+)
- Git
- OpenSSL (for generating secrets)

### Server Requirements
- **Minimum:** 2 CPU cores, 4GB RAM, 20GB storage
- **Recommended:** 4 CPU cores, 8GB RAM, 50GB storage
- Ubuntu 20.04 LTS or later (or equivalent)

### Ports
- `80` - HTTP (redirects to HTTPS)
- `443` - HTTPS
- `3000` - Backend API (internal, optional external access)
- `5432` - PostgreSQL (internal only)

## Initial Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd Poop
```

### 2. Create Production Environment File

```bash
cp backend/.env.production.example .env.production
```

### 3. Configure Environment Variables

Edit `.env.production` and replace all placeholder values:

#### Critical Variables

```bash
# Generate JWT secret
openssl rand -base64 32

# Generate PostgreSQL password
openssl rand -base64 24
```

Update `.env.production`:
```env
JWT_SECRET="<your-generated-jwt-secret>"
POSTGRES_PASSWORD="<your-generated-password>"
STRIPE_SECRET_KEY="sk_live_<your-stripe-key>"
STRIPE_WEBHOOK_SECRET="whsec_<your-webhook-secret>"
CORS_ORIGIN="https://yourdomain.com,https://app.yourdomain.com"
```

### 4. SSL Certificates

#### Option A: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chmod 644 nginx/ssl/*.pem
```

#### Option B: Self-Signed (Development/Testing)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

### 5. Initialize Production Environment

```bash
chmod +x scripts/*.sh
./scripts/init-prod.sh
```

This script will:
- Check prerequisites
- Validate configuration
- Run security checks
- Build Docker images

## Configuration

### Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | `postgresql://user:pass@postgres:5432/db` |
| `JWT_SECRET` | Secret for JWT tokens | Yes | `<long-random-string>` |
| `JWT_EXPIRATION` | Token expiration time | No | `7d` |
| `STRIPE_SECRET_KEY` | Stripe API secret key | Yes | `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | No | `whsec_...` |
| `CORS_ORIGIN` | Allowed origins | Yes | `https://yourdomain.com` |
| `PORT` | Backend port | No | `3000` |
| `NODE_ENV` | Environment | Yes | `production` |

### Docker Compose Profiles

The `docker-compose.prod.yml` supports profiles:

```bash
# Start without Nginx (use external reverse proxy)
docker-compose -f docker-compose.prod.yml up -d

# Start with Nginx reverse proxy
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

## Deployment

### First-Time Deployment

```bash
# 1. Start services
docker-compose -f docker-compose.prod.yml up -d

# 2. Wait for database to be ready
docker-compose -f docker-compose.prod.yml logs -f postgres

# 3. Run migrations
./scripts/migrate-prod.sh

# 4. Verify deployment
curl https://yourdomain.com/health
```

### Update Deployment

```bash
./scripts/deploy-prod.sh
```

This script will:
1. Pull latest changes (if using git)
2. Stop existing containers
3. Build new images
4. Start services
5. Run migrations
6. Perform health checks

### Manual Deployment Steps

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend npx prisma migrate deploy
```

## Database Migrations

### Running Migrations

```bash
# Using script (recommended)
./scripts/migrate-prod.sh

# Or manually
docker-compose -f docker-compose.prod.yml exec backend npx prisma migrate deploy
```

### Check Migration Status

```bash
docker-compose -f docker-compose.prod.yml exec backend npx prisma migrate status
```

### Rollback Migration

```bash
# Restore from backup first!
docker-compose -f docker-compose.prod.yml exec backend npx prisma migrate resolve --rolled-back <migration_name>
```

## Monitoring

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f postgres

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Health Checks

```bash
# Backend health
curl https://yourdomain.com/health

# Database health
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Container status
docker-compose -f docker-compose.prod.yml ps
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Backup & Recovery

### Database Backup

#### Create Backup

```bash
# Automated backup script
docker-compose -f docker-compose.prod.yml exec postgres pg_dump \
  -U prod_user business_consulting_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# With compression
docker-compose -f docker-compose.prod.yml exec postgres pg_dump \
  -U prod_user business_consulting_prod | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Restore Backup

```bash
# Stop backend
docker-compose -f docker-compose.prod.yml stop backend

# Restore database
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U prod_user business_consulting_prod

# Or from compressed
gunzip -c backup.sql.gz | docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U prod_user business_consulting_prod

# Start backend
docker-compose -f docker-compose.prod.yml start backend
```

### Uploaded Files Backup

```bash
# Backup uploads volume
docker run --rm -v business-consulting_uploads_data:/data \
  -v $(pwd)/backups:/backup alpine \
  tar czf /backup/uploads_$(date +%Y%m%d).tar.gz -C /data .

# Restore uploads
docker run --rm -v business-consulting_uploads_data:/data \
  -v $(pwd)/backups:/backup alpine \
  tar xzf /backup/uploads_YYYYMMDD.tar.gz -C /data
```

### Automated Backups

Add to crontab:

```bash
# Daily database backup at 2 AM
0 2 * * * cd /path/to/project && docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U prod_user business_consulting_prod | gzip > backups/db_$(date +\%Y\%m\%d).sql.gz

# Weekly uploads backup on Sunday at 3 AM
0 3 * * 0 cd /path/to/project && docker run --rm -v business-consulting_uploads_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/uploads_$(date +\%Y\%m\%d).tar.gz -C /data .

# Delete backups older than 30 days
0 4 * * * find /path/to/project/backups -name "*.gz" -mtime +30 -delete
```

## Security

### Security Checklist

- [ ] Strong JWT_SECRET (32+ characters)
- [ ] Strong POSTGRES_PASSWORD
- [ ] SSL/TLS certificates configured
- [ ] CORS origins restricted to your domains
- [ ] Firewall configured (UFW or iptables)
- [ ] Regular security updates
- [ ] Database backups automated
- [ ] Log monitoring enabled
- [ ] Rate limiting configured
- [ ] File upload size limits set

### Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Update SSL Certificates

```bash
# Let's Encrypt auto-renewal
sudo certbot renew --dry-run

# Setup auto-renewal cron
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet --post-hook "docker-compose -f /path/to/docker-compose.prod.yml restart nginx"
```

## Troubleshooting

### Backend Not Starting

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Common issues:
# 1. DATABASE_URL incorrect
# 2. Missing environment variables
# 3. Port conflict

# Verify environment
docker-compose -f docker-compose.prod.yml exec backend env | grep -E "DATABASE_URL|JWT_SECRET"
```

### Database Connection Failed

```bash
# Check if postgres is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check postgres logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U prod_user -d business_consulting_prod -c "SELECT 1"
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Clear unused Docker resources
docker system prune -a
```

### Stripe Webhooks Not Working

```bash
# Check webhook secret
docker-compose -f docker-compose.prod.yml exec backend env | grep STRIPE_WEBHOOK_SECRET

# Check backend logs for webhook errors
docker-compose -f docker-compose.prod.yml logs backend | grep webhook

# Test webhook endpoint
curl -X POST https://yourdomain.com/payments/webhook \
  -H "stripe-signature: test" \
  -d '{}'
```

## Maintenance

### Update Node Dependencies

```bash
# In backend directory
npm audit fix
npm update

# Rebuild image
docker-compose -f docker-compose.prod.yml build --no-cache backend
```

### Clean Up Docker

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes (BE CAREFUL!)
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

### Scale Services

```bash
# Scale backend to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Performance Optimization

### Database Connection Pooling

In `.env.production`:
```env
DATABASE_URL="postgresql://user:pass@postgres:5432/db?schema=public&connection_limit=10&pool_timeout=20"
```

### Enable Redis Caching (Optional)

Add to `docker-compose.prod.yml`:
```yaml
redis:
  image: redis:7-alpine
  restart: unless-stopped
  volumes:
    - redis_data:/data
```

## Support

For issues and questions:
- Check logs first
- Review this documentation
- Check GitHub issues
- Contact DevOps team

## Additional Resources

- [Prisma Production Best Practices](https://www.prisma.io/docs/guides/performance-and-optimization/deployment)
- [Docker Production Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [NestJS Performance](https://docs.nestjs.com/techniques/performance)
