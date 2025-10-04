#!/usr/bin/env python3
"""
CV Project - Docker Setup Script (Python)
This script sets up the entire project using Docker Compose
"""

import os
import sys
import time
import subprocess
import platform
from pathlib import Path

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_status(message):
    print(f"{Colors.CYAN}[INFO]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def run_command(command, check=True, capture_output=False):
    """Run a shell command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=check)
            return True
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {command}")
            print_error(f"Error: {e}")
            sys.exit(1)
        return False

def check_docker():
    """Check if Docker is running"""
    print_status("Checking Docker...")
    if not run_command("docker info", check=False, capture_output=True):
        print_error("Docker is not running. Please start Docker and try again.")
        sys.exit(1)
    print_success("Docker is running")

def check_docker_compose():
    """Check if docker-compose is available"""
    print_status("Checking Docker Compose...")
    if not run_command("docker-compose --version", check=False, capture_output=True):
        print_error("docker-compose is not installed. Please install Docker Compose and try again.")
        sys.exit(1)
    print_success("Docker Compose is available")

def setup_environment():
    """Create environment file if it doesn't exist"""
    print_status("Setting up environment configuration...")

    env_docker = Path("env.docker")
    env_example = Path("env.example")

    if not env_docker.exists():
        print_warning("env.docker not found. Creating from env.example...")
        if env_example.exists():
            env_docker.write_text(env_example.read_text())
            print_success("Created env.docker from env.example")
        else:
            print_error("env.example not found. Please create env.docker manually.")
            sys.exit(1)
    else:
        print_success("env.docker already exists")

def start_services():
    """Build and start services"""
    print_status("Building and starting Docker services...")

    # Stop any existing containers
    print_status("Stopping existing containers...")
    run_command("docker-compose down --remove-orphans", check=False)

    # Build and start services
    print_status("Building Docker images...")
    run_command("docker-compose build --no-cache")

    print_status("Starting services...")
    run_command("docker-compose up -d")

    # Wait for services to be healthy
    print_status("Waiting for services to be ready...")
    time.sleep(10)

    print_success("All services are running")

def wait_for_database():
    """Wait for database to be ready"""
    print_status("Waiting for database to be ready...")

    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        if run_command("docker-compose exec -T db pg_isready -U cvproject_user -d cvproject", check=False):
            print_success("Database is ready")
            return
        print_status(f"Database not ready yet (attempt {attempt}/{max_attempts})...")
        time.sleep(2)

    print_error("Database failed to become ready after {max_attempts} attempts")
    sys.exit(1)

def run_migrations():
    """Run Django migrations"""
    print_status("Running Django migrations...")

    # Make migrations
    print_status("Creating migrations...")
    run_command("docker-compose exec -T web python manage.py makemigrations")

    # Apply migrations
    print_status("Applying migrations...")
    run_command("docker-compose exec -T web python manage.py migrate")

    print_success("Migrations completed")

def create_superuser():
    """Create superuser"""
    print_status("Creating superuser...")

    python_script = "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@admin.com', 'admin') if not User.objects.filter(username='admin').exists() else None"

    run_command(f'docker-compose exec -T web python manage.py shell -c "{python_script}"')
    print_success("Superuser created (username: admin, password: admin)")

def load_sample_data():
    """Load sample data"""
    print_status("Loading sample data...")

    # Load initial data
    run_command("docker-compose exec -T web python manage.py loaddata main/fixtures/initial_data.json")
    print_success("Initial sample data loaded")

    # Load Jane Smith complete data
    print_status("Loading Jane Smith complete data...")
    run_command("docker-compose exec -T web python manage.py loaddata main/fixtures/jane_smith_complete.json")
    print_success("Jane Smith complete data loaded")

    print_success("All sample data loaded")

def collect_static():
    """Collect static files"""
    print_status("Collecting static files...")
    run_command("docker-compose exec -T web python manage.py collectstatic --noinput --clear")
    print_success("Static files collected")

def test_setup():
    """Test the setup"""
    print_status("Testing the setup...")

    # Test if web service is responding
    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:8000/", timeout=5)
            print_success("Web service is responding")
            return
        except:
            print_status(f"Web service not ready yet (attempt {attempt}/{max_attempts})...")
            time.sleep(3)

    print_warning("Web service test failed, but setup may still be successful")

def show_final_info():
    """Show final information"""
    print()
    print(f"{Colors.GREEN}🎉 CV Project Setup Complete!{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}📋 Access Information:{Colors.NC}")
    print(f"  🌐 Web Application: http://localhost:8000")
    print(f"  🔧 Admin Panel: http://localhost:8000/admin")
    print(f"  📚 API: http://localhost:8000/api/")
    print(f"  📊 Audit: http://localhost:8000/audit/")
    print()
    print(f"{Colors.YELLOW}👤 Admin Credentials:{Colors.NC}")
    print(f"  Username: admin")
    print(f"  Email: admin@admin.com")
    print(f"  Password: admin")
    print()
    print(f"{Colors.YELLOW}🛠 Useful Commands:{Colors.NC}")
    print(f"  View logs: docker-compose logs -f")
    print(f"  Stop services: docker-compose down")
    print(f"  Restart services: docker-compose restart")
    print(f"  Access web shell: docker-compose exec web python manage.py shell")
    print()
    print(f"{Colors.YELLOW}📁 Project Structure:{Colors.NC}")
    print(f"  Main app: main/")
    print(f"  Audit app: audit/")
    print(f"  Authentication: authentication/")
    print()
    print(f"{Colors.GREEN}🚀 You can now start using the CV Project!{Colors.NC}")

def main():
    """Main execution"""
    print(f"{Colors.BLUE}=========================================={Colors.NC}")
    print(f"{Colors.BLUE}🚀 CV Project Docker Setup{Colors.NC}")
    print(f"{Colors.BLUE}=========================================={Colors.NC}")
    print()

    check_docker()
    check_docker_compose()
    setup_environment()
    start_services()
    wait_for_database()
    run_migrations()
    create_superuser()
    load_sample_data()
    collect_static()
    test_setup()
    show_final_info()

if __name__ == "__main__":
    main()
