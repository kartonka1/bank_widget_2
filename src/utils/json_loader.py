"""Backward-compatible JSON loading helpers."""

from typing import Any

from src.logger_config import get_file_logger
from src.utils.json_reader import read_json

logger = get_file_logger("src.utils", "utils.log")


def load_operations(path: str) -> list[dict[str, Any]]:
    """Load operations from a JSON file."""
    operations = read_json(path)
    logger.debug("load_operations returned %s records for %s", len(operations), path)
    return operations
