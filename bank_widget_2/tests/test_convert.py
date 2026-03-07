from src.external_api import convert_to_rubles


def test_convert_to_rubles_multiple(monkeypatch):
    transactions = [
        {"operationAmount": {"amount": 100, "currency": {"code": "RUB"}}},
        {"operationAmount": {"amount": 50, "currency": {"code": "USD"}}},
        {"operationAmount": {"amount": 70, "currency": {"code": "EUR"}}},
    ]

    def fake_get(*args, **kwargs):
        class FakeResponse:
            def raise_for_status(self): pass
            def json(self): return {"rates": {"RUB": 80.0, "EUR": 90.0, "USD": 80.0}}
        return FakeResponse()

    import src.external_api
    monkeypatch.setattr(src.external_api.requests, "get", fake_get)

    results = [convert_to_rubles(t) for t in transactions]
    assert results[0] == 100.0
    assert results[1] == 50 * 80.0
    assert results[2] == 70 * 90.0
