# CVProject Docker Management
# Makefile for easy Docker operations

.PHONY: help build up down restart logs shell test clean

# Default target
help:
	@echo "CVProject Docker Management"
	@echo "=========================="
	@echo ""
	@echo "Available commands:"
	@echo "  build     - Build Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - Show logs from all services"
	@echo "  shell     - Open shell in web container"
	@echo "  test      - Run tests in Docker"
	@echo "  clean     - Clean up Docker resources"
	@echo "  migrate   - Run Django migrations"
	@echo "  collectstatic - Collect static files"
	@echo "  createsuperuser - Create Django superuser"
	@echo "  loaddata  - Load sample data"
	@echo ""

# Build Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Restart all services
restart: down up

# Show logs
logs:
	docker-compose logs -f

# Open shell in web container
shell:
	docker-compose exec web bash

# Run tests
test:
	docker-compose exec web python manage.py test

# Clean up Docker resources
clean:
	docker-compose down -v
	docker system prune -f

# Django management commands
migrate:
	docker-compose exec web python manage.py migrate

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

loaddata:
	docker-compose exec web python manage.py load_sample_data --clear

# Development commands
dev-up:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

dev-down:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Production commands
prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Database commands
db-shell:
	docker-compose exec db psql -U cvproject_user -d cvproject

db-backup:
	docker-compose exec db pg_dump -U cvproject_user cvproject > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore:
	docker-compose exec -T db psql -U cvproject_user -d cvproject < $(FILE)

# Health check
health:
	@echo "Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "Testing web service..."
	@curl -f http://localhost:8000/ || echo "Web service not responding"
	@echo ""
	@echo "Testing database connection..."
	@docker-compose exec web python manage.py check --database default || echo "Database connection failed"
