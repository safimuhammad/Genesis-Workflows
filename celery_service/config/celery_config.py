# celery_service/celery_app/config.py
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

def make_celery():
    broker_url = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672//')
    backend_url = os.getenv('CELERY_RESULT_BACKEND', 'rpc://')

    celery = Celery(
        'celery_service',
        broker=broker_url,
        backend=backend_url,
    )

    celery.conf.update(
        result_expires=3600,
        imports=['app.tasks'],
        broker_connection_retry_on_startup=True,
        task_track_started=True,
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )

    return celery

celery_app = make_celery()