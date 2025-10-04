#!/bin/bash

# CV Project - Docker Setup Script
# This script sets up the entire project using Docker Compose

set -e  # Exit on any error

echo "🚀 Starting CV Project Docker Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if docker-compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Create environment file if it doesn't exist
setup_environment() {
    print_status "Setting up environment configuration..."

    if [ ! -f "env.docker" ]; then
        print_warning "env.docker not found. Creating from env.example..."
        if [ -f "env.example" ]; then
            cp env.example env.docker
            print_success "Created env.docker from env.example"
        else
            print_error "env.example not found. Please create env.docker manually."
            exit 1
        fi
    else
        print_success "env.docker already exists"
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting Docker services..."

    # Stop any existing containers
    print_status "Stopping existing containers..."
    docker-compose down --remove-orphans

    # Build and start services
    print_status "Building Docker images..."
    docker-compose build --no-cache

    print_status "Starting services..."
    docker-compose up -d

    # Wait for services to be healthy
    print_status "Waiting for services to be ready..."
    sleep 10

    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    fi

    print_success "All services are running"
}

# Wait for database to be ready
wait_for_database() {
    print_status "Waiting for database to be ready..."

    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T db pg_isready -U cvproject_user -d cvproject > /dev/null 2>&1; then
            print_success "Database is ready"
            return 0
        fi

        print_status "Database not ready yet (attempt $attempt/$max_attempts)..."
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "Database failed to become ready after $max_attempts attempts"
    exit 1
}

# Run Django migrations
run_migrations() {
    print_status "Running Django migrations..."

    # Make migrations
    print_status "Creating migrations..."
    docker-compose exec -T web python manage.py makemigrations

    # Apply migrations
    print_status "Applying migrations..."
    docker-compose exec -T web python manage.py migrate

    print_success "Migrations completed"
}

# Create superuser
create_superuser() {
    print_status "Creating superuser..."

    # Create superuser with predefined credentials
    docker-compose exec -T web python manage.py shell << EOF
from django.contrib.auth.models import User
import os

username = 'admin'
email = 'admin@admin.com'
password = 'admin'

if User.objects.filter(username=username).exists():
    pass
else:
    User.objects.create_superuser(username, email, password)
EOF

    print_success "Superuser created (username: admin, password: admin)"
}

# Load sample data
load_sample_data() {
    print_status "Loading sample data..."

    # Load fixtures
    docker-compose exec -T web python manage.py loaddata main/fixtures/initial_data.json

    print_success "Sample data loaded"
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."

    docker-compose exec -T web python manage.py collectstatic --noinput --clear

    print_success "Static files collected"
}

# Test the setup
test_setup() {
    print_status "Testing the setup..."

    # Test if web service is responding
    max_attempts=10
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/ > /dev/null 2>&1; then
            print_success "Web service is responding"
            break
        fi

        print_status "Web service not ready yet (attempt $attempt/$max_attempts)..."
        sleep 3
        attempt=$((attempt + 1))
    done

    if [ $attempt -gt $max_attempts ]; then
        print_warning "Web service test failed, but setup may still be successful"
    fi
}

# Show final information
show_final_info() {
    echo ""
    echo "🎉 CV Project Setup Complete!"
    echo ""
    echo "📋 Access Information:"
    echo "  🌐 Web Application: http://localhost:8000"
    echo "  🔧 Admin Panel: http://localhost:8000/admin"
    echo "  📚 API: http://localhost:8000/api/"
    echo "  📊 Audit: http://localhost:8000/audit/"
    echo ""
    echo "👤 Admin Credentials:"
    echo "  Username: admin"
    echo "  Email: admin@admin.com"
    echo "  Password: admin"
    echo ""
    echo "🛠 Useful Commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart services: docker-compose restart"
    echo "  Access web shell: docker-compose exec web python manage.py shell"
    echo ""
    echo "📁 Project Structure:"
    echo "  Main app: main/"
    echo "  Audit app: audit/"
    echo "  Authentication: authentication/"
    echo ""
    echo "🚀 You can now start using the CV Project!"
}

# Main execution
main() {
    echo "=========================================="
    echo "🚀 CV Project Docker Setup"
    echo "=========================================="
    echo ""

    check_docker
    check_docker_compose
    setup_environment
    start_services
    wait_for_database
    run_migrations
    create_superuser
    load_sample_data
    collect_static
    test_setup
    show_final_info
}

# Run main function
main "$@"
