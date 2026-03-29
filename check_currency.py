from src.external_api.currency import convert_to_rubles

transaction = {
    "operationAmount": {
        "amount": "10",
        "currency": {
            "code": "USD"
        }
    }
}

result = convert_to_rubles(transaction)
print(result)
