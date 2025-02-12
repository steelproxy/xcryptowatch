import logging
import os
from datetime import datetime
import sys

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

def setup_logger(name, log_file, level=logging.DEBUG):
    """Set up a new logger with consistent formatting"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(f'logs/{log_file}', delay=False, encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = []  # Clear existing handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)  # Add console handler
    logger.propagate = False
    
    return logger

# Main application logger
main_logger = setup_logger('xcryptowatch', 'xcryptowatch.log')
twitter_logger = setup_logger('xcryptowatch_twitter', 'twitter.log')
truth_logger = setup_logger('xcryptowatch_truth', 'truth.log')
gpt_logger = setup_logger('xcryptowatch_gpt', 'gpt.log')
postal_logger = setup_logger('xcryptowatch_postal', "postal.log")