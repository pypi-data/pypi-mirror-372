#!/bin/bash

# Nosto Email Widgets MCP Server - Docker Startup Script

set -e

echo "🐳 Starting Nosto Email Widgets MCP Server with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping containers..."
    docker-compose down
    echo "✅ Containers stopped"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Build and start the containers
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting MCP server..."
docker-compose up -d

echo "⏳ Waiting for server to be ready..."
sleep 10

# Check if server is running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Server is running successfully!"
    echo "🌐 MCP endpoint: http://localhost:8000/mcp"
    echo "❤️  Health check: http://localhost:8000/health"
    echo ""
    echo "📊 Container status:"
    docker-compose ps
    echo ""
    echo "📝 Logs (Ctrl+C to stop):"
    docker-compose logs -f
else
    echo "❌ Server failed to start. Check logs with: docker-compose logs"
    exit 1
fi
