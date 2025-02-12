#!/usr/bin/env bash
set -e

echo "Starting dispatcher in the background..."
python /app/celery_service/dispatcher_start.py &

echo "Starting Celery worker in the foreground..."
exec celery -A config.celery_config.celery_app worker --loglevel=info