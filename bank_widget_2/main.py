from src.masks import get_mask_account, get_mask_card_number
from src.widget import get_date, mask_account_card


def main() -> None:
    # Проверка функций из masks.py
    card_number = 1234567812345678
    account_number = 9876543210

    masked_card = get_mask_card_number(card_number)
    masked_account = get_mask_account(account_number)

    print(f"Маскированная карта: {masked_card}")
    print(f"Маскированный счёт: {masked_account}")

    # Проверка функции mask_account_card из widget.py
    test_data = [
        "Visa Platinum 7000792289606361",
        "Maestro 1596837868705199",
        "Счет 73654108430135874305",
    ]

    for item in test_data:
        print(mask_account_card(item))

    # Проверка функции get_date из widget.py
    test_date = "2024-03-11T02:26:18.671407"
    print(get_date(test_date))


if __name__ == "__main__":
    main()
