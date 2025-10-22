.PHONY: help build up down restart logs shell test clean health migrate createsuperuser

help:
	@echo "Telegram Bot Service - Docker Commands"
	@echo "======================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs"
	@echo "  make logs-web       - View web service logs"
	@echo "  make shell          - Open shell in web container"
	@echo "  make test           - Run tests"
	@echo "  make health         - Check service health"
	@echo "  make migrate        - Run database migrations"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make ps             - Show running containers"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started! Check status with: make ps"
	@echo "Health check: make health"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web



shell:
	docker-compose exec web bash

test:
	docker-compose --profile test run --rm test

health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/api/health/ | python3 -m json.tool || echo "Service not responding"

migrate:
	docker-compose exec web python manage.py migrate

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

clean:
	docker-compose down -v
	@echo "All containers and volumes removed"

ps:
	docker-compose ps

# Development helpers
dev-setup: build up migrate
	@echo "Development environment ready!"
	@echo "Create a superuser with: make createsuperuser"

full-test: build up
	@sleep 10
	@make health
	@make test
