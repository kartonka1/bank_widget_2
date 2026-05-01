import pandas as pd

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"date": "2024-01-10", "category": "Еда", "amount": 1000},
            {"date": "2024-01-11", "category": "Еда", "amount": 500},
            {"date": "2024-01-12", "category": "Такси", "amount": 300},
            {"date": "2024-01-13", "category": "Пополнение", "amount": -4000},
        ]
    )


def test_spending_by_category() -> None:
    result = spending_by_category(_sample_df(), "Еда", "2024-01-20")
    assert not result.empty
    assert set(result["category"].unique()) == {"Еда"}


def test_spending_by_weekday() -> None:
    result = spending_by_weekday(_sample_df(), "2024-01-20")
    assert "weekday" in result.columns
    assert "average_spending" in result.columns


def test_spending_by_workday() -> None:
    result = spending_by_workday(_sample_df(), "2024-01-20")
    assert set(result["day_type"].tolist()) <= {"workday", "weekend"}
