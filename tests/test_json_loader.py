import pytest
import json
from pathlib import Path
from src.utils.json_loader import load_operations

@pytest.fixture
def tmp_json_file(tmp_path: Path):
    """Создаёт временный JSON-файл с данными для теста."""
    file_path = tmp_path / "operations.json"
    data = [
        {"id": 1, "state": "EXECUTED", "amount": 100},
        {"id": 2, "state": "CANCELED", "amount": 50},
    ]
    file_path.write_text(json.dumps(data), encoding="utf-8")
    return file_path

def test_load_operations_success(tmp_json_file):
    result = load_operations(str(tmp_json_file))
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == 1

def test_load_operations_empty(tmp_path: Path):
    file_path = tmp_path / "empty.json"
    file_path.write_text("[]", encoding="utf-8")
    result = load_operations(str(file_path))
    assert result == []

def test_load_operations_invalid_json(tmp_path: Path):
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{ bad json }", encoding="utf-8")
    result = load_operations(str(file_path))
    assert result == []

def test_load_operations_file_not_found():
    result = load_operations("non_existent_file.json")
    assert result == []
