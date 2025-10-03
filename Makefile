# Makefile for CVProject Docker operations
# Following SOLID principles and DRY approach

.PHONY: help build up down restart logs shell test clean

# Default target
help:
	@echo "CVProject Docker Commands:"
	@echo "  build     - Build Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - Show logs from all services"
	@echo "  shell     - Open shell in web container"
	@echo "  test      - Run tests in Docker"
	@echo "  clean     - Clean up Docker resources"
	@echo "  migrate   - Run database migrations"
	@echo "  collectstatic - Collect static files"
	@echo "  createsuperuser - Create Django superuser"

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

# Database operations
migrate:
	docker-compose exec web python manage.py migrate

# Collect static files
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Load sample data
loaddata:
	docker-compose exec web python manage.py load_sample_data --clear

# Development setup
dev-setup: build up migrate collectstatic loaddata
	@echo "Development environment is ready!"
	@echo "Visit http://localhost to access the application"

# Production setup
prod-setup: build up migrate collectstatic
	@echo "Production environment is ready!"
	@echo "Visit http://localhost to access the application"
