import pytest
from unittest.mock import patch, Mock
from src.external_api import convert_to_rubles

def test_convert_to_rubles_rub():
    transaction = {"amount": 100, "currency": "RUB"}
    assert convert_to_rubles(transaction) == 100

@patch("src.external_api.requests.get")
def test_convert_to_rubles_usd(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"rates": {"USD": 0.012}}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    transaction = {"amount": 100, "currency": "USD"}
    result = convert_to_rubles(transaction)
    assert isinstance(result, float)
    assert result > 0

@patch("src.external_api.requests.get")
def test_convert_to_rubles_eur(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"rates": {"EUR": 0.011}}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    transaction = {"amount": 100, "currency": "EUR"}
    result = convert_to_rubles(transaction)
    assert isinstance(result, float)
    assert result > 0