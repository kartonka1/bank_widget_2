import json

from src.services import (
    cashback_categories,
    investment_bank,
    search_by_phone_numbers,
    search_personal_transfers,
    simple_search,
)


def test_cashback_categories_returns_top_three() -> None:
    data = [
        {"Дата операции": "2024-01-10", "Сумма операции": 10000, "Категория": "Еда"},
        {"Дата операции": "2024-01-11", "Сумма операции": 9000, "Категория": "Такси"},
        {"Дата операции": "2024-01-12", "Сумма операции": 8000, "Категория": "АЗС"},
        {"Дата операции": "2024-01-13", "Сумма операции": 1000, "Категория": "Книги"},
    ]
    payload = json.loads(cashback_categories(data, 2024, 1))
    assert list(payload.keys()) == ["Еда", "Такси", "АЗС"]


def test_investment_bank_rounds_to_limit() -> None:
    transactions = [
        {"Дата операции": "2024-01-10", "Сумма операции": 1712},
        {"Дата операции": "2024-01-11", "Сумма операции": 99},
    ]
    assert investment_bank("2024-01", transactions, 50) == 39.0


def test_simple_search_case_insensitive() -> None:
    data = [
        {"Дата операции": "2024-01-10", "Категория": "Переводы", "Описание": "Валерий А.", "Сумма операции": 100},
        {"Дата операции": "2024-01-11", "Категория": "Еда", "Описание": "Магазин", "Сумма операции": 200},
    ]
    payload = json.loads(simple_search(data, "валерий"))
    assert len(payload) == 1


def test_search_by_phone_numbers_supports_multiple_formats() -> None:
    data = [
        {"Дата операции": "2024-01-10", "Категория": "Связь", "Описание": "МТС +7 (900) 000-00-00", "Сумма операции": 100},
        {"Дата операции": "2024-01-11", "Категория": "Связь", "Описание": "Т-Банк 89000000000", "Сумма операции": 100},
    ]
    payload = json.loads(search_by_phone_numbers(data))
    assert len(payload) == 2


def test_search_personal_transfers() -> None:
    data = [
        {"Дата операции": "2024-01-10", "Категория": "Переводы", "Описание": "Валерий А.", "Сумма операции": 100},
        {"Дата операции": "2024-01-11", "Категория": "Переводы", "Описание": "Платеж в банк", "Сумма операции": 200},
    ]
    payload = json.loads(search_personal_transfers(data))
    assert len(payload) == 1
