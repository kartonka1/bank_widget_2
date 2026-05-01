"""JSON builders for bank web pages."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any, Callable

import pandas as pd
import requests
from dotenv import load_dotenv

from src.logger_config import get_file_logger

logger = get_file_logger("src.views", "views.log")
load_dotenv()

_DATE_COLUMNS = ("Дата операции", "date", "Дата платежа")
_AMOUNT_COLUMNS = ("Сумма платежа", "amount", "Сумма операции")
_CARD_COLUMNS = ("Номер карты", "card_last_digits", "card")
_CATEGORY_COLUMNS = ("Категория", "category")
_DESCRIPTION_COLUMNS = ("Описание", "description")
_STATUS_COLUMNS = ("Статус", "state")
_STATUS_OK = {"OK", "EXECUTED"}


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


def _to_dataframe(data: list[dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    return pd.DataFrame(data)


def _pick_first(dataframe: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate in dataframe.columns:
            return candidate
    return None


def _prepare_operations(data: list[dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    dataframe = _to_dataframe(data)
    if dataframe.empty:
        return dataframe

    date_col = _pick_first(dataframe, _DATE_COLUMNS)
    if date_col is None:
        return pd.DataFrame()

    dataframe = dataframe.copy()
    dataframe["__date"] = _parse_dates(dataframe[date_col])
    dataframe = dataframe.dropna(subset=["__date"])

    amount_col = _pick_first(dataframe, _AMOUNT_COLUMNS)
    if amount_col:
        dataframe["__amount"] = pd.to_numeric(dataframe[amount_col], errors="coerce").fillna(0.0)
    else:
        dataframe["__amount"] = 0.0

    category_col = _pick_first(dataframe, _CATEGORY_COLUMNS)
    dataframe["__category"] = dataframe[category_col].fillna("").astype(str) if category_col else ""

    description_col = _pick_first(dataframe, _DESCRIPTION_COLUMNS)
    dataframe["__description"] = dataframe[description_col].fillna("").astype(str) if description_col else ""

    card_col = _pick_first(dataframe, _CARD_COLUMNS)
    if card_col:
        dataframe["__card"] = dataframe[card_col].fillna("").astype(str).str.extract(r"(\d{4})", expand=False).fillna("")
    else:
        dataframe["__card"] = ""

    status_col = _pick_first(dataframe, _STATUS_COLUMNS)
    if status_col:
        dataframe["__status"] = dataframe[status_col].fillna("").astype(str).str.upper()
        dataframe = dataframe[dataframe["__status"].isin(_STATUS_OK)]

    return dataframe


def _month_range(value: datetime) -> tuple[datetime, datetime]:
    start = value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = value.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def _week_range(value: datetime) -> tuple[datetime, datetime]:
    start = (value - timedelta(days=value.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    end = value.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def _year_range(value: datetime) -> tuple[datetime, datetime]:
    start = value.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end = value.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def _all_range(value: datetime) -> tuple[datetime, datetime]:
    start = datetime.min.replace(tzinfo=None)
    end = value.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def _resolve_greeting(value: datetime) -> str:
    hour = value.hour
    if 6 <= hour <= 11:
        return "Доброе утро"
    if 12 <= hour <= 17:
        return "Добрый день"
    if 18 <= hour <= 22:
        return "Добрый вечер"
    return "Доброй ночи"


def _load_settings(settings_path: str = "user_settings.json") -> dict[str, list[str]]:
    try:
        with open(settings_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        logger.exception("Failed to read settings from %s", settings_path)
        return {"user_currencies": [], "user_stocks": []}

    currencies = [str(item).upper() for item in data.get("user_currencies", [])]
    stocks = [str(item).upper() for item in data.get("user_stocks", [])]
    return {"user_currencies": currencies, "user_stocks": stocks}


def _fetch_currency_rates(currencies: list[str]) -> list[dict[str, float | str]]:
    if not currencies:
        return []

    base = os.getenv("CURRENCY_BASE", "RUB").upper()
    url = os.getenv("CURRENCY_API_URL", "https://open.er-api.com/v6/latest/RUB").replace("/RUB", f"/{base}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()
        rates = payload.get("rates", {})
    except Exception:
        logger.exception("Currency API request failed")
        return [{"currency": currency, "rate": 1.0} for currency in currencies]

    result: list[dict[str, float | str]] = []
    for currency in currencies:
        raw_rate = rates.get(currency)
        if raw_rate is None:
            result.append({"currency": currency, "rate": 1.0})
            continue
        rate = float(raw_rate)
        if rate > 0:
            result.append({"currency": currency, "rate": rate})
        else:
            result.append({"currency": currency, "rate": 1.0})
    return result


def _fetch_stock_prices(stocks: list[str]) -> list[dict[str, float | str]]:
    if not stocks:
        return []

    token = os.getenv("FINNHUB_TOKEN", "")
    if not token:
        logger.warning("FINNHUB_TOKEN is not configured")
        return [{"stock": stock, "price": 1.0} for stock in stocks]

    result: list[dict[str, float | str]] = []
    for stock in stocks:
        try:
            response = requests.get(
                "https://finnhub.io/api/v1/quote",
                params={"symbol": stock, "token": token},
                timeout=10,
            )
            response.raise_for_status()
            price = float(response.json().get("c", 0))
            if price > 0:
                result.append({"stock": stock, "price": price})
            else:
                result.append({"stock": stock, "price": 1.0})
        except Exception:
            logger.exception("Stock API request failed for %s", stock)
            result.append({"stock": stock, "price": 1.0})
    return result


def _transactions_payload(dataframe: pd.DataFrame, amount_desc: bool = True, limit: int = 5) -> list[dict[str, Any]]:
    if dataframe.empty:
        items: list[dict[str, Any]] = []
    else:
        sorted_df = dataframe.sort_values("__amount", ascending=not amount_desc).head(limit)
        items = [
            {
                "date": row["__date"].strftime("%d.%m.%Y"),
                "amount": float(row["__amount"]),
                "category": row["__category"],
                "description": row["__description"],
            }
            for _, row in sorted_df.iterrows()
        ]
    if len(items) < limit:
        items.extend(
            [
                {
                    "date": "01.01.1970",
                    "amount": 0.0,
                    "category": "Нет данных",
                    "description": "Недостаточно транзакций за период",
                }
                for _ in range(limit - len(items))
            ]
        )
    return items[:limit]


def _cards_payload(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    cards_df = dataframe[dataframe["__card"] != ""]
    if cards_df.empty:
        return []
    grouped = cards_df.groupby("__card", as_index=False)["__amount"].sum().sort_values("__amount", ascending=False)
    return [
        {
            "last_digits": row["__card"],
            "total_spent": round(float(row["__amount"]), 2),
            "cashback": round(float(row["__amount"]) / 100, 2),
        }
        for _, row in grouped.iterrows()
    ]


def _parse_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _range_filter(dataframe: pd.DataFrame, start: datetime, end: datetime) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe
    return dataframe[(dataframe["__date"] >= start) & (dataframe["__date"] <= end)].copy()


def home_page(
    date_time: str,
    data: list[dict[str, Any]] | pd.DataFrame,
    settings_path: str = "user_settings.json",
    currency_fetcher: Callable[[list[str]], list[dict[str, float | str]]] = _fetch_currency_rates,
    stock_fetcher: Callable[[list[str]], list[dict[str, float | str]]] = _fetch_stock_prices,
) -> str:
    """Build the JSON response for the Home page."""
    point = _parse_datetime(date_time)
    prepared = _prepare_operations(data)
    start, end = _month_range(point)
    period = _range_filter(prepared, start, end)

    settings = _load_settings(settings_path)
    payload = {
        "greeting": _resolve_greeting(point),
        "cards": _cards_payload(period[period["__amount"] > 0]),
        "top_transactions": _transactions_payload(period, amount_desc=True, limit=5),
        "currency_rates": currency_fetcher(settings["user_currencies"]),
        "stock_prices": stock_fetcher(settings["user_stocks"]),
    }
    return json.dumps(payload, ensure_ascii=False)


def _get_range(point: datetime, range_key: str) -> tuple[datetime, datetime]:
    return {
        "W": _week_range,
        "M": _month_range,
        "Y": _year_range,
        "ALL": _all_range,
    }.get(range_key, _month_range)(point)


def _category_summary(source: pd.DataFrame, keep_top: int = 7) -> list[dict[str, int | str]]:
    if source.empty:
        return []
    grouped = source.groupby("__category", as_index=False)["__amount"].sum()
    grouped = grouped.sort_values("__amount", ascending=False)
    top = grouped.head(keep_top).copy()
    tail_sum = grouped.iloc[keep_top:]["__amount"].sum()
    result = [
        {"category": row["__category"], "amount": int(round(float(row["__amount"])))}
        for _, row in top.iterrows()
    ]
    if tail_sum > 0:
        result.append({"category": "Остальное", "amount": int(round(float(tail_sum)))})
    return result


def _category_full(source: pd.DataFrame) -> list[dict[str, int | str]]:
    if source.empty:
        return []
    grouped = source.groupby("__category", as_index=False)["__amount"].sum().sort_values("__amount", ascending=False)
    return [{"category": row["__category"], "amount": int(round(float(row["__amount"])))} for _, row in grouped.iterrows()]


def events_page(
    date_time: str,
    data: list[dict[str, Any]] | pd.DataFrame,
    range_key: str = "M",
    settings_path: str = "user_settings.json",
    currency_fetcher: Callable[[list[str]], list[dict[str, float | str]]] = _fetch_currency_rates,
    stock_fetcher: Callable[[list[str]], list[dict[str, float | str]]] = _fetch_stock_prices,
) -> str:
    """Build the JSON response for the Events page."""
    point = _parse_datetime(date_time)
    prepared = _prepare_operations(data)
    start, end = _get_range(point, range_key)
    period = _range_filter(prepared, start, end)

    expenses_df = period[period["__amount"] > 0].copy()
    income_df = period[period["__amount"] < 0].copy()
    income_df["__amount"] = income_df["__amount"].abs()

    transfers_cash_df = expenses_df[expenses_df["__category"].isin(["Наличные", "Переводы"])]
    expenses_main = expenses_df[~expenses_df["__category"].isin(["Наличные", "Переводы"])]

    settings = _load_settings(settings_path)
    payload = {
        "expenses": {
            "total_amount": int(round(float(expenses_df["__amount"].sum()))) if not expenses_df.empty else 0,
            "main": _category_summary(expenses_main, keep_top=7),
            "transfers_and_cash": _category_full(transfers_cash_df),
        },
        "income": {
            "total_amount": int(round(float(income_df["__amount"].sum()))) if not income_df.empty else 0,
            "main": _category_full(income_df),
        },
        "currency_rates": currency_fetcher(settings["user_currencies"]),
        "stock_prices": stock_fetcher(settings["user_stocks"]),
    }
    return json.dumps(payload, ensure_ascii=False)


main_page = home_page
events = events_page

