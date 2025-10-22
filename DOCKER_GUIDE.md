# Docker Deployment Guide

This guide covers running the Telegram Bot Service using Docker and Docker Compose.

## Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:
- `DJANGO_SECRET_KEY`: Generate a secure secret key
- `BASE_URL`: Your public HTTPS URL for webhooks
- `DATABASE_URL`: Uncomment for PostgreSQL (already configured for Docker)

### 2. Build and Run

Start all services:

```bash
docker-compose up -d
```

This will start:
- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)

### 3. Check Service Health

```bash
# Check container status
docker-compose ps

# Check health endpoint
curl http://localhost:8000/api/health/

# View logs
docker-compose logs -f web
```

## Running Tests

Run the test suite using the test profile:

```bash
docker-compose --profile test run --rm test
```

Or run specific tests:

```bash
docker-compose --profile test run --rm test sh -c "python manage.py test Bot.tests.TestBotCreation"
```

## Common Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Run Django Management Commands
```bash
# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Database Operations
```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d telegram_bots

# Backup database
docker-compose exec db pg_dump -U postgres telegram_bots > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres telegram_bots < backup.sql
```

## Health Checks

The application includes health checks for monitoring:

### Application Health
- **Endpoint**: `http://localhost:8000/api/health/`
- **Checks**: Database connectivity, service status
- **Interval**: Every 30 seconds
- **Timeout**: 10 seconds

### Database Health
- **Check**: PostgreSQL ready check
- **Interval**: Every 10 seconds
- **Timeout**: 5 seconds

## Production Deployment

### 1. Update Environment Variables

```bash
# .env
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<strong-random-key>
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
BASE_URL=https://yourdomain.com
DATABASE_URL=postgresql://postgres:secure_password@db:5432/telegram_bots
```

### 2. Use Production-Ready Server

Update `docker-compose.yml` command for the web service:

```yaml
command: >
  sh -c "python manage.py migrate &&
         gunicorn MAIN.wsgi:application --bind 0.0.0.0:8000 --workers 4"
```

Add gunicorn to `pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies
    "gunicorn>=21.2.0",
]
```

### 3. Add Nginx Reverse Proxy

Create `nginx.conf` and add nginx service to `docker-compose.yml` for SSL termination and static file serving.

### 4. Enable SSL/TLS

Use Let's Encrypt with certbot or configure your cloud provider's SSL certificates.

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs web

# Check if port is already in use
lsof -i :8000
```

### Database Connection Issues
```bash
# Verify database is healthy
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection manually
docker-compose exec web python manage.py dbshell
```

### Health Check Failing
```bash
# Check health endpoint directly
docker-compose exec web curl http://localhost:8000/api/health/

# Verify migrations are applied
docker-compose exec web python manage.py showmigrations
```

## Volume Management

### Persistent Data
- `postgres_data`: Database files
- `static_volume`: Static files (CSS, JS, images)
- `media_volume`: User-uploaded media

### Backup Volumes
```bash
# Backup
docker run --rm -v telegram-bot-service_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore
docker run --rm -v telegram-bot-service_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## Development Workflow

### Local Development with Docker

1. Mount your code as a volume (already configured)
2. Make changes to your code
3. Changes are reflected immediately (Django auto-reload)

### Running Shell Inside Container
```bash
docker-compose exec web bash
```

### Debugging
```bash
# Python shell
docker-compose exec web python manage.py shell

# Database shell
docker-compose exec web python manage.py dbshell
```

## Monitoring

### Resource Usage
```bash
docker stats
```

### Container Inspection
```bash
docker-compose exec web ps aux
docker-compose exec web df -h
```

## Cleanup

### Remove All Containers and Volumes
```bash
docker-compose down -v
```

### Remove Images
```bash
docker-compose down --rmi all
```

### Clean System
```bash
docker system prune -a --volumes
```
