import logging
import os
from typing import Optional

def setup_logger(
    name: str,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Simple logger setup function.
    
    Args:
        name (str): Name of the logger
        log_file (Optional[str]): Path to log file (default: None)
        level (int): Logging level (default: logging.INFO)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler) 
    return logger
