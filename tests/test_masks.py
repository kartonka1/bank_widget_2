from unittest.mock import patch

import pytest

from src.masks import get_mask_account, get_mask_card_number, logger


def test_get_mask_card_number() -> None:
    assert get_mask_card_number(1234567812345678) == "1234 56** **** 5678"
    with pytest.raises(ValueError):
        get_mask_card_number(123)


def test_get_mask_account() -> None:
    assert get_mask_account(9876543210) == "**3210"
    with pytest.raises(ValueError):
        get_mask_account(123)


def test_masks_logger_configuration() -> None:
    assert logger.name == "src.masks"
    assert logger.level == 10
    assert logger.handlers


def test_get_mask_card_number_logs_success() -> None:
    with patch.object(logger, "debug") as mock_debug:
        assert get_mask_card_number(1234567812345678) == "1234 56** **** 5678"

    mock_debug.assert_called_once_with("Card number masked successfully")


def test_get_mask_account_logs_error() -> None:
    with patch.object(logger, "error") as mock_error:
        with pytest.raises(ValueError):
            get_mask_account(123)

    mock_error.assert_called_once()
