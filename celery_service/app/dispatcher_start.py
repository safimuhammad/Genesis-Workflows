# celery_service/app/dispatcher_start.py

import os
from dotenv import load_dotenv
load_dotenv()

from core.memory.message_system import RabbitMQMessageSystem
from core.memory.message_dispatcher import MessageDispatcher
from core.memory.datastore import Datastore
from core.agent import WriteAgent, ReadAgent, ContentWriter

# 1) Import the custom logging setup
from core.logging_config import setup_custom_logger  # Adjust path if needed
import logging

def main():
    # 2) Initialize the base logger
    base_logger = setup_custom_logger("DispatcherStart")
    # 3) Wrap it in a LoggerAdapter with default extra fields
    logger = logging.LoggerAdapter(
        base_logger,
        extra={'chain_id': 'N/A', 'component': 'DispatcherStart'}
    )

    # 4) Log something so we know we're in main()
    logger.info("Starting dispatcher_start.py script...")

    # rabbitmq_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
    queue_name = os.getenv("RABBITMQ_QUEUE_NAME", "message_dispatcher_queue")
    rabbitmq_url = "amqp://guest:guest@rabbitmq:5672/%2F"
    
    data_store = Datastore()
    message_system = RabbitMQMessageSystem(rabbitmq_url, queue_name)
    agent_registry = {
        "read_file": ReadAgent,
        "write_file": WriteAgent,
        "content_writer": ContentWriter,
    }

    dispatcher = MessageDispatcher(message_system, agent_registry, data_store)
    dispatcher.start()

    logger.info("Dispatcher is now running... (press CTRL+C to exit)")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Stopping dispatcher...")
        dispatcher.stop()
        logger.info("Dispatcher stopped gracefully.")

if __name__ == "__main__":
    main()