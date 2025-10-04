# CV Project - Docker Setup Script (PowerShell)
# This script sets up the entire project using Docker Compose

param(
    [switch]$SkipTests = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting CV Project Docker Setup..." -ForegroundColor Blue

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is running
function Test-Docker {
    Write-Status "Checking Docker..."
    try {
        docker info | Out-Null
        Write-Success "Docker is running"
    }
    catch {
        Write-Error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    }
}

# Check if docker-compose is available
function Test-DockerCompose {
    Write-Status "Checking Docker Compose..."
    try {
        docker-compose --version | Out-Null
        Write-Success "Docker Compose is available"
    }
    catch {
        Write-Error "docker-compose is not installed. Please install Docker Compose and try again."
        exit 1
    }
}

# Create environment file if it doesn't exist
function Initialize-Environment {
    Write-Status "Setting up environment configuration..."

    if (-not (Test-Path "env.docker")) {
        Write-Warning "env.docker not found. Creating from env.example..."
        if (Test-Path "env.example") {
            Copy-Item "env.example" "env.docker"
            Write-Success "Created env.docker from env.example"
        }
        else {
            Write-Error "env.example not found. Please create env.docker manually."
            exit 1
        }
    }
    else {
        Write-Success "env.docker already exists"
    }
}

# Build and start services
function Start-Services {
    Write-Status "Building and starting Docker services..."

    # Stop any existing containers
    Write-Status "Stopping existing containers..."
    docker-compose down --remove-orphans

    # Build and start services
    Write-Status "Building Docker images..."
    docker-compose build --no-cache

    Write-Status "Starting services..."
    docker-compose up -d

    # Wait for services to be healthy
    Write-Status "Waiting for services to be ready..."
    Start-Sleep -Seconds 10

    # Check if services are running
    $services = docker-compose ps
    if ($services -notmatch "Up") {
        Write-Error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    }

    Write-Success "All services are running"
}

# Wait for database to be ready
function Wait-ForDatabase {
    Write-Status "Waiting for database to be ready..."

    $maxAttempts = 30
    $attempt = 1

    while ($attempt -le $maxAttempts) {
        try {
            docker-compose exec -T db pg_isready -U cvproject_user -d cvproject | Out-Null
            Write-Success "Database is ready"
            return
        }
        catch {
            Write-Status "Database not ready yet (attempt $attempt/$maxAttempts)..."
            Start-Sleep -Seconds 2
            $attempt++
        }
    }

    Write-Error "Database failed to become ready after $maxAttempts attempts"
    exit 1
}

# Run Django migrations
function Invoke-Migrations {
    Write-Status "Running Django migrations..."

    # Make migrations
    Write-Status "Creating migrations..."
    docker-compose exec -T web python manage.py makemigrations

    # Apply migrations
    Write-Status "Applying migrations..."
    docker-compose exec -T web python manage.py migrate

    Write-Success "Migrations completed"
}

# Create superuser
function New-Superuser {
    Write-Status "Creating superuser..."

    # Create superuser with predefined credentials
    $pythonScript = @"
from django.contrib.auth.models import User
import os

username = 'admin'
email = 'admin@admin.com'
password = 'admin'

if User.objects.filter(username=username).exists():
    pass
else:
    User.objects.create_superuser(username, email, password)
"@

    docker-compose exec -T web python manage.py shell -c $pythonScript

    Write-Success "Superuser created (username: admin, password: admin)"
}

# Load sample data
function Import-SampleData {
    Write-Status "Loading sample data..."

    # Load fixtures
    docker-compose exec -T web python manage.py loaddata main/fixtures/initial_data.json

    Write-Success "Sample data loaded"
}

# Collect static files
function Invoke-CollectStatic {
    Write-Status "Collecting static files..."

    docker-compose exec -T web python manage.py collectstatic --noinput --clear

    Write-Success "Static files collected"
}

# Test the setup
function Test-Setup {
    if ($SkipTests) {
        Write-Warning "Skipping setup tests"
        return
    }

    Write-Status "Testing the setup..."

    # Test if web service is responding
    $maxAttempts = 10
    $attempt = 1

    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Success "Web service is responding"
                break
            }
        }
        catch {
            Write-Status "Web service not ready yet (attempt $attempt/$maxAttempts)..."
            Start-Sleep -Seconds 3
            $attempt++
        }
    }

    if ($attempt -gt $maxAttempts) {
        Write-Warning "Web service test failed, but setup may still be successful"
    }
}

# Show final information
function Show-FinalInfo {
    Write-Host ""
    Write-Host "🎉 CV Project Setup Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Access Information:" -ForegroundColor Yellow
    Write-Host "  🌐 Web Application: http://localhost:8000" -ForegroundColor White
    Write-Host "  🔧 Admin Panel: http://localhost:8000/admin" -ForegroundColor White
    Write-Host "  📚 API: http://localhost:8000/api/" -ForegroundColor White
    Write-Host "  📊 Audit: http://localhost:8000/audit/" -ForegroundColor White
    Write-Host ""
    Write-Host "👤 Admin Credentials:" -ForegroundColor Yellow
    Write-Host "  Username: admin" -ForegroundColor White
    Write-Host "  Email: admin@admin.com" -ForegroundColor White
    Write-Host "  Password: admin" -ForegroundColor White
    Write-Host ""
    Write-Host "🛠 Useful Commands:" -ForegroundColor Yellow
    Write-Host "  View logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "  Stop services: docker-compose down" -ForegroundColor White
    Write-Host "  Restart services: docker-compose restart" -ForegroundColor White
    Write-Host "  Access web shell: docker-compose exec web python manage.py shell" -ForegroundColor White
    Write-Host ""
    Write-Host "📁 Project Structure:" -ForegroundColor Yellow
    Write-Host "  Main app: main/" -ForegroundColor White
    Write-Host "  Audit app: audit/" -ForegroundColor White
    Write-Host "  Authentication: authentication/" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 You can now start using the CV Project!" -ForegroundColor Green
}

# Main execution
function Main {
    Write-Host "==========================================" -ForegroundColor Blue
    Write-Host "🚀 CV Project Docker Setup" -ForegroundColor Blue
    Write-Host "==========================================" -ForegroundColor Blue
    Write-Host ""

    Test-Docker
    Test-DockerCompose
    Initialize-Environment
    Start-Services
    Wait-ForDatabase
    Invoke-Migrations
    New-Superuser
    Import-SampleData
    Invoke-CollectStatic
    Test-Setup
    Show-FinalInfo
}

# Run main function
Main
