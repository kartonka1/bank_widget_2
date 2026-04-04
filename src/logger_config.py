"""Helpers for configuring module-specific file loggers."""

from __future__ import annotations

import logging
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def get_file_logger(logger_name: str, log_file_name: str) -> logging.Logger:
    """Return a configured logger writing to a project log file."""
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    LOGS_DIR.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(LOGS_DIR / log_file_name, mode="w", encoding="utf-8")
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger
