"""Logging configuration for AnswerDeck application."""

import logging
import sys
from pathlib import Path
from src.config import get_config

config = get_config()


def setup_logger(name: str) -> logging.Logger:
    """Setup logger with both file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if config.LOG_FILE:
        file_path = Path(config.LOG_FILE)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Module-level logger
logger = setup_logger(__name__)
