import logging
import sys
from pathlib import Path

def setup_logging(log_file: str = "app.log"):
    """
    Set up logging configuration.
    Logs will be written to both console and a log file.
    """
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(log_file)

    # Set level for handlers
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()
# Create a helper config in shared/ to initialize Python's logging library. Stop using arbitrary print() statements inside agents; use proper logger.info(), logger.warning(), and logger.error() levels.