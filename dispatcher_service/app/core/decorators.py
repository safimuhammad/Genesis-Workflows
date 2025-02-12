# core/decorators.py
import functools
import logging
from core.logging_config import setup_custom_logger

def log_agent_execution(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Set up a logger for the agent using its class name
        base_logger = setup_custom_logger(self.__class__.__name__)
        # Create a LoggerAdapter to inject chain_id and the agent name as component.
        extra_context = {
            'chain_id': self.message.get('chain_id', 'N/A'),
            'component': self.__class__.__name__
        }
        logger = logging.LoggerAdapter(base_logger, extra_context)
        logger.info("Starting execution")
        try:
            result = func(self, *args, **kwargs)
            logger.info("Execution finished", extra=extra_context)
            logger.info(f"Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Execution encountered an error: {e}", extra=extra_context)
            raise
    return wrapper