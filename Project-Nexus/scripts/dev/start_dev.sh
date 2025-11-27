#!/bin/bash

# E-Commerce Backend Development Startup Script

set -e

echo "🚀 Starting E-Commerce Backend Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please update with your configuration."
fi

# Build and start services
echo "📦 Building and starting services..."
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until docker-compose -f docker-compose.dev.yml exec db pg_isready -U postgres; do
    sleep 2
done

# Run database migrations
echo "🗃️ Running database migrations..."
docker-compose -f docker-compose.dev.yml run --rm web python manage.py migrate

# Seed initial data
echo "🌱 Seeding initial data..."
docker-compose -f docker-compose.dev.yml run --rm web python manage.py seed_data

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.dev.yml run --rm web python manage.py collectstatic --noinput

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "📊 Services:"
echo "   - API Server: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/api/docs/"
echo "   - Admin Panel: http://localhost:8000/admin/"
echo "   - pgAdmin: http://localhost:5050"
echo "   - MailHog: http://localhost:8025"
echo ""
echo "🔧 Useful Commands:"
echo "   - make logs          # View logs"
echo "   - make shell         # Django shell"
echo "   - make test          # Run tests"
echo "   - make dev-down      # Stop services"
echo ""
