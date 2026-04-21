"""Application entry point for transaction filtering workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.operations import process_bank_search
from src.processing import filter_by_state, sort_by_date
from src.utils.json_loader import load_operations
from src.utils.transactions_reader import read_transactions_from_csv, read_transactions_from_excel
from src.widget import get_date, mask_account_card

VALID_STATUSES = {"EXECUTED", "CANCELED", "PENDING"}


def _is_yes(answer: str) -> bool:
    """Return True for positive answers in Russian/English."""
    return answer.strip().lower() in {"да", "yes", "y", "д"}


def _safe_mask(value: str) -> str:
    """Mask account/card number if possible, otherwise return source value."""
    try:
        return mask_account_card(value)
    except (ValueError, TypeError):
        return value


def _load_transactions(choice: str) -> list[dict[str, Any]]:
    """Load transactions for selected source choice."""
    data_dir = Path(__file__).resolve().parent / "data"
    if choice == "1":
        return load_operations(str(data_dir / "operations.json"))
    if choice == "2":
        return read_transactions_from_csv(str(data_dir / "transactions.csv"))

    return read_transactions_from_excel(str(data_dir / "transactions_excel.xlsx"))


def _format_operation(operation: dict[str, Any]) -> str:
    """Build multiline text representation of one operation."""
    description = str(operation.get("description", ""))
    date_value = str(operation.get("date", ""))

    try:
        date_text = get_date(date_value)
    except ValueError:
        date_text = date_value

    from_account = str(operation.get("from", "")).strip()
    to_account = str(operation.get("to", "")).strip()
    route_parts = []
    if from_account:
        route_parts.append(_safe_mask(from_account))
    if to_account:
        route_parts.append(_safe_mask(to_account))
    route_line = " -> ".join(route_parts)

    operation_amount = operation.get("operationAmount", {})
    amount = str(operation_amount.get("amount", "0"))
    currency = str(operation_amount.get("currency", {}).get("code", ""))
    currency_text = "руб." if currency == "RUB" else currency

    lines = [f"{date_text} {description}"]
    if route_line:
        lines.append(route_line)
    lines.append(f"Сумма: {amount} {currency_text}")
    return "\n".join(lines)


def main() -> None:
    """Run interactive transaction filtering flow."""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    source = input().strip()
    while source not in {"1", "2", "3"}:
        print("Недоступный пункт меню. Введите 1, 2 или 3.")
        source = input().strip()

    source_messages = {
        "1": "Для обработки выбран JSON-файл.",
        "2": "Для обработки выбран CSV-файл.",
        "3": "Для обработки выбран XLSX-файл.",
    }
    print(source_messages[source])
    operations = _load_transactions(source)

    status_prompt = (
        "Введите статус, по которому необходимо выполнить фильтрацию.\n"
        "Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING"
    )
    print(status_prompt)
    status_input = input().strip()
    status = status_input.upper()
    while status not in VALID_STATUSES:
        print(f'Статус операции "{status_input}" недоступен.')
        print(status_prompt)
        status_input = input().strip()
        status = status_input.upper()

    filtered = filter_by_state(operations, status)
    print(f'Операции отфильтрованы по статусу "{status}"')

    print("Отсортировать операции по дате? Да/Нет")
    if _is_yes(input()):
        print("Отсортировать по возрастанию или по убыванию?")
        sorting_order = input().strip().lower()
        filtered = sort_by_date(filtered, reverse="возрастан" not in sorting_order)

    print("Выводить только рублевые транзакции? Да/Нет")
    if _is_yes(input()):
        filtered = [
            operation
            for operation in filtered
            if str(operation.get("operationAmount", {}).get("currency", {}).get("code", "")) == "RUB"
        ]

    print("Отфильтровать список транзакций по определенному слову в описании? Да/Нет")
    if _is_yes(input()):
        print("Введите слово для поиска:")
        filtered = process_bank_search(filtered, input().strip())

    print("Распечатываю итоговый список транзакций...")
    if not filtered:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    print(f"Всего банковских операций в выборке: {len(filtered)}")
    for operation in filtered:
        print()
        print(_format_operation(operation))


if __name__ == "__main__":
    main()
