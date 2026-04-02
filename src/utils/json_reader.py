"""Helpers for reading transaction data from JSON files."""

import json
from pathlib import Path
from typing import Any


def read_json(file_path: str) -> list[dict[str, Any]]:
    """Return a list of transactions from a JSON file or an empty list on failure."""
    path = Path(file_path)

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]
