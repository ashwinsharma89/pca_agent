"""
Logging configuration using Loguru.
"""
import sys
from pathlib import Path
from loguru import logger

from ..config.settings import settings


def setup_logger():
    """Configure loguru logger with file and console outputs."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.debug else "INFO",
        colorize=True
    )
    
    # File handler - general logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "pca_agent_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    # File handler - errors only
    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR"
    )
    
    logger.info("Logger initialized")


# Initialize logger on import
setup_logger()
