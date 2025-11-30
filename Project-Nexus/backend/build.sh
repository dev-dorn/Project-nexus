#!/usr/bin/env bash
# build.sh - Render deployment script

set -o errexit

echo "=== Starting Build Process ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files (from backend directory)
echo "Collecting static files..."
cd backend
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

echo "=== Build Complete ==="
