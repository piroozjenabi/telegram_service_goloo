# Docker Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Read-Only Error

**Error:**
```
OperationalError: attempt to write a readonly database
```

**Cause:** SQLite database file has incorrect permissions when mounted from host.

**Solution:**

The Dockerfile now runs as root to handle volume-mounted files properly. Rebuild:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Alternative:** Delete the database and let Docker recreate it:

```bash
docker-compose down
rm db.sqlite3
docker-compose up -d
```

### 2. Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use
```

**Solution:**

Change the port mapping in `docker-compose.yml` or stop the conflicting service:

```bash
# Find what's using the port
lsof -i :5432

# Stop the service or change docker-compose.yml port mapping
```

### 3. Permission Denied: /app/bot.log

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/app/bot.log'
```

**Solution:**

This is already fixed - logging now only goes to console. If you still see this:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 4. CSRF Verification Failed

**Error:**
```
Forbidden (403)
CSRF verification failed. Request aborted.
Origin checking failed - https://your-domain.com does not match any trusted origins.
```

**Solution:**

Add your domain to `.env`:

```bash
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://other-domain.com
```

Then restart:

```bash
docker-compose restart
```

See [CSRF_CONFIGURATION.md](CSRF_CONFIGURATION.md) for details.

### 5. Container Keeps Restarting

**Check logs:**
```bash
docker-compose logs -f web
```

**Common causes:**
- Database migration errors
- Missing environment variables
- Port conflicts
- Syntax errors in code

**Solution:**
```bash
# Check container status
docker-compose ps

# View full logs
docker-compose logs web

# Restart with fresh build
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 6. Health Check Failing

**Check health status:**
```bash
docker-compose ps
curl http://localhost:7004/api/health/
```

**Solution:**

```bash
# Check if migrations are applied
docker-compose exec web python manage.py showmigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Check database connection
docker-compose exec web python manage.py check --database default
```

### 7. Static Files Not Loading

**Solution:**

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Or rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 8. Environment Variables Not Loading

**Check if .env exists:**
```bash
ls -la .env
```

**Verify variables are loaded:**
```bash
docker-compose exec web python manage.py shell
>>> import os
>>> print(os.getenv('DJANGO_SECRET_KEY'))
>>> print(os.getenv('BASE_URL'))
```

**Solution:**

```bash
# Ensure .env file exists
cp .env.example .env

# Edit .env with your values
nano .env

# Restart to load new values
docker-compose restart
```

### 9. Database Migrations Not Applied

**Error:**
```
django.db.utils.OperationalError: no such table: ...
```

**Solution:**

```bash
# Apply migrations
docker-compose exec web python manage.py migrate

# Or restart (migrations run on startup)
docker-compose restart
```

### 10. Can't Create Superuser

**Solution:**

```bash
# Interactive mode
docker-compose exec web python manage.py createsuperuser

# Or use make command
make createsuperuser
```

## Debugging Commands

### View Logs
```bash
# All logs
docker-compose logs -f

# Web service only
docker-compose logs -f web

# Last 50 lines
docker-compose logs --tail=50 web
```

### Access Container Shell
```bash
# Bash shell
docker-compose exec web bash

# Python shell
docker-compose exec web python manage.py shell

# Database shell
docker-compose exec web python manage.py dbshell
```

### Check Container Status
```bash
# List containers
docker-compose ps

# Detailed info
docker inspect telegram-bot-service

# Resource usage
docker stats telegram-bot-service
```

### Database Operations
```bash
# Show migrations
docker-compose exec web python manage.py showmigrations

# Make migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Database shell
docker-compose exec web python manage.py dbshell
```

### Test Configuration
```bash
# Check Django configuration
docker-compose exec web python manage.py check

# Check database
docker-compose exec web python manage.py check --database default

# Test health endpoint
curl http://localhost:7004/api/health/
```

## Clean Slate Rebuild

If nothing else works, start fresh:

```bash
# Stop and remove everything
docker-compose down -v

# Remove database
rm db.sqlite3

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

# Rebuild from scratch
docker-compose build --no-cache

# Start services
docker-compose up -d

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Check status
docker-compose ps
curl http://localhost:7004/api/health/
```

## Performance Issues

### Slow Build Times

**Solution:**

```bash
# Use build cache
docker-compose build

# Only rebuild if needed
docker-compose up -d --build
```

### High Memory Usage

**Check usage:**
```bash
docker stats
```

**Solution:**

Add resource limits to `docker-compose.yml`:

```yaml
services:
  web:
    # ... other config
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

## Getting Help

### Collect Debug Information

```bash
# System info
docker version
docker-compose version

# Container status
docker-compose ps

# Recent logs
docker-compose logs --tail=100 web

# Environment check
docker-compose exec web env | grep DJANGO

# Django check
docker-compose exec web python manage.py check --deploy
```

### Report Issues

When reporting issues, include:

1. Error message from logs
2. Docker version
3. Output of `docker-compose ps`
4. Relevant configuration (`.env`, `docker-compose.yml`)
5. Steps to reproduce

## Prevention Tips

1. **Always use .env for configuration** - Don't hardcode values
2. **Check logs regularly** - `docker-compos