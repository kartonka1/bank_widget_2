"""Helpers for reading transaction data from JSON files."""

import json
from pathlib import Path
from typing import Any

from src.logger_config import get_file_logger

logger = get_file_logger("src.utils", "utils.log")


def read_json(file_path: str) -> list[dict[str, Any]]:
    """Return a list of transactions from a JSON file or an empty list on failure."""
    path = Path(file_path)

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.error("JSON file not found: %s", path)
        return []
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in file: %s", path)
        return []
    except OSError as error:
        logger.error("Failed to read JSON file %s: %s", path, error)
        return []

    if not isinstance(data, list):
        logger.error("JSON root element is not a list in file: %s", path)
        return []

    transactions = [item for item in data if isinstance(item, dict)]
    logger.debug("Loaded %s transaction records from %s", len(transactions), path)
    return transactions
