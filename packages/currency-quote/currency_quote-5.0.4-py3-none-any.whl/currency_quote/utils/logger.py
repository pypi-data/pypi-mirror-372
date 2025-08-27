import logging

# Configure the root logger
def setup_logging(level=logging.INFO):
    """
    Setup logging configuration for the currency_quote package.

    Args:
        level: The logging level. Default is INFO.
    """
    logger = logging.getLogger("currency_quote")
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# Get a named logger
def get_logger(name):
    """
    Get a logger with the specified name.

    Args:
        name: The name of the logger.

    Returns:
        A logger instance.
    """
    return logging.getLogger(f"currency_quote.{name}")

