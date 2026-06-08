import logging
import sys
from pathlib import Path

from app.core.config import settings

LOG_DIR = Path("logs")

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
FILE_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Console handler (always on — captured by Docker/CloudWatch in production)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(console_handler)

    # File handler (opt-in via LOG_TO_FILE=True) — disabled in containers by default
    if settings.LOG_TO_FILE:
        LOG_DIR.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(FILE_LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(file_handler)

    logger.propagate = False

    return logger
