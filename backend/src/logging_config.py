import logging
import sys
from datetime import datetime
from typing import Optional

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up logging configuration for the application
    """
    # Create custom formatter
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            # Add timestamp with milliseconds
            timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # Format the log message
            if record.levelno == logging.INFO:
                log_format = f"{timestamp} | {record.levelname} | {record.name} | {record.getMessage()}"
            else:
                log_format = f"{timestamp} | {record.levelname} | {record.name} | {record.getMessage()}"

            # Create formatter with the format
            formatter = logging.Formatter(log_format)
            return formatter.format(record)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Create custom formatter
    formatter = CustomFormatter()
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Optionally add file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Suppress overly verbose logs from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return root_logger

# Initialize logger
logger = setup_logging()