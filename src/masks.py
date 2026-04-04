"""Functions for masking card and account numbers."""

from src.logger_config import get_file_logger

logger = get_file_logger(__name__, "masks.log")


def get_mask_card_number(card_number: int) -> str:
    """Return a masked card number in the format XXXX XX** **** XXXX."""
    number_str = str(card_number)
    if len(number_str) != 16:
        logger.error("Invalid card number length: expected 16 digits, got %s", len(number_str))
        raise ValueError("Номер карты должен содержать 16 цифр")

    masked_number = f"{number_str[:4]} {number_str[4:6]}** **** {number_str[-4:]}"
    logger.debug("Card number masked successfully")
    return masked_number


def get_mask_account(account_number: int) -> str:
    """Return a masked account number in the format **XXXX."""
    number_str = str(account_number)
    if len(number_str) < 4:
        logger.error("Invalid account number length: expected at least 4 digits, got %s", len(number_str))
        raise ValueError("Номер счёта должен содержать минимум 4 цифры")

    masked_account = f"**{number_str[-4:]}"
    logger.debug("Account number masked successfully")
    return masked_account
