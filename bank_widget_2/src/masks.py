def get_mask_card_number(card_number: int) -> str:
    """
    Возвращает маску номера карты по правилу XXXX XX** **** XXXX.

    :param card_number: Номер карты
    :return: Маскированный номер
    """
    number_str = str(card_number)
    if len(number_str) != 16:
        raise ValueError("Номер карты должен содержать 16 цифр")
    return f"{number_str[:4]} {number_str[4:6]}** **** {number_str[-4:]}"


def get_mask_account(account_number: int) -> str:
    """
    Возвращает маску номера счёта по правилу **XXXX.

    :param account_number: Номер счёта
    :return: Маскированный счёт
    """
    number_str = str(account_number)
    if len(number_str) < 4:
        raise ValueError("Номер счёта должен содержать минимум 4 цифры")
    return f"**{number_str[-4:]}"
