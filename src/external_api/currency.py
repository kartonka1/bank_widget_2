import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EXCHANGE_RATES_API_KEY")
API_URL = "https://api.apilayer.com/exchangerates_data/latest"
SUPPORTED_CURRENCIES = {"USD", "EUR"}


def _extract_currency_code(raw_currency: Any) -> str | None:
    if isinstance(raw_currency, dict):
        code = raw_currency.get("code")
        return str(code).upper() if code is not None else None

    if raw_currency is None:
        return None

    return str(raw_currency).upper()


def _parse_transaction(transaction: dict[str, Any]) -> tuple[float, str]:
    amount = transaction.get("amount")
    currency_code = _extract_currency_code(transaction.get("currency"))

    if amount is None or currency_code is None:
        operation_amount = transaction.get("operationAmount", {})
        amount = operation_amount.get("amount")
        currency_code = _extract_currency_code(operation_amount.get("currency"))

    if amount is None or currency_code is None:
        raise ValueError("Transaction must contain amount and currency.")

    return float(amount), currency_code


def convert_to_rubles(transaction: dict[str, Any]) -> float:
    amount, currency_code = _parse_transaction(transaction)

    if currency_code == "RUB":
        return amount

    if currency_code not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Conversion for currency {currency_code} is not supported.")

    headers = {"apikey": API_KEY} if API_KEY else {}
    params = {"base": currency_code, "symbols": "RUB"}

    response = requests.get(API_URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    rates = data.get("rates", {})
    rate = rates.get("RUB")

    if rate is None:
        raise ValueError("API did not return the expected exchange rate.")

    return amount * float(rate)
