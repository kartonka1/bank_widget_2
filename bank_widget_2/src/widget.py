from datetime import datetime

from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(data: str) -> str:
    """
    Принимает строку с типом и номером карты или счёта.
    Маскирует номер с помощью функций из masks.py.

    Примеры:
        "Visa Platinum 7000792289606361" -> "Visa Platinum 7000 79** **** 6361"
        "Счет 73654108430135874305" -> "Счет **4305"
    """
    # Проверяем, начинается ли строка со слова "Счет"
    if data.startswith("Счет"):
        # Разделяем строку и получаем номер счёта
        parts = data.split()
        account_number = int(parts[-1])

        # Маскируем номер счёта с помощью функции из masks.py
        masked = get_mask_account(account_number)
        return f"Счет {masked}"

    # Если это карта, обрабатываем иначе
    *name_parts, card_number = data.split()
    card_name = " ".join(name_parts)

    # Маскируем номер карты
    masked = get_mask_card_number(int(card_number))
    return f"{card_name} {masked}"


def get_date(date_str: str) -> str:
    """
    Принимает дату в формате '2024-03-11T02:26:18.671407'
    и возвращает её в формате '11.03.2024'.
    """
    # Преобразуем строку в объект datetime
    date_obj = datetime.fromisoformat(date_str)

    # Возвращаем дату в нужном формате
    return date_obj.strftime("%d.%m.%Y")
