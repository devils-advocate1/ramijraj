"""
Logger setup utility for SentimentGuard.
"""
import logging

def setup_logger(name="sentimentguard", level=logging.INFO):
    """Set up and return a logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger

if __name__ == "__main__":
    log = setup_logger()
    log.info("Logger initialized.")