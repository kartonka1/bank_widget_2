"""Helpers for searching and counting transaction operations."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any


def process_bank_search(data: list[dict[str, Any]], search: str) -> list[dict[str, Any]]:
    """Return operations whose ``description`` contains the search string."""
    if not search:
        return data

    pattern = re.compile(re.escape(search), re.IGNORECASE)
    return [operation for operation in data if pattern.search(str(operation.get("description", "")))]


def process_bank_operations(data: list[dict[str, Any]], categories: list[str]) -> dict[str, int]:
    """Return operation counts for requested categories based on ``description``."""
    descriptions = [str(operation.get("description", "")) for operation in data]
    counts = Counter(descriptions)
    return {category: counts.get(category, 0) for category in categories}
