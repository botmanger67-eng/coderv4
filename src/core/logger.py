import sys
from pathlib import Path
from loguru import logger
from src.core.config import settings


def setup_logger() -> None:
    """Configure Loguru logger with console and file handlers."""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL.upper(),
        colorize=True,
    )

    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_dir / "bot_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="gz",
        enqueue=True,
    )

    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="gz",
        enqueue=True,
    )


def get_logger(name: str | None = None) -> logger:
    """Get a configured logger instance.

    Args:
        name: Optional logger name for identification.

    Returns:
        Configured Loguru logger instance.
    """
    if name:
        return logger.bind(name=name)
    return logger