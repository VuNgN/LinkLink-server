"""
Logging configuration and utilities
"""

import logging
import sys
from typing import Optional

from loguru import logger


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
) -> None:
    """
    Setup application logging

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        rotation: Log rotation size
        retention: Log retention period
    """

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>",
        colorize=True,
    )

    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} | {message}",
            rotation=rotation,
            retention=retention,
            compression="zip",
        )

    # Intercept standard logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # Replace standard logging handlers
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set specific loggers to use loguru
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True


def get_logger(name: str) -> logger:
    """
    Get a logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)
