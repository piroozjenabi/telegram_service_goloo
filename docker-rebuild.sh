#!/bin/bash

echo "🔄 Rebuilding and Restarting Docker Services"
echo "============================================="
echo ""

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Rebuild images
echo ""
echo "Rebuilding Docker images..."
docker-compose build --no-cache

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for services
echo ""
echo "Waiting for services to start..."
sleep 5

# Check status
echo ""
echo "Service Status:"
docker-compose ps

# Check logs
echo ""
echo "Recent logs:"
docker-compose logs --tail=20 web

echo ""
echo "✓ Rebuild complete!"
echo ""
echo "Check health: curl http://localhost:7004/api/health/"
echo "View logs: docker-compose logs -f web"
