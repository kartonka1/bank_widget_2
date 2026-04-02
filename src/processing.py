"""Helpers for filtering and sorting bank operations."""

from typing import Any


def filter_by_state(operations: list[dict[str, Any]], state: str = "EXECUTED") -> list[dict[str, Any]]:
    """Return only operations with the requested state."""
    return [operation for operation in operations if operation.get("state") == state]


def sort_by_date(data: list[dict[str, Any]], reverse: bool = True) -> list[dict[str, Any]]:
    """Return operations sorted by the ``date`` field."""
    return sorted(data, key=lambda item: item["date"], reverse=reverse)
