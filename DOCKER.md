# Docker Setup for CVProject

This document provides instructions for running the CVProject using Docker and Docker Compose.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+

## Quick Start

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd DTeam
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Load sample data:**
   ```bash
   docker-compose exec web python manage.py load_sample_data --clear
   ```

5. **Access the application:**
   - Web application: http://localhost
   - Direct Django server: http://localhost:8000
   - API endpoints: http://localhost:8000/api/

## Services

The Docker setup includes the following services:

### Web Application (Django)
- **Container:** `cvproject_web`
- **Port:** 8000
- **Image:** Built from local Dockerfile
- **Features:** Django app with Gunicorn WSGI server

### Database (PostgreSQL)
- **Container:** `cvproject_db`
- **Port:** 5432
- **Image:** postgres:15-alpine
- **Database:** cvproject
- **User:** cvproject_user
- **Password:** cvproject_password

### Cache (Redis)
- **Container:** `cvproject_redis`
- **Port:** 6379
- **Image:** redis:7-alpine
- **Purpose:** Session storage and caching

### Reverse Proxy (Nginx)
- **Container:** `cvproject_nginx`
- **Ports:** 80, 443
- **Image:** nginx:alpine
- **Features:** Static file serving, reverse proxy, security headers

## Management Commands

### Using Makefile (Recommended)

```bash
# Build Docker images
make build

# Start all services
make up

# Stop all services
make down

# Restart all services
make restart

# View logs
make logs

# Open shell in web container
make shell

# Run Django migrations
make migrate

# Load sample data
make loaddata

# Create superuser
make createsuperuser

# Run tests
make test

# Clean up Docker resources
make clean

# Check service health
make health
```

### Using Docker Compose Directly

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Execute commands in containers
docker-compose exec web python manage.py <command>
docker-compose exec db psql -U cvproject_user -d cvproject
docker-compose exec redis redis-cli
```

## Development vs Production

### Development Mode
```bash
# Use development configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Production Mode
```bash
# Use production configuration (when available)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Environment Configuration

### Environment Variables

The following environment variables can be configured:

- `DJANGO_ENV`: Environment (development/production)
- `DEBUG`: Django debug mode
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Environment Files

- `env.docker`: Docker-specific environment variables
- `.env`: Local development environment variables

## Database Management

### Backup Database
```bash
make db-backup
# or
docker-compose exec db pg_dump -U cvproject_user cvproject > backup.sql
```

### Restore Database
```bash
make db-restore FILE=backup.sql
# or
docker-compose exec -T db psql -U cvproject_user -d cvproject < backup.sql
```

### Access Database Shell
```bash
make db-shell
# or
docker-compose exec db psql -U cvproject_user -d cvproject
```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Ensure ports 80, 8000, 5432, and 6379 are not in use
   - Modify ports in docker-compose.yml if needed

2. **Permission issues:**
   - On Linux/Mac, ensure Docker has proper permissions
   - Run `sudo docker-compose` if needed

3. **Database connection issues:**
   - Wait for database to be ready: `docker-compose logs db`
   - Check database health: `docker-compose exec db pg_isready`

4. **Static files not loading:**
   - Ensure static files are collected: `make collectstatic`
   - Check Nginx configuration

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs web
docker-compose logs db
docker-compose logs redis
docker-compose logs nginx

# Test web application
curl http://localhost:8000/
curl http://localhost/

# Test API
curl http://localhost:8000/api/
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Complete cleanup
make clean
```

## Security Considerations

- Change default passwords in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Regularly update base images
- Use secrets management for production

## Performance Optimization

- Use multi-stage builds for smaller images
- Enable Docker layer caching
- Use .dockerignore to exclude unnecessary files
- Configure resource limits in production
- Use health checks for better reliability

## Monitoring

- Use `docker-compose ps` to check service status
- Monitor logs with `docker-compose logs -f`
- Use health check endpoints
- Monitor resource usage with `docker stats`
