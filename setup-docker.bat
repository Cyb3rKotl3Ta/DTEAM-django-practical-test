@echo off
REM CV Project - Docker Setup Script (Windows Batch)
REM This script sets up the entire project using Docker Compose

echo.
echo ==========================================
echo 🚀 CV Project Docker Setup
echo ==========================================
echo.

REM Check if Docker is running
echo [INFO] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is running

REM Check if docker-compose is available
echo [INFO] Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] docker-compose is not installed. Please install Docker Compose and try again.
    pause
    exit /b 1
)
echo [SUCCESS] Docker Compose is available

REM Create environment file if it doesn't exist
echo [INFO] Setting up environment configuration...
if not exist "env.docker" (
    echo [WARNING] env.docker not found. Creating from env.example...
    if exist "env.example" (
        copy "env.example" "env.docker" >nul
        echo [SUCCESS] Created env.docker from env.example
    ) else (
        echo [ERROR] env.example not found. Please create env.docker manually.
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] env.docker already exists
)

REM Build and start services
echo [INFO] Building and starting Docker services...
echo [INFO] Stopping existing containers...
docker-compose down --remove-orphans

echo [INFO] Building Docker images...
docker-compose build --no-cache

echo [INFO] Starting services...
docker-compose up -d

REM Wait for services to be healthy
echo [INFO] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Run Django migrations
echo [INFO] Running Django migrations...
echo [INFO] Creating migrations...
docker-compose exec -T web python manage.py makemigrations

echo [INFO] Applying migrations...
docker-compose exec -T web python manage.py migrate

echo [SUCCESS] Migrations completed

REM Create superuser
echo [INFO] Creating superuser...
docker-compose exec -T web python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@admin.com', 'admin') if not User.objects.filter(username='admin').exists() else None"

echo [SUCCESS] Superuser created (username: admin, password: admin)

REM Load sample data
echo [INFO] Loading sample data...
docker-compose exec -T web python manage.py loaddata main/fixtures/initial_data.json

echo [SUCCESS] Sample data loaded

REM Collect static files
echo [INFO] Collecting static files...
docker-compose exec -T web python manage.py collectstatic --noinput --clear

echo [SUCCESS] Static files collected

REM Show final information
echo.
echo 🎉 CV Project Setup Complete!
echo.
echo 📋 Access Information:
echo   🌐 Web Application: http://localhost:8000
echo   🔧 Admin Panel: http://localhost:8000/admin
echo   📚 API: http://localhost:8000/api/
echo   📊 Audit: http://localhost:8000/audit/
echo.
echo 👤 Admin Credentials:
echo   Username: admin
echo   Email: admin@admin.com
echo   Password: admin
echo.
echo 🛠 Useful Commands:
echo   View logs: docker-compose logs -f
echo   Stop services: docker-compose down
echo   Restart services: docker-compose restart
echo   Access web shell: docker-compose exec web python manage.py shell
echo.
echo 📁 Project Structure:
echo   Main app: main/
echo   Audit app: audit/
echo   Authentication: authentication/
echo.
echo 🚀 You can now start using the CV Project!
echo.
pause
