from src.external_api import convert_to_rubles


def test_convert_to_rubles_rub():
    transaction = {"amount": 100, "currency": "RUB"}
    assert convert_to_rubles(transaction) == 100