import json
from pathlib import Path
from typing import Dict, List


def read_json(file_path: str) -> List[Dict]:
    path = Path(file_path)
    if not path.exists():
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return data
