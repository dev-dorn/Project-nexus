#!/bin/bash

# E-Commerce Backend Development Shutdown Script

echo "🛑 Stopping E-Commerce Backend Development Environment..."

docker-compose -f docker-compose.dev.yml down

echo "✅ Development environment stopped."
