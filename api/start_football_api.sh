#!/bin/bash

# Football Results API Startup Script

echo "=== Football Results API Setup ==="

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check Redis connection
echo "Testing Redis connection..."
python3 -c "
import redis
import os
from dotenv import load_dotenv

load_dotenv()
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

try:
    r = redis.Redis.from_url(redis_url, decode_responses=True)
    r.ping()
    print('✓ Redis connection OK')
except Exception as e:
    print(f'✗ Redis connection failed: {e}')
    print('Please check your Redis server and REDIS_URL in .env')
    exit(1)
"

# Start the API
echo "Starting Football Results API..."
echo "API will be available at: http://localhost:8000"
echo "Documentation at: http://localhost:8000/docs"
echo "Health check at: http://localhost:8000/health"

uvicorn api:app --host 0.0.0.0 --port 8000 --reload --log-level info
