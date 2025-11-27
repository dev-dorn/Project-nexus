.PHONY: help dev build test clean migrate seed logs shell

# Detect which compose command to use
DOCKER_COMPOSE = $(shell which docker-compose 2>/dev/null || echo "docker compose")

help: ## Show this help message
	@echo "E-Commerce Backend Management Commands:"
	@echo ""
	@echo "Using: $(DOCKER_COMPOSE)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development
dev: ## Start development environment
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml up --build

dev-down: ## Stop development environment
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml down

dev-logs: ## View development logs
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml logs -f

# Production
build: ## Build production images
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml build

prod: ## Start production environment
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml up -d

prod-down: ## Stop production environment
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml down

prod-logs: ## View production logs
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml logs -f

# Testing
test: ## Run tests
	$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm web pytest

test-coverage: ## Run tests with coverage
	$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm web pytest --cov --cov-report=html

# Database
migrate: ## Run database migrations
	$(DOCKER_COMPOSE) run --rm web python manage.py migrate

makemigrations: ## Create new migrations
	$(DOCKER_COMPOSE) run --rm web python manage.py makemigrations

seed: ## Seed database with sample data
	$(DOCKER_COMPOSE) run --rm web python manage.py seed_data

# Maintenance
logs: ## View application logs
	$(DOCKER_COMPOSE) logs -f web

shell: ## Open Django shell
	$(DOCKER_COMPOSE) run --rm web python manage.py shell_plus

clean: ## Clean up Docker resources
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

# Administration
create-superuser: ## Create superuser
	$(DOCKER_COMPOSE) run --rm web python manage.py createsuperuser

collectstatic: ## Collect static files
	$(DOCKER_COMPOSE) run --rm web python manage.py collectstatic --noinput

# Health
health: ## Check service health
	curl -f http://localhost:8000/health/ || echo "Service is unhealthy"

status: ## Show service status
	$(DOCKER_COMPOSE) ps

# Debug
which-compose: ## Show which compose command is being used
	@echo "Using: $(DOCKER_COMPOSE)"