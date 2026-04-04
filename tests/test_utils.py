from typing import Any
from unittest.mock import patch

from src.utils.json_reader import logger, read_json


@patch("pathlib.Path.open")
def test_read_json_valid(mock_open_file: Any) -> None:
    mock_open_file.return_value.__enter__.return_value.read.return_value = '[{"amount": 100, "currency": "RUB"}]'
    result = read_json("data.json")
    assert result == [{"amount": 100, "currency": "RUB"}]


@patch("pathlib.Path.open")
def test_read_json_empty(mock_open_file: Any) -> None:
    mock_open_file.return_value.__enter__.return_value.read.return_value = ""
    result = read_json("empty.json")
    assert result == []


@patch("pathlib.Path.open")
def test_read_json_not_list(mock_open_file: Any) -> None:
    mock_open_file.return_value.__enter__.return_value.read.return_value = '{"amount": 100}'
    result = read_json("not_list.json")
    assert result == []


@patch("pathlib.Path.open", side_effect=FileNotFoundError)
def test_read_json_file_not_found(_: Any) -> None:
    result = read_json("non_existing_file.json")
    assert result == []


def test_utils_logger_configuration() -> None:
    assert logger.name == "src.utils"
    assert logger.level == 10
    assert logger.handlers


@patch("pathlib.Path.open")
def test_read_json_logs_success(mock_open_file: Any) -> None:
    mock_open_file.return_value.__enter__.return_value.read.return_value = '[{"amount": 100, "currency": "RUB"}]'

    with patch.object(logger, "debug") as mock_debug:
        result = read_json("data.json")

    assert result == [{"amount": 100, "currency": "RUB"}]
    mock_debug.assert_called_once()


def test_read_json_logs_error_for_missing_file() -> None:
    with patch.object(logger, "error") as mock_error:
        result = read_json("non_existing_file.json")

    assert result == []
    mock_error.assert_called_once()
