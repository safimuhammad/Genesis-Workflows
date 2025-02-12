import logging
import os
import colorlog

# Directory and filename for custom logs
LOG_DIR = 'logs'
CUSTOM_LOG_FILENAME = 'custom_logs.log'

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

CUSTOM_LOG_FILEPATH = os.path.join(LOG_DIR, CUSTOM_LOG_FILENAME)

def get_file_handlers(filepath):
    """
    Create two file handlers:
      - One for DEBUG/INFO messages.
      - One for WARNING and above.
    Both handlers write to the same file but use different color schemes.
    """
    # Handler for DEBUG and INFO messages.
    file_handler_out = logging.FileHandler(filepath)
    file_handler_out.setLevel(logging.DEBUG)
    file_formatter_out = colorlog.ColoredFormatter(
        fmt='%(log_color)s[%(chain_id)s][%(component)s] [%(levelname)-8s]: %(message)s',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green'
        }
    )
    file_handler_out.setFormatter(file_formatter_out)

    # Handler for WARNING and above.
    file_handler_err = logging.FileHandler(filepath)
    file_handler_err.setLevel(logging.WARNING)
    file_formatter_err = colorlog.ColoredFormatter(
        fmt='%(log_color)s[%(chain_id)s][%(component)s] [%(levelname)-8s]: %(message)s',
        log_colors={
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red'
        }
    )
    file_handler_err.setFormatter(file_formatter_err)

    return file_handler_out, file_handler_err

def setup_custom_logger(name):
    """
    Set up a logger for non-Celery components that writes logs to a file.
    This logger uses two file handlers for different levels.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers to prevent duplicate logs
    logger.handlers = []

    # Get our two file handlers
    out_handler, err_handler = get_file_handlers(CUSTOM_LOG_FILEPATH)
    logger.addHandler(out_handler)
    logger.addHandler(err_handler)

    # For this scenario, we disable propagation so that Celery’s logger (or root logger)
    # does not also log them to the main console.
    logger.propagate = False
    return logger