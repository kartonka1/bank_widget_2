from unittest.mock import patch, Mock
from src.external_api import convert_to_rubles

@patch("external_api.requests.get")
def test_convert_to_rubles_rub_direct(mock_get):
    transaction = {"operationAmount": {"amount": 100, "currency": {"code": "RUB"}}}
    result = convert_to_rubles(transaction)
    assert result == 100.0

@patch("external_api.requests.get")
def test_convert_to_rubles_usd_direct(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 80.0}}
    mock_get.return_value = mock_response

    transaction = {"operationAmount": {"amount": 100, "currency": {"code": "USD"}}}
    result = convert_to_rubles(transaction)
    assert result == 8000.0

@patch("external_api.requests.get")
def test_convert_to_rubles_eur_direct(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 90.0}}
    mock_get.return_value = mock_response

    transaction = {"operationAmount": {"amount": 100, "currency": {"code": "EUR"}}}
    result = convert_to_rubles(transaction)
    assert result == 9000.0