import json
from typing import Any, List


def load_operations(path: str) -> List[dict[str, Any]]:
    """
    Загружает финансовые операции из JSON-файла.

    :param path: путь к JSON-файлу
    :return: список словарей с операциями или пустой список
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []
