"""Reporting functions for transaction analytics."""

from __future__ import annotations

import json
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

from src.logger_config import get_file_logger

logger = get_file_logger("src.reports", "reports.log")
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports_output"

_DATE_COLUMNS = ("Дата операции", "date")
_AMOUNT_COLUMNS = ("Сумма платежа", "Сумма операции", "amount")
_CATEGORY_COLUMNS = ("Категория", "category")


def _parse_dates(series: pd.Series) -> pd.Series:
    source = series.astype(str)
    dayfirst_mask = source.str.contains(r"\d{1,2}\.\d{1,2}\.\d{2,4}", regex=True, na=False)
    parsed = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    if dayfirst_mask.any():
        parsed.loc[dayfirst_mask] = pd.to_datetime(series.loc[dayfirst_mask], errors="coerce", dayfirst=True)
    if (~dayfirst_mask).any():
        parsed.loc[~dayfirst_mask] = pd.to_datetime(series.loc[~dayfirst_mask], errors="coerce")
    missing_mask = parsed.isna()
    if missing_mask.any():
        parsed.loc[missing_mask] = pd.to_datetime(series.loc[missing_mask], errors="coerce", dayfirst=True)
    return parsed


def _pick_first(dataframe: pd.DataFrame, names: tuple[str, ...]) -> str | None:
    for name in names:
        if name in dataframe.columns:
            return name
    return None


def _ensure_prepared(transactions: pd.DataFrame) -> pd.DataFrame:
    data = transactions.copy()
    if data.empty:
        return data

    date_col = _pick_first(data, _DATE_COLUMNS)
    amount_col = _pick_first(data, _AMOUNT_COLUMNS)
    category_col = _pick_first(data, _CATEGORY_COLUMNS)

    if date_col:
        data["__date"] = _parse_dates(data[date_col])
    else:
        data["__date"] = pd.NaT
    data["__amount"] = pd.to_numeric(data[amount_col], errors="coerce").fillna(0.0) if amount_col else 0.0
    data["__category"] = data[category_col].fillna("").astype(str) if category_col else ""
    return data.dropna(subset=["__date"])


def report_to_file(filename: str | None = None) -> Callable[..., Any]:
    """Save report result to a JSON file."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            REPORTS_DIR.mkdir(exist_ok=True)
            target_name = filename or f"{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            target_path = REPORTS_DIR / target_name

            if isinstance(result, pd.DataFrame):
                payload = result.to_dict(orient="records")
            else:
                payload = result

            with target_path.open("w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2, default=str)
            return result

        return wrapper

    if callable(filename):
        func = filename
        filename = None
        return decorator(func)
    return decorator


def _three_month_window(date: Optional[str]) -> tuple[pd.Timestamp, pd.Timestamp]:
    end_date = pd.to_datetime(date) if date else pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(months=3)
    return start_date, end_date


@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Return expenses by category for the last three months."""
    data = _ensure_prepared(transactions)
    if data.empty:
        return pd.DataFrame(columns=["date", "category", "amount"])

    start_date, end_date = _three_month_window(date)
    filtered = data[
        (data["__date"] >= start_date)
        & (data["__date"] <= end_date)
        & (data["__category"] == category)
        & (data["__amount"] > 0)
    ]

    result = filtered.loc[:, ["__date", "__category", "__amount"]].rename(
        columns={"__date": "date", "__category": "category", "__amount": "amount"}
    )
    return result.sort_values("date")


@report_to_file()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Return average expenses by weekdays for the last three months."""
    data = _ensure_prepared(transactions)
    if data.empty:
        return pd.DataFrame(columns=["weekday", "average_spending"])

    start_date, end_date = _three_month_window(date)
    filtered = data[(data["__date"] >= start_date) & (data["__date"] <= end_date) & (data["__amount"] > 0)].copy()
    filtered["weekday"] = filtered["__date"].dt.day_name()
    result = filtered.groupby("weekday", as_index=False)["__amount"].mean()
    return result.rename(columns={"__amount": "average_spending"}).sort_values("weekday")


@report_to_file()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Return average spending for workdays vs weekends for the last three months."""
    data = _ensure_prepared(transactions)
    if data.empty:
        return pd.DataFrame(columns=["day_type", "average_spending"])

    start_date, end_date = _three_month_window(date)
    filtered = data[(data["__date"] >= start_date) & (data["__date"] <= end_date) & (data["__amount"] > 0)].copy()
    filtered["day_type"] = filtered["__date"].dt.weekday.apply(lambda value: "workday" if value < 5 else "weekend")
    result = filtered.groupby("day_type", as_index=False)["__amount"].mean()
    return result.rename(columns={"__amount": "average_spending"}).sort_values("day_type")

