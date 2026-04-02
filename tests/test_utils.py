from typing import Any
from unittest.mock import patch

from src.utils.json_reader import read_json


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
