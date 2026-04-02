"""Backward-compatible JSON loading helpers."""

from typing import Any

from src.utils.json_reader import read_json


def load_operations(path: str) -> list[dict[str, Any]]:
    """Load operations from a JSON file."""
    return read_json(path)
