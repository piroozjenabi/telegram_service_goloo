# Docker Quick Reference

## Essential Commands

### Start & Stop
```bash
make up              # Start all services
make down            # Stop all services
make restart         # Restart services
docker-compose ps    # Check status
```

### Logs & Debugging
```bash
make logs            # All logs (follow mode)
make logs-web        # Web service logs only
make logs-db         # Database logs only
make shell           # Open bash in web container
```

### Testing
```bash
make test            # Run all tests
make health          # Check health endpoint
./docker-test.sh     # Full automated test
```

### Database
```bash
make migrate         # Run migrations
make createsuperuser # Create admin user
docker-compose exec web python manage.py dbshell  # Database shell
```

### Development
```bash
make dev-setup       # Build, start, and migrate
make build           # Rebuild images
make clean           # Remove all containers and volumes
```

## Health Check Endpoints

### Application Health
```bash
curl http://localhost:8000/api/health/
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "service": "telegram-bot-service"
}
```

### Container Health
```bash
docker-compose ps
# Look for "healthy" status
```

## Common Tasks

### View Running Containers
```bash
docker-compose ps
docker ps
```

### Execute Commands in Container
```bash
# Django management commands
docker-compose exec web python manage.py <command>

# Examples:
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py collectstatic
```

### Database Operations
```bash
# Backup
docker-compose exec db pg_dump -U postgres telegram_bots > backup.sql

# Restore
docker-compose exec -T db psql -U postgres telegram_bots < backup.sql

# Access PostgreSQL
docker-compose exec db psql -U postgres telegram_bots
```

### View Resource Usage
```bash
docker stats
docker-compose top
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs web

# Check if port is in use
lsof -i :8000

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues
```bash
# Check database health
docker-compose ps db

# View database logs
docker-compose logs db

# Test connection
docker-compose exec web python manage.py check --database default
```

### Health Check Failing
```bash
# Test endpoint manually
docker-compose exec web curl http://localhost:8000/api/health/

# Check migrations
docker-compose exec web python manage.py showmigrations

# Apply migrations
make migrate
```

### Container Keeps Restarting
```bash
# View recent logs
docker-compose logs --tail=100 web

# Check container status
docker-compose ps

# Inspect container
docker inspect telegram-bot-service
```

## File Locations

### Configuration Files
- `Dockerfile` - Docker image definition
- `docker-compose.yml` - Service orchestration
- `.dockerignore` - Build context exclusions
- `.env` - Environment variables
- `Makefile` - Command shortcuts

### Documentation
- `DOCKER_GUIDE.md` - Complete guide
- `DOCKER_SETUP_SUMMARY.md` - Setup overview
- `DOCKER_QUICK_REFERENCE.md` - This file

### Scripts
- `docker-test.sh` - Automated testing
- `.github/workflows/docker-test.yml` - CI/CD pipeline

## Environment Variables

### Required
```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/telegram_bots
DJANGO_SECRET_KEY=your-secret-key
BASE_URL=https://your-domain.com
```

### Optional
```bash
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=yourdomain.com
```

## Ports

- `8000` - Django application
- `5432` - PostgreSQL database

## Volumes

- `postgres_data` - Database persistence
- `static_volume` - Static files
- `media_volume` - Media uploads

## Profiles

### Default Profile
Runs web and database services:
```bash
docker-compose up
```

### Test Profile
Runs tests in isolated environment:
```bash
docker-compose --profile test run --rm test
```

## Tips

1. **Use Makefile**: Shortcuts for common commands
2. **Check Health**: Always verify health after starting
3. **View Logs**: Use `-f` flag to follow logs in real-time
4. **Clean Regularly**: Remove unused containers and volumes
5. **Backup Data**: Regular database backups before updates

## Quick Workflow

```bash
# 1. Initial setup
cp .env.example .env
# Edit .env with your settings

# 2. Start services
make up

# 3. Setup database
make migrate
make createsuperuser

# 4. Verify
make health
make ps

# 5. View logs
make logs

# 6. Access application
# http://localhost:8000/admin
```

## Getting Help

```bash
make help           # Show available commands
docker-compose --help
docker --help
```
