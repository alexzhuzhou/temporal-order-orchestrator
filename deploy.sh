#!/bin/bash

# Quick deployment script for DigitalOcean
# Run this on your droplet after cloning the repository

set -e

echo "========================================"
echo "Order Orchestrator - Quick Deploy"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.production .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and set a secure DB_PASSWORD"
    echo "   Run: nano .env"
    echo "   Then run this script again"
    exit 1
fi

echo "✓ Environment file found"

# Build and start services
echo ""
echo "Building Docker images (this may take 5-10 minutes)..."
docker compose -f docker-compose.production.yml build

echo ""
echo "Starting all services..."
docker compose -f docker-compose.production.yml up -d

echo ""
echo "Waiting for services to be healthy (30 seconds)..."
sleep 30

# Setup search attributes
echo ""
echo "Registering Temporal search attributes..."
docker exec temporal tctl admin cluster add-search-attributes --name CustomerId --type Keyword 2>/dev/null || echo "  CustomerId already exists"
docker exec temporal tctl admin cluster add-search-attributes --name CustomerName --type Text 2>/dev/null || echo "  CustomerName already exists"
docker exec temporal tctl admin cluster add-search-attributes --name OrderTotal --type Double 2>/dev/null || echo "  OrderTotal already exists"
docker exec temporal tctl admin cluster add-search-attributes --name Priority --type Keyword 2>/dev/null || echo "  Priority already exists"

echo ""
echo "========================================"
echo "✓ Deployment Complete!"
echo "========================================"
echo ""
echo "Your application is now running:"
echo ""
echo "  Frontend:    http://$(curl -s ifconfig.me)"
echo "  API Docs:    http://$(curl -s ifconfig.me):8000/docs"
echo "  Temporal UI: http://$(curl -s ifconfig.me):8080"
echo ""
echo "Check status: docker compose -f docker-compose.production.yml ps"
echo "View logs:    docker compose -f docker-compose.production.yml logs -f"
echo ""
