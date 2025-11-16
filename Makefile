.PHONY: help setup start stop restart logs clean seed migrate reset-db mobile backend install

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '$(BLUE)Business Consulting App - Makefile Commands$(NC)'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

setup: ## Install all dependencies and setup project
	@echo '$(BLUE)Setting up project...$(NC)'
	@./scripts/dev.sh setup

install: setup ## Alias for setup

start: ## Start Docker containers (database + backend)
	@echo '$(BLUE)Starting services...$(NC)'
	@./scripts/dev.sh start

stop: ## Stop Docker containers
	@echo '$(BLUE)Stopping services...$(NC)'
	@./scripts/dev.sh stop

restart: ## Restart Docker containers
	@echo '$(BLUE)Restarting services...$(NC)'
	@./scripts/dev.sh restart

logs: ## Show Docker logs
	@./scripts/dev.sh logs

clean: ## Clean all dependencies and build files
	@./scripts/dev.sh clean

seed: ## Seed database with test data
	@./scripts/dev.sh seed

migrate: ## Run database migrations
	@./scripts/dev.sh migrate

reset-db: ## Reset database (WARNING: destructive)
	@./scripts/dev.sh reset-db

mobile: ## Start mobile app (Expo)
	@echo '$(BLUE)Starting mobile app...$(NC)'
	@cd mobile-app && npm start

backend: ## Start backend in dev mode (without Docker)
	@echo '$(BLUE)Starting backend...$(NC)'
	@cd backend && npm run start:dev

prisma-studio: ## Open Prisma Studio
	@echo '$(BLUE)Opening Prisma Studio...$(NC)'
	@cd backend && npx prisma studio

test-backend: ## Run backend tests
	@echo '$(BLUE)Running backend tests...$(NC)'
	@cd backend && npm test

lint-backend: ## Lint backend code
	@echo '$(BLUE)Linting backend...$(NC)'
	@cd backend && npm run lint

lint-mobile: ## Lint mobile app code
	@echo '$(BLUE)Linting mobile app...$(NC)'
	@cd mobile-app && npm run lint

docker-build: ## Build Docker images
	@echo '$(BLUE)Building Docker images...$(NC)'
	@docker-compose build

docker-clean: ## Clean Docker volumes and images
	@echo '$(BLUE)Cleaning Docker...$(NC)'
	@docker-compose down -v
	@docker system prune -f

dev: start ## Start development environment
	@echo '$(GREEN)Development environment started!$(NC)'
	@echo ''
	@echo 'Services:'
	@echo '  - Backend API: http://localhost:3000'
	@echo '  - API Docs: http://localhost:3000/api/docs'
	@echo '  - PostgreSQL: localhost:5432'
	@echo ''
	@echo 'Next steps:'
	@echo '  - Run migrations: make migrate'
	@echo '  - Seed database: make seed'
	@echo '  - Start mobile app: make mobile'

full-start: start migrate seed ## Start and setup everything
	@echo '$(GREEN)Full environment started and configured!$(NC)'
