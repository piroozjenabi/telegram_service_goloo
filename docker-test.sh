#!/bin/bash

# Docker Health Check Test Script
# This script tests the Docker setup and health checks

set -e

echo "🐳 Docker Setup Test Script"
echo "============================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "1. Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Check if docker-compose is available
echo "2. Checking Docker Compose..."
if ! docker-compose version > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is available${NC}"
echo ""

# Build images
echo "3. Building Docker images..."
docker-compose build
echo -e "${GREEN}✓ Images built successfully${NC}"
echo ""

# Start services
echo "4. Starting services..."
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Wait for services to be healthy
echo "5. Waiting for services to be healthy (max 60s)..."
TIMEOUT=60
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if docker-compose ps | grep -q "healthy"; then
        echo -e "${GREEN}✓ Services are healthy${NC}"
        break
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    echo -n "."
done
echo ""

if [ $ELAPSED -ge $TIMEOUT ]; then
    echo -e "${YELLOW}⚠ Timeout waiting for health checks${NC}"
fi

# Check service status
echo "6. Checking service status..."
docker-compose ps
echo ""

# Test health endpoint
echo "7. Testing health endpoint..."
sleep 5  # Give the service a moment to fully start
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health/ || echo "failed")

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Response: $HEALTH_RESPONSE"
    echo ""
    echo "Checking logs..."
    docker-compose logs --tail=50 web
fi
echo ""

# Run tests
echo "8. Running Django tests..."
if docker-compose --profile test run --rm test; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${RED}❌ Tests failed${NC}"
fi
echo ""

# Show logs
echo "9. Recent logs from web service:"
docker-compose logs --tail=20 web
echo ""

# Summary
echo "============================"
echo "🎉 Docker setup test complete!"
echo ""
echo "Services running:"
echo "  - Web: http://localhost:8000"
echo "  - Admin: http://localhost:8000/admin"
echo "  - API: http://localhost:8000/api"
echo "  - Health: http://localhost:8000/api/health/"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart: docker-compose restart"
echo ""
