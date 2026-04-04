from typing import Any
from unittest.mock import patch

from src.utils.json_loader import load_operations, logger


@patch("pathlib.Path.open")
def test_load_operations_success(mock_open_file: Any) -> None:
    mock_open_file.return_value.__enter__.return_value.read.return_value = '[{"id": 1}, {"id": 2}]'
    result = load_operations("data/operations.json")
    assert result == [{"id": 1}, {"id": 2}]


@patch("pathlib.Path.open")
def test_load_operations_empty_file(mock_open_file: Any) -> None:
    mock_open_file.return_value.__enter__.return_value.read.return_value = ""
    result = load_operations("data/operations.json")
    assert result == []


@patch("pathlib.Path.open")
def test_load_operations_returns_empty_for_non_list(mock_open_file: Any) -> None:
    mock_open_file.return_value.__enter__.return_value.read.return_value = '{"id": 1}'
    result = load_operations("data/operations.json")
    assert result == []


@patch("pathlib.Path.open", side_effect=FileNotFoundError)
def test_load_operations_returns_empty_when_file_is_missing(_: Any) -> None:
    result = load_operations("missing.json")
    assert result == []


@patch("pathlib.Path.open")
def test_load_operations_returns_empty_for_invalid_json(mock_open_file: Any) -> None:
    mock_open_file.return_value.__enter__.return_value.read.return_value = "{ bad json }"
    result = load_operations("data/operations.json")
    assert result == []


def test_load_operations_logs_result() -> None:
    with patch("src.utils.json_loader.read_json", return_value=[{"id": 1}]):
        with patch.object(logger, "debug") as mock_debug:
            result = load_operations("data/operations.json")

    assert result == [{"id": 1}]
    mock_debug.assert_called_once()
