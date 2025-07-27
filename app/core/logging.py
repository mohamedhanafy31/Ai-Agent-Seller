"""
Centralized logging configuration for AI Agent Seller Backend.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from .config import get_settings

settings = get_settings()


class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to Loguru."""
    
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def format_record(record: Dict[str, Any]) -> str:
    """Custom formatter for log records."""
    format_string = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = (
            record["extra"]["payload"] 
            if isinstance(record["extra"]["payload"], str)
            else str(record["extra"]["payload"])
        )
        format_string += "\n<level>Payload:</level> <level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


def setup_logging() -> None:
    """Setup application logging configuration."""
    
    # Remove default handler and add custom one
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        format=format_record,
        level=settings.LOG_LEVEL,
        colorize=True,
        serialize=False,
    )
    
    # File handler
    log_path = Path(settings.LOG_FILE)
    logger.add(
        log_path,
        format=format_record,
        level=settings.LOG_LEVEL,
        rotation="100 MB",
        retention="1 week",
        compression="zip",
        serialize=False,
    )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Set specific loggers
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]


def get_logger(name: str) -> Any:
    """Get a logger instance."""
    return logger.bind(name=name) 