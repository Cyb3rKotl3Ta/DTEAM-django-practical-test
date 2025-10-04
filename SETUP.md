# 🚀 Quick Setup Guide

This guide provides multiple ways to set up the CV Project using Docker Compose without the Makefile.

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** available
- **Git** (to clone the repository)

## 🎯 Quick Start Options

### Option 1: PowerShell Script (Windows - Recommended)
```powershell
# Run the PowerShell setup script
.\setup-docker.ps1

# Or with execution policy bypass
PowerShell -ExecutionPolicy Bypass -File .\setup-docker.ps1
```

### Option 2: Batch Script (Windows)
```cmd
# Run the batch setup script
setup-docker.bat
```

### Option 3: Bash Script (Linux/macOS)
```bash
# Make the script executable
chmod +x setup-docker.sh

# Run the bash setup script
./setup-docker.sh
```

### Option 4: Python Script (Cross-platform)
```bash
# Run the Python setup script
python setup-docker.py

# Or with Python 3 explicitly
python3 setup-docker.py
```

## 🔧 What the Scripts Do

All setup scripts perform the following steps automatically:

1. **✅ Check Prerequisites**
   - Verify Docker is running
   - Verify Docker Compose is available

2. **⚙️ Environment Setup**
   - Create `env.docker` from `env.example` if needed
   - Configure environment variables

3. **🐳 Docker Services**
   - Stop existing containers
   - Build Docker images
   - Start all services (web, db, redis, celery)

4. **🗄️ Database Setup**
   - Wait for database to be ready
   - Run Django migrations
   - Create database tables

5. **👤 User Management**
   - Create superuser account
   - Username: `admin`
   - Email: `admin@admin.com`
   - Password: `admin`

6. **📊 Sample Data**
   - Load initial CV data
   - Load sample skills and projects
   - Load contact information

7. **🎨 Static Files**
   - Collect static files
   - Prepare for production

8. **🧪 Testing**
   - Test web service response
   - Verify setup completion

## 🌐 Access Information

After successful setup, you can access:

- **🌐 Web Application**: http://localhost:8000
- **🔧 Admin Panel**: http://localhost:8000/admin
- **📚 API**: http://localhost:8000/api/
- **📊 Audit**: http://localhost:8000/audit/

## 👤 Admin Credentials

- **Username**: `admin`
- **Email**: `admin@admin.com`
- **Password**: `admin`

## 🛠 Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Access web shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web python manage.py test

# Create new migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

## 🚨 Troubleshooting

### Common Issues

#### Docker Not Running
```
[ERROR] Docker is not running. Please start Docker Desktop and try again.
```
**Solution**: Start Docker Desktop and wait for it to be ready.

#### Port Already in Use
```
[ERROR] Port 8000 is already in use
```
**Solution**: Stop other services using port 8000 or change the port in `docker-compose.yml`.

#### Database Connection Failed
```
[ERROR] Database failed to become ready
```
**Solution**: Check if PostgreSQL container is running and healthy.

#### Permission Denied (Linux/macOS)
```
Permission denied: ./setup-docker.sh
```
**Solution**: Make the script executable:
```bash
chmod +x setup-docker.sh
```

#### PowerShell Execution Policy (Windows)
```
Execution of scripts is disabled on this system
```
**Solution**: Run with bypass:
```powershell
PowerShell -ExecutionPolicy Bypass -File .\setup-docker.ps1
```

### Manual Setup

If scripts fail, you can set up manually:

```bash
# 1. Create environment file
cp env.example env.docker

# 2. Start services
docker-compose up -d

# 3. Wait for services
sleep 10

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser

# 6. Load sample data
docker-compose exec web python manage.py loaddata main/fixtures/initial_data.json

# 7. Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## 📁 Project Structure

```
DTeam/
├── setup-docker.sh      # Bash script (Linux/macOS)
├── setup-docker.ps1     # PowerShell script (Windows)
├── setup-docker.bat     # Batch script (Windows)
├── setup-docker.py      # Python script (Cross-platform)
├── docker-compose.yml   # Docker services
├── Dockerfile          # Docker image
├── env.example         # Environment template
└── env.docker          # Docker environment (created by script)
```

## 🎯 Next Steps

After successful setup:

1. **🌐 Open the web application** at http://localhost:8000
2. **🔧 Access admin panel** at http://localhost:8000/admin
3. **📚 Explore the API** at http://localhost:8000/api/
4. **📊 Check audit logs** at http://localhost:8000/audit/
5. **🤖 Configure OpenAI** for translation features
6. **📧 Set up email** for PDF sending

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. View logs: `docker-compose logs -f`
3. Check service status: `docker-compose ps`
4. Restart services: `docker-compose restart`

---

**Happy coding! 🚀**
