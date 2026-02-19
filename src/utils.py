import time
import random
import logging
import os
from datetime import datetime

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name, log_file=None):
    if log_file is None:
        log_file = f"{name}.log"
    
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler = logging.FileHandler(os.path.join(LOG_DIR, log_file))
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger('common_utils')

def random_sleep(min_seconds=30, max_seconds=90, reason="Wait"):
    """Sleep for a random amount of time to simulate human behavior"""
    sleep_time = random.uniform(min_seconds, max_seconds)
    logger.info(f"{reason}: Sleeping for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)

def human_typing_delay(text_length):
    """Simulate typing delay based on text length"""
    # Average typing speed approx 200-300 ms per char
    delay = text_length * random.uniform(0.1, 0.3)
    time.sleep(min(delay, 5.0)) # Cap at 5 seconds for safety

def get_time_based_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"
