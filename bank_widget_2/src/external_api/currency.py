import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("EXCHANGE_RATES_API_KEY")
API_URL = "https://api.apilayer.com/exchangerates_data/latest"

def convert_to_rubles(transaction: dict) -> float:
    amount = float(transaction.get("amount", 0))
    currency = transaction.get("currency", "RUB").upper()

    if currency == "RUB":
        return amount

    if currency not in ["USD", "EUR"]:
        raise ValueError(f"Conversion for currency {currency} is not supported.")

    headers = {"apikey": API_KEY}
    params = {"base": currency, "symbols": "RUB"}

    response = requests.get(API_URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if "rates" not in data or "RUB" not in data["rates"]:
        raise ValueError("API did not return the expected exchange rate.")

    rate = data["rates"]["RUB"]
    return amount * rate