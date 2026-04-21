from typing import Any

import main as app_main


def _operation(description: str, status: str, currency_code: str = "RUB") -> dict[str, Any]:
    return {
        "id": 1,
        "state": status,
        "date": "2024-01-01T10:00:00.000000",
        "description": description,
        "operationAmount": {"amount": "100.00", "currency": {"code": currency_code}},
        "from": "Visa Platinum 7000792289606361",
        "to": "Счет 73654108430135874305",
    }


def test_main_happy_path(monkeypatch: Any, capsys: Any) -> None:
    operations = [_operation("Перевод организации", "EXECUTED"), _operation("Открытие вклада", "CANCELED")]
    monkeypatch.setattr(app_main, "_load_transactions", lambda _: operations)

    user_inputs = iter(["1", "executed", "нет", "нет", "нет"])
    monkeypatch.setattr("builtins.input", lambda: next(user_inputs))

    app_main.main()
    out = capsys.readouterr().out

    assert "Для обработки выбран JSON-файл." in out
    assert 'Операции отфильтрованы по статусу "EXECUTED"' in out
    assert "Всего банковских операций в выборке: 1" in out
    assert "Перевод организации" in out


def test_main_invalid_status_and_empty_result(monkeypatch: Any, capsys: Any) -> None:
    operations = [_operation("Открытие вклада", "EXECUTED", currency_code="USD")]
    monkeypatch.setattr(app_main, "_load_transactions", lambda _: operations)

    user_inputs = iter(["1", "test", "executed", "нет", "да", "да", "перевод"])
    monkeypatch.setattr("builtins.input", lambda: next(user_inputs))

    app_main.main()
    out = capsys.readouterr().out

    assert 'Статус операции "test" недоступен.' in out
    assert "Не найдено ни одной транзакции, подходящей под ваши условия фильтрации" in out


def test_main_retries_invalid_menu_choice(monkeypatch: Any, capsys: Any) -> None:
    operations = [_operation("Перевод организации", "EXECUTED")]
    monkeypatch.setattr(app_main, "_load_transactions", lambda _: operations)

    user_inputs = iter(["0", "2", "EXECUTED", "нет", "нет", "нет"])
    monkeypatch.setattr("builtins.input", lambda: next(user_inputs))

    app_main.main()
    out = capsys.readouterr().out

    assert "Недоступный пункт меню. Введите 1, 2 или 3." in out
    assert "Для обработки выбран CSV-файл." in out
