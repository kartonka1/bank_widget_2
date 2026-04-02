from unittest.mock import Mock, patch

import pytest

from src.external_api.currency import convert_to_rubles


@patch("src.external_api.currency.requests.get")
def test_convert_to_rubles_rub_direct(mock_get: Mock) -> None:
    transaction = {"operationAmount": {"amount": 100, "currency": {"code": "RUB"}}}
    result = convert_to_rubles(transaction)
    assert result == 100.0
    mock_get.assert_not_called()


@patch("src.external_api.currency.requests.get")
def test_convert_to_rubles_usd_direct(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 80.0}}
    mock_get.return_value = mock_response

    transaction = {"operationAmount": {"amount": 100, "currency": {"code": "USD"}}}
    result = convert_to_rubles(transaction)
    assert result == 8000.0


@patch("src.external_api.currency.requests.get")
def test_convert_to_rubles_eur_direct(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 90.0}}
    mock_get.return_value = mock_response

    transaction = {"operationAmount": {"amount": 100, "currency": {"code": "EUR"}}}
    result = convert_to_rubles(transaction)
    assert result == 9000.0


@patch("src.external_api.currency.requests.get")
def test_convert_to_rubles_top_level_currency_object(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 80.0}}
    mock_get.return_value = mock_response

    transaction = {"amount": 100, "currency": {"code": "USD"}}
    result = convert_to_rubles(transaction)
    assert result == 8000.0


@patch("src.external_api.currency.requests.get")
def test_convert_to_rubles_raises_for_missing_rate(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"rates": {}}
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="exchange rate"):
        convert_to_rubles({"amount": 100, "currency": "USD"})
