#!/bin/bash
set -e

echo "================================================"
echo "Production Deployment Script"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Load environment variables
if [ -f ".env.production" ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
fi

# Pull latest changes (if using git deployment)
if [ -d ".git" ]; then
    print_info "Pulling latest changes from repository..."
    git pull origin main
    print_success "Repository updated"
fi

# Stop running containers
print_info "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build new images
print_info "Building new Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache backend

# Start services
print_info "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 10

# Run migrations
print_info "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend sh -c "npx prisma migrate deploy"

# Check health
print_info "Checking service health..."
sleep 5

if curl -f http://localhost:${BACKEND_PORT:-3000}/health > /dev/null 2>&1; then
    print_success "Backend is healthy"
else
    echo "Warning: Backend health check failed"
    docker-compose -f docker-compose.prod.yml logs --tail=50 backend
fi

# Show running containers
echo ""
print_success "Deployment completed!"
echo ""
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "Useful commands:"
echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop services: docker-compose -f docker-compose.prod.yml down"
echo "  Restart backend: docker-compose -f docker-compose.prod.yml restart backend"
echo ""
