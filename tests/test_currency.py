from unittest.mock import Mock, patch

import pytest

from src.external_api.currency import convert_to_rubles


def test_convert_to_rubles_rub() -> None:
    transaction = {"amount": 100, "currency": "RUB"}
    result = convert_to_rubles(transaction)
    assert isinstance(result, float)
    assert result == 100


@patch("src.external_api.currency.requests.get")
def test_convert_to_rubles_usd(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 90.0}}
    mock_get.return_value = mock_response

    transaction = {"amount": 2, "currency": "USD"}
    result = convert_to_rubles(transaction)
    assert isinstance(result, float)
    assert result == 180.0


@patch("src.external_api.currency.requests.get")
def test_convert_to_rubles_eur(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 100.0}}
    mock_get.return_value = mock_response

    transaction = {"amount": 3, "currency": "EUR"}
    result = convert_to_rubles(transaction)
    assert isinstance(result, float)
    assert result == 300.0


def test_convert_to_rubles_unsupported_currency() -> None:
    transaction = {"amount": 50, "currency": "GBP"}
    with pytest.raises(ValueError):
        convert_to_rubles(transaction)
