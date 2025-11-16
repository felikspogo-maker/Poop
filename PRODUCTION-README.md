# Production Deployment Quick Start

## 🚀 Deploy to Production in 5 Minutes

### Prerequisites
- Server with Docker and Docker Compose installed
- Domain name with DNS pointing to your server
- SSL certificates (Let's Encrypt recommended)

### Quick Start

```bash
# 1. Clone and navigate
git clone <your-repo>
cd Poop

# 2. Create production environment file
cp backend/.env.production.example .env.production

# 3. Configure (replace all CHANGE_THIS values)
nano .env.production

# Generate secrets:
openssl rand -base64 32  # For JWT_SECRET
openssl rand -base64 24  # For POSTGRES_PASSWORD

# 4. Setup SSL certificates
mkdir -p nginx/ssl
# Copy your SSL certificates to nginx/ssl/cert.pem and nginx/ssl/key.pem

# 5. Initialize production environment
chmod +x scripts/*.sh
./scripts/init-prod.sh

# 6. Deploy
./scripts/deploy-prod.sh
```

### Verify Deployment

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check health
curl https://yourdomain.com/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📋 Environment Variables Checklist

**Critical** (must change):
- [ ] `JWT_SECRET` - Generate with `openssl rand -base64 32`
- [ ] `POSTGRES_PASSWORD` - Generate with `openssl rand -base64 24`
- [ ] `STRIPE_SECRET_KEY` - Your Stripe live secret key
- [ ] `CORS_ORIGIN` - Your production domain(s)

**Important** (recommended to change):
- [ ] `STRIPE_WEBHOOK_SECRET` - From Stripe dashboard
- [ ] `POSTGRES_USER` - Change from default

**Optional**:
- [ ] `JWT_EXPIRATION` - Token lifetime (default: 7d)
- [ ] `BACKEND_PORT` - External port (default: 3000)
- [ ] `MAX_FILE_SIZE` - Upload limit (default: 10MB)

## 🔒 SSL Certificate Setup

### Option 1: Let's Encrypt (Free, Recommended)

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy to nginx
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# Setup auto-renewal
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet
```

### Option 2: CloudFlare (Easiest)

1. Add your domain to CloudFlare
2. Enable CloudFlare proxy (orange cloud)
3. Set SSL/TLS mode to "Full"
4. Use CloudFlare origin certificates in nginx/ssl/

## 📦 Deployment Modes

### With Nginx Reverse Proxy (Recommended)

```bash
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

Includes:
- Automatic HTTP to HTTPS redirect
- SSL termination
- Rate limiting
- Static file serving
- WebSocket support

### Without Nginx (Use External Load Balancer)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Use when:
- Behind AWS ALB, CloudFlare, or other load balancer
- Using Kubernetes Ingress
- Have existing reverse proxy

## 🔄 Common Operations

### Update Application

```bash
./scripts/deploy-prod.sh
```

### Database Backup

```bash
docker-compose -f docker-compose.prod.yml exec postgres pg_dump \
  -U prod_user business_consulting_prod > backup_$(date +%Y%m%d).sql
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Just backend
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Restart Services

```bash
# All services
docker-compose -f docker-compose.prod.yml restart

# Just backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Stop Services

```bash
docker-compose -f docker-compose.prod.yml down
```

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Verify environment
docker-compose -f docker-compose.prod.yml exec backend env
```

### Database connection error
```bash
# Check postgres is running
docker-compose -f docker-compose.prod.yml ps postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U prod_user -d business_consulting_prod -c "SELECT 1"
```

### Port already in use
```bash
# Change BACKEND_PORT in .env.production
echo "BACKEND_PORT=3001" >> .env.production

# Or stop conflicting service
sudo lsof -i :3000
```

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl https://yourdomain.com/health

# Should return:
# {
#   "status": "ok",
#   "info": {...},
#   "error": {},
#   "details": {...}
# }
```

### Container Stats

```bash
# Real-time resource usage
docker stats

# Disk usage
docker system df
```

## 🔐 Security Checklist

Production security checklist:

- [ ] Strong JWT_SECRET (32+ characters)
- [ ] Strong POSTGRES_PASSWORD
- [ ] SSL/TLS enabled
- [ ] CORS restricted to your domains
- [ ] Firewall configured (ports 80, 443 only)
- [ ] Regular database backups
- [ ] Log monitoring enabled
- [ ] Stripe webhook secret configured
- [ ] File upload limits set
- [ ] Rate limiting enabled

### Firewall Setup (Ubuntu/Debian)

```bash
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw enable
```

## 📚 Full Documentation

For detailed production deployment guide, see:
- [docs/PRODUCTION.md](docs/PRODUCTION.md) - Complete production guide
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Platform-specific deployments
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture

## 🆘 Support

Issues? Check:
1. [Troubleshooting section](docs/PRODUCTION.md#troubleshooting)
2. Service logs: `docker-compose -f docker-compose.prod.yml logs`
3. GitHub Issues

## 🚨 Emergency Rollback

```bash
# Stop current version
docker-compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout HEAD~1

# Deploy previous version
./scripts/deploy-prod.sh
```

---

**Ready for production!** 🎉

For questions or issues, refer to the full [Production Guide](docs/PRODUCTION.md).
