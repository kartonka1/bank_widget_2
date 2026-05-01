"""Service layer for analytical and search features."""

from __future__ import annotations

import json
import re
from functools import reduce
from typing import Any

import pandas as pd

from src.logger_config import get_file_logger

logger = get_file_logger("src.services", "services.log")

_DATE_COLUMN_CANDIDATES = ("Дата операции", "date")
_AMOUNT_COLUMN_CANDIDATES = ("Сумма операции", "Сумма платежа", "amount")
_CATEGORY_COLUMN_CANDIDATES = ("Категория", "category")
_DESCRIPTION_COLUMN_CANDIDATES = ("Описание", "description")


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


def _to_dataframe(data: list[dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    return pd.DataFrame(data)


def _prepare(data: list[dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    dataframe = _to_dataframe(data)
    if dataframe.empty:
        return dataframe

    date_col = _pick_first(dataframe, _DATE_COLUMN_CANDIDATES)
    amount_col = _pick_first(dataframe, _AMOUNT_COLUMN_CANDIDATES)
    category_col = _pick_first(dataframe, _CATEGORY_COLUMN_CANDIDATES)
    description_col = _pick_first(dataframe, _DESCRIPTION_COLUMN_CANDIDATES)

    if date_col:
        dataframe["__date"] = _parse_dates(dataframe[date_col])
    else:
        dataframe["__date"] = pd.NaT

    dataframe["__amount"] = (
        pd.to_numeric(dataframe[amount_col], errors="coerce").fillna(0.0) if amount_col else 0.0
    )
    dataframe["__category"] = dataframe[category_col].fillna("").astype(str) if category_col else ""
    dataframe["__description"] = dataframe[description_col].fillna("").astype(str) if description_col else ""
    return dataframe.dropna(subset=["__date"])


def cashback_categories(data: list[dict[str, Any]] | pd.DataFrame, year: int, month: int) -> str:
    """Return potential cashback by category for a given month."""
    dataframe = _prepare(data)
    if dataframe.empty:
        return json.dumps({}, ensure_ascii=False)

    period = dataframe[(dataframe["__date"].dt.year == year) & (dataframe["__date"].dt.month == month)]
    expenses = period[period["__amount"] > 0]
    grouped = expenses.groupby("__category")["__amount"].sum()
    cashback = {category: int(round(amount / 100)) for category, amount in grouped.items() if category}
    top3 = dict(sorted(cashback.items(), key=lambda item: item[1], reverse=True)[:3])
    return json.dumps(top3, ensure_ascii=False)


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """Calculate saved amount for investment bank round-ups."""
    target = pd.to_datetime(f"{month}-01", format="%Y-%m-%d", errors="coerce")
    if pd.isna(target):
        raise ValueError("month must match format YYYY-MM")
    if limit <= 0:
        raise ValueError("limit must be a positive integer")

    dataframe = _prepare(transactions)
    if dataframe.empty:
        return 0.0

    filtered = dataframe[
        (dataframe["__date"].dt.year == target.year) & (dataframe["__date"].dt.month == target.month) & (dataframe["__amount"] > 0)
    ]
    round_ups = map(lambda value: (limit - (value % limit)) % limit, filtered["__amount"].tolist())
    result = reduce(lambda acc, item: acc + item, round_ups, 0.0)
    return float(round(result, 2))


def simple_search(data: list[dict[str, Any]] | pd.DataFrame, query: str) -> str:
    """Find transactions by case-insensitive substring in category or description."""
    dataframe = _prepare(data)
    base_columns = [column for column in dataframe.columns if not column.startswith("__")]
    if not query:
        return dataframe[base_columns].to_json(orient="records", force_ascii=False, date_format="iso")

    lowered = query.lower()
    filtered = dataframe[
        dataframe["__category"].str.lower().str.contains(lowered, na=False)
        | dataframe["__description"].str.lower().str.contains(lowered, na=False)
    ]
    return filtered[base_columns].to_json(orient="records", force_ascii=False, date_format="iso")


def search_by_phone_numbers(data: list[dict[str, Any]] | pd.DataFrame) -> str:
    """Find transactions containing a mobile phone number in description."""
    dataframe = _prepare(data)
    phone_pattern = re.compile(r"(?:\+7|8)\D*\d{3}\D*\d{3}\D*\d{2}\D*\d{2}")
    filtered = dataframe[dataframe["__description"].str.contains(phone_pattern, na=False)]
    base_columns = [column for column in dataframe.columns if not column.startswith("__")]
    return filtered[base_columns].to_json(orient="records", force_ascii=False, date_format="iso")


def search_personal_transfers(data: list[dict[str, Any]] | pd.DataFrame) -> str:
    """Find transfer transactions to individuals."""
    dataframe = _prepare(data)
    name_pattern = re.compile(r"[А-ЯA-ZЁ][а-яa-zё]+ [А-ЯA-ZЁ]\.")
    filtered = dataframe[
        (dataframe["__category"].str.lower() == "переводы") & dataframe["__description"].str.contains(name_pattern, na=False)
    ]
    base_columns = [column for column in dataframe.columns if not column.startswith("__")]
    return filtered[base_columns].to_json(orient="records", force_ascii=False, date_format="iso")


profitable_cashback_categories = cashback_categories
phone_number_search = search_by_phone_numbers
personal_transfers_search = search_personal_transfers

