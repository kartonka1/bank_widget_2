import pytest
from src.utils.json_reader import read_json

def test_read_json_valid(tmp_path):
    file = tmp_path / "data.json"
    file.write_text('[{"amount": 100, "currency": "RUB"}]')
    result = read_json(str(file))
    assert isinstance(result, list)
    assert result[0]["amount"] == 100

def test_read_json_empty(tmp_path):
    file = tmp_path / "empty.json"
    file.write_text("")
    result = read_json(str(file))
    assert result == []

def test_read_json_not_list(tmp_path):
    file = tmp_path / "not_list.json"
    file.write_text('{"amount": 100}')
    result = read_json(str(file))
    assert result == []

def test_read_json_file_not_found():
    result = read_json("non_existing_file.json")
    assert result == []
