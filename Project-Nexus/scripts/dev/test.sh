#!/bin/bash

# Test Runner Script

set -e

echo "🧪 Running Tests..."

# Run tests with coverage
docker-compose -f docker-compose.test.yml run --rm web pytest "$@"

echo "✅ Tests completed!"
