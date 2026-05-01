import json

from src.views import events_page, home_page


def _currency_stub(currencies: list[str]) -> list[dict[str, float | str]]:
    return [{"currency": currency, "rate": 10.0} for currency in currencies]


def _stocks_stub(stocks: list[str]) -> list[dict[str, float | str]]:
    return [{"stock": stock, "price": 100.0} for stock in stocks]


def test_home_page_returns_expected_shape(tmp_path) -> None:
    settings_path = tmp_path / "settings.json"
    settings_path.write_text('{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}', encoding="utf-8")
    data = [
        {"Дата операции": "2024-01-10", "Сумма платежа": 1000, "Номер карты": "*1234", "Категория": "Еда", "Описание": "Магазин"},
        {"Дата операции": "2024-01-11", "Сумма платежа": 2500, "Номер карты": "*1234", "Категория": "Транспорт", "Описание": "Такси"},
    ]

    payload = json.loads(
        home_page(
            "2024-01-20 10:00:00",
            data,
            settings_path=str(settings_path),
            currency_fetcher=_currency_stub,
            stock_fetcher=_stocks_stub,
        )
    )

    assert payload["greeting"] == "Доброе утро"
    assert payload["cards"][0]["last_digits"] == "1234"
    assert len(payload["top_transactions"]) == 5
    assert all(set(item.keys()) == {"date", "amount", "category", "description"} for item in payload["top_transactions"])
    assert payload["currency_rates"][0]["currency"] == "USD"
    assert payload["stock_prices"][0]["stock"] == "AAPL"


def test_events_page_returns_required_blocks(tmp_path) -> None:
    settings_path = tmp_path / "settings.json"
    settings_path.write_text('{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}', encoding="utf-8")
    data = [
        {"Дата операции": "2024-01-10", "Сумма платежа": 1000, "Категория": "Супермаркеты", "Описание": "Магазин"},
        {"Дата операции": "2024-01-11", "Сумма платежа": 500, "Категория": "Наличные", "Описание": "ATM"},
        {"Дата операции": "2024-01-12", "Сумма платежа": -2000, "Категория": "Пополнение", "Описание": "ЗП"},
    ]

    payload = json.loads(
        events_page(
            "2024-01-20 10:00:00",
            data,
            range_key="M",
            settings_path=str(settings_path),
            currency_fetcher=_currency_stub,
            stock_fetcher=_stocks_stub,
        )
    )

    assert "expenses" in payload
    assert "income" in payload
    assert "currency_rates" in payload
    assert "stock_prices" in payload
    assert payload["expenses"]["total_amount"] == 1500
    assert payload["income"]["total_amount"] == 2000
