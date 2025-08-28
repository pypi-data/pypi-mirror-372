import logging

def setup_logging(name: str, level=logging.INFO) -> logging.Logger:
    """Configures and returns a logger instance for an application. 
    It ensures that logs from this specific logger do not interfere with other loggers.
    Formats the output to include the timestamp, logger name, log level, and the message itself."""
    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent logs from bubbling up to root

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger
