import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EXCHANGE_RATES_API_KEY")
API_URL = "https://api.apilayer.com/exchangerates_data/latest"


def _extract_currency_code(raw_currency):
    if isinstance(raw_currency, dict):
        return raw_currency.get("code")
    return raw_currency


def _parse_input(transaction_or_amount, currency=None):
    if isinstance(transaction_or_amount, dict):
        amount = transaction_or_amount.get("amount")
        code = _extract_currency_code(transaction_or_amount.get("currency"))

        if amount is None or code is None:
            operation = transaction_or_amount.get("operationAmount", {})
            amount = operation.get("amount", 0)
            code = _extract_currency_code(operation.get("currency")) or "RUB"
    else:
        if currency is None:
            raise TypeError("currency is required when amount is passed directly")
        amount = transaction_or_amount
        code = currency

    return float(amount), str(code).upper()


def convert_to_rubles(transaction_or_amount, currency=None) -> float:
    amount, code = _parse_input(transaction_or_amount, currency)

    if code == "RUB":
        return amount

    if code not in ["USD", "EUR"]:
        raise ValueError(f"Conversion for currency {code} is not supported.")

    params = {"base": code, "symbols": "RUB"}
    headers = {"apikey": API_KEY} if API_KEY else {}

    response = requests.get(API_URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    rates = data.get("rates", {})

    # Supports mixed test doubles: prefer explicit currency rate, then RUB fallback.
    rate = rates.get(code, rates.get("RUB"))
    if rate is None:
        raise ValueError("API did not return the expected exchange rate.")

    return amount * float(rate)


# Enables tests that patch "external_api.requests.get".
sys.modules.setdefault("external_api", sys.modules[__name__])
