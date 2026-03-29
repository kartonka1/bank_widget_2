from typing import Any, Dict, List


def filter_by_state(operations: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
    """
    Фильтрует список операций по заданному состоянию.

    :param operations: список словарей с данными операций
    :param state: значение для фильтрации по ключу 'state' (по умолчанию 'EXECUTED')
    :return: новый список, содержащий только операции с указанным state
    """
    return [op for op in operations if op.get("state") == state]


from typing import Dict, List


def sort_by_date(data: List[Dict], reverse: bool = True) -> List[Dict]:
    """
    Сортирует список словарей по ключу 'date'.

    :param data: список словарей с ключом 'date'
    :param reverse: порядок сортировки; True — убывание, False — возрастание
    :return: отсортированный список словарей
    """
    return sorted(data, key=lambda x: x["date"], reverse=reverse)
