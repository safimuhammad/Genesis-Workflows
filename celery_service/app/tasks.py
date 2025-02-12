# celery_service/app/tasks.py
from config.celery_config import celery_app
from database.models import Chain
from database.deps import get_db_session

import json
import os
import logging
from dotenv import load_dotenv
from core.memory.message_system import RabbitMQMessageSystem

load_dotenv()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_chain_task(self, chain_id, chain, message):
    db = get_db_session()
    try:
        # push chain messages to RabbitMQ
        rabbitmq_url = os.getenv('CELERY_BROKER_URL')
        queue_name = os.getenv('RABBITMQ_QUEUE_NAME')
        
        message_system = RabbitMQMessageSystem('amqp://guest:guest@rabbitmq:5672/%2F', queue_name)
        for msg in chain:
            message_system.send(msg)
        
        new_chain = Chain(chain_id=chain_id, chain=chain, is_active=True)
        db.add(new_chain)
        db.commit()
        db.refresh(new_chain)
        return f"chain_id:{chain_id}, message:{message}"
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()