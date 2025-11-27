# E-Commerce Backend

A robust, scalable e-commerce backend built with Django and Django REST Framework.

## Features

- 🔐 JWT Authentication & Authorization
- 🛍️ Product Catalog with Categories
- 🛒 Shopping Cart Functionality
- 📦 Order Management System
- 💳 Payment Processing (Stripe Integration)
- ⭐ Product Reviews & Ratings
- 🔍 Advanced Filtering & Search
- 📚 Comprehensive API Documentation
- 🐳 Docker Containerization
- 🔄 CI/CD with GitHub Actions

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL

### Development
```bash
# Clone the repository
git clone <repository-url>
cd ecommerce-backend

# Copy environment file
cp .env.example .env

# Start development environment
make dev

**Makefile**
```makefile
.PHONY: help dev build test clean migrate seed logs shell

help: ## Show this help message
	@echo "E-Commerce Backend Management Commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development
dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up --build

dev-down: ## Stop development environment
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## View development logs
	docker-compose -f docker-compose.dev.yml logs -f

# Production
build: ## Build production images
	docker-compose -f docker-compose.prod.yml build

prod: ## Start production environment
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## View production logs
	docker-compose -f docker-compose.prod.yml logs -f

# Testing
test: ## Run tests
	docker-compose -f docker-compose.test.yml run --rm web pytest

test-coverage: ## Run tests with coverage
	docker-compose -f docker-compose.test.yml run --rm web pytest --cov --cov-report=html

test-watch: ## Run tests in watch mode
	docker-compose -f docker-compose.test.yml run --rm web ptw

# Database
migrate: ## Run database migrations
	docker-compose run --rm web python manage.py migrate

makemigrations: ## Create new migrations
	docker-compose run --rm web python manage.py makemigrations

migrations: makemigrations ## Alias for makemigrations

seed: ## Seed database with sample data
	docker-compose run --rm web python manage.py seed_data

reset-db: ## Reset database (development only)
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml up -d db
	sleep 5
	docker-compose run --rm web python manage.py migrate
	docker-compose run --rm web python manage.py seed_data

# Maintenance
logs: ## View application logs
	docker-compose logs -f web

shell: ## Open Django shell
	docker-compose run --rm web python manage.py shell_plus

dbshell: ## Open database shell
	docker-compose exec db psql -U postgres -d ecommerce_dev

clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

# Code Quality
lint: ## Run code linting
	docker-compose run --rm web black --check .
	docker-compose run --rm web flake8 .
	docker-compose run --rm web isort --check-only .

format: ## Format code automatically
	docker-compose run --rm web black .
	docker-compose run --rm web isort .

security: ## Run security checks
	docker-compose run --rm web bandit -r .
	docker-compose run --rm web safety check

# Administration
create-superuser: ## Create superuser
	docker-compose run --rm web python manage.py createsuperuser

collectstatic: ## Collect static files
	docker-compose run --rm web python manage.py collectstatic --noinput

backup: ## Backup database
	./scripts/database/backup.py

restore: ## Restore database
	./scripts/database/restore.py

# Health
health: ## Check service health
	curl -f http://localhost:8000/health/ || echo "Service is unhealthy"

status: ## Show service status
	docker-compose ps

# Documentation
docs: ## Generate API documentation
	docker-compose run --rm web python manage.py spectacular --file docs/api/openapi.yaml

serve-docs: ## Serve documentation locally
	python -m http.server 8001 -d docs/