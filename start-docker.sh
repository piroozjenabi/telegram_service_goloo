#!/bin/bash

echo "🚀 Starting Telegram Bot Service with Docker (SQLite)"
echo "======================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  Please edit .env and set your configuration:"
    echo "   - DJANGO_SECRET_KEY"
    echo "   - BASE_URL"
    echo ""
fi

# Start services
echo "Starting Docker services..."
docker-compose up -d

# Wait a moment
sleep 3

# Check status
echo ""
echo "Service Status:"
docker-compose ps

echo ""
echo "✓ Services started!"
echo ""
echo "Access your application:"
echo "  - Web: http://localhost:7004"
echo "  - Admin: http://localhost:7004/admin"
echo "  - API: http://localhost:7004/api"
echo "  - Health: http://localhost:7004/api/health/"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop: docker-compose down"
echo "  - Migrate: docker-compose exec web python manage.py migrate"
echo "  - Create superuser: docker-compose exec web python manage.py createsuperuser"
echo ""
