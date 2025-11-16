#!/bin/bash

# Development helper script

set -e

echo "🚀 Business Consulting App - Development Helper"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
start_docker() {
    echo -e "${BLUE}Starting Docker containers...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ Docker containers started${NC}"
    echo ""
    echo "Services:"
    echo "  - Backend API: http://localhost:3000"
    echo "  - API Docs: http://localhost:3000/api/docs"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - PGAdmin: http://localhost:5050 (run with --profile debug)"
}

stop_docker() {
    echo -e "${BLUE}Stopping Docker containers...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Docker containers stopped${NC}"
}

restart_docker() {
    echo -e "${BLUE}Restarting Docker containers...${NC}"
    docker-compose restart
    echo -e "${GREEN}✓ Docker containers restarted${NC}"
}

logs() {
    echo -e "${BLUE}Showing Docker logs...${NC}"
    docker-compose logs -f
}

setup() {
    echo -e "${BLUE}Setting up project...${NC}"

    # Install root dependencies
    echo -e "${YELLOW}Installing root dependencies...${NC}"
    npm install

    # Install mobile app dependencies
    echo -e "${YELLOW}Installing mobile app dependencies...${NC}"
    cd mobile-app && npm install && cd ..

    # Install backend dependencies
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    cd backend && npm install && cd ..

    # Install shared dependencies
    echo -e "${YELLOW}Installing shared dependencies...${NC}"
    cd shared && npm install && cd ..

    # Copy env file
    if [ ! -f backend/.env ]; then
        echo -e "${YELLOW}Creating backend .env file...${NC}"
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✓ Created backend/.env - please update with your values${NC}"
    fi

    echo -e "${GREEN}✓ Project setup complete!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Update backend/.env with your database credentials"
    echo "  2. Run: ./scripts/dev.sh start"
    echo "  3. Run migrations: cd backend && npm run prisma:migrate"
    echo "  4. Seed database: cd backend && npm run prisma:seed"
}

seed() {
    echo -e "${BLUE}Seeding database...${NC}"
    cd backend && npm run prisma:seed && cd ..
    echo -e "${GREEN}✓ Database seeded successfully${NC}"
}

migrate() {
    echo -e "${BLUE}Running database migrations...${NC}"
    cd backend && npm run prisma:migrate && cd ..
    echo -e "${GREEN}✓ Migrations completed${NC}"
}

reset_db() {
    echo -e "${RED}WARNING: This will reset your database!${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        echo -e "${BLUE}Resetting database...${NC}"
        cd backend && npx prisma migrate reset --force && cd ..
        echo -e "${GREEN}✓ Database reset complete${NC}"
    else
        echo "Cancelled."
    fi
}

clean() {
    echo -e "${BLUE}Cleaning project...${NC}"

    echo "Removing node_modules..."
    rm -rf node_modules mobile-app/node_modules backend/node_modules shared/node_modules

    echo "Removing build files..."
    rm -rf backend/dist mobile-app/.expo

    echo "Removing lock files..."
    rm -f package-lock.json mobile-app/package-lock.json backend/package-lock.json shared/package-lock.json

    echo -e "${GREEN}✓ Project cleaned${NC}"
    echo "Run './scripts/dev.sh setup' to reinstall"
}

# Main menu
case "$1" in
    start)
        start_docker
        ;;
    stop)
        stop_docker
        ;;
    restart)
        restart_docker
        ;;
    logs)
        logs
        ;;
    setup)
        setup
        ;;
    seed)
        seed
        ;;
    migrate)
        migrate
        ;;
    reset-db)
        reset_db
        ;;
    clean)
        clean
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|setup|seed|migrate|reset-db|clean}"
        echo ""
        echo "Commands:"
        echo "  start     - Start Docker containers"
        echo "  stop      - Stop Docker containers"
        echo "  restart   - Restart Docker containers"
        echo "  logs      - Show Docker logs"
        echo "  setup     - Setup project (install dependencies)"
        echo "  seed      - Seed database with test data"
        echo "  migrate   - Run database migrations"
        echo "  reset-db  - Reset database (WARNING: destructive)"
        echo "  clean     - Clean all dependencies and build files"
        exit 1
        ;;
esac
