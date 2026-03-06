from src.external_api import convert_to_rubles

def test_convert_to_rubles():
    transactions = [
        {"amount": 100, "currency": "RUB"},
        {"amount": 50, "currency": "USD"},
        {"amount": 70, "currency": "EUR"},
    ]

    for t in transactions:
        rub = convert_to_rubles(t)
        assert isinstance(rub, float), f"{t} не вернул float"
        assert rub > 0, f"{t} вернул неположительное значение"
        print(f"{t['amount']} {t['currency']} = {rub:.2f} RUB")

# Запуск функции для теста напрямую
if __name__ == "__main__":
    test_convert_to_rubles()
