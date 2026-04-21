from typing import Any

from src.operations import process_bank_operations, process_bank_search


def test_process_bank_search_returns_matching_descriptions() -> None:
    data: list[dict[str, Any]] = [
        {"description": "Перевод организации", "id": 1},
        {"description": "Открытие вклада", "id": 2},
        {"description": "перевод между счетами", "id": 3},
    ]

    result = process_bank_search(data, "перевод")

    assert [item["id"] for item in result] == [1, 3]


def test_process_bank_search_escapes_regex_and_is_case_insensitive() -> None:
    data: list[dict[str, Any]] = [
        {"description": "Перевод. Срочный", "id": 1},
        {"description": "перевод без точки", "id": 2},
        {"description": "Оплата услуг", "id": 3},
    ]

    result = process_bank_search(data, "ПЕРЕВОД.")

    assert [item["id"] for item in result] == [1]


def test_process_bank_search_returns_source_data_for_empty_search() -> None:
    data: list[dict[str, Any]] = [{"description": "Открытие вклада", "id": 1}]

    result = process_bank_search(data, "")

    assert result == data


def test_process_bank_operations_counts_categories() -> None:
    data: list[dict[str, Any]] = [
        {"description": "Перевод организации"},
        {"description": "Открытие вклада"},
        {"description": "Перевод организации"},
    ]

    result = process_bank_operations(data, ["Перевод организации", "Открытие вклада", "Оплата"])

    assert result == {"Перевод организации": 2, "Открытие вклада": 1, "Оплата": 0}


def test_process_bank_operations_returns_zeroes_for_missing_categories() -> None:
    data: list[dict[str, Any]] = [{"description": "Перевод организации"}]

    result = process_bank_operations(data, ["Оплата", "Перевод организации"])

    assert result == {"Оплата": 0, "Перевод организации": 1}
