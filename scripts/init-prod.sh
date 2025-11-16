#!/bin/bash
set -e

echo "================================================"
echo "Production Environment Initialization"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
echo ""
echo "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed"
    exit 1
fi
print_success "Docker is installed"

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed"
    exit 1
fi
print_success "Docker Compose is installed"

# Check for .env file
echo ""
echo "Checking environment configuration..."

if [ ! -f ".env.production" ]; then
    print_error ".env.production file not found"
    echo ""
    echo "Please create .env.production file based on backend/.env.production.example"
    echo "Run: cp backend/.env.production.example .env.production"
    exit 1
fi
print_success ".env.production file exists"

# Security checks
echo ""
echo "Running security checks..."

# Check JWT_SECRET
JWT_SECRET=$(grep "^JWT_SECRET=" .env.production | cut -d '=' -f2 | tr -d '"' | tr -d "'")
if [ -z "$JWT_SECRET" ] || [ "$JWT_SECRET" = "CHANGE_THIS_TO_A_LONG_RANDOM_STRING_AT_LEAST_32_CHARACTERS" ]; then
    print_error "JWT_SECRET is not set or uses default value"
    echo "Generate a strong secret with: openssl rand -base64 32"
    exit 1
fi
if [ ${#JWT_SECRET} -lt 32 ]; then
    print_warning "JWT_SECRET is shorter than 32 characters"
fi
print_success "JWT_SECRET is configured"

# Check POSTGRES_PASSWORD
POSTGRES_PASSWORD=$(grep "^POSTGRES_PASSWORD=" .env.production | cut -d '=' -f2 | tr -d '"' | tr -d "'")
if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "CHANGE_THIS_PASSWORD" ]; then
    print_error "POSTGRES_PASSWORD is not set or uses default value"
    exit 1
fi
print_success "POSTGRES_PASSWORD is configured"

# Check Stripe keys
STRIPE_SECRET=$(grep "^STRIPE_SECRET_KEY=" .env.production | cut -d '=' -f2)
if [[ $STRIPE_SECRET == *"YOUR_LIVE_STRIPE_SECRET_KEY"* ]]; then
    print_warning "Stripe secret key appears to be a placeholder"
fi
print_success "Stripe configuration checked"

# Create necessary directories
echo ""
echo "Creating necessary directories..."

mkdir -p logs
mkdir -p nginx/ssl
print_success "Directories created"

# Build Docker images
echo ""
echo "Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

print_success "Docker images built"

echo ""
echo "================================================"
echo -e "${GREEN}Production environment initialized successfully!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Review .env.production file"
echo "2. Start services: docker-compose -f docker-compose.prod.yml up -d"
echo "3. Run migrations: ./scripts/migrate-prod.sh"
echo "4. Check logs: docker-compose -f docker-compose.prod.yml logs -f"
echo ""
