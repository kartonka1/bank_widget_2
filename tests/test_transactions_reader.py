from typing import Any
from unittest.mock import Mock, patch

import pandas as pd

from src.utils.transactions_reader import read_transactions_from_csv, read_transactions_from_excel


@patch("src.utils.transactions_reader.pd.read_csv")
def test_read_transactions_from_csv_success(mock_read_csv: Mock) -> None:
    dataframe = pd.DataFrame([{"id": 1, "amount": 120.5}, {"id": 2, "amount": 300.0}])
    mock_read_csv.return_value = dataframe

    result = read_transactions_from_csv("data/transactions.csv")

    assert result == [{"id": 1, "amount": 120.5}, {"id": 2, "amount": 300.0}]
    mock_read_csv.assert_called_once_with("data/transactions.csv")


@patch("src.utils.transactions_reader.pd.read_csv", side_effect=FileNotFoundError)
def test_read_transactions_from_csv_missing_file(_: Any) -> None:
    result = read_transactions_from_csv("missing.csv")
    assert result == []


@patch("src.utils.transactions_reader.pd.read_csv", side_effect=pd.errors.EmptyDataError("empty"))
def test_read_transactions_from_csv_empty_file(_: Any) -> None:
    result = read_transactions_from_csv("empty.csv")
    assert result == []


@patch("src.utils.transactions_reader.pd.read_excel")
def test_read_transactions_from_excel_success(mock_read_excel: Mock) -> None:
    dataframe = pd.DataFrame([{"id": 10, "amount": 999.99}, {"id": 11, "amount": 5.5}])
    mock_read_excel.return_value = dataframe

    result = read_transactions_from_excel("data/transactions_excel.xlsx")

    assert result == [{"id": 10, "amount": 999.99}, {"id": 11, "amount": 5.5}]
    mock_read_excel.assert_called_once_with("data/transactions_excel.xlsx")


@patch("src.utils.transactions_reader.pd.read_excel", side_effect=FileNotFoundError)
def test_read_transactions_from_excel_missing_file(_: Any) -> None:
    result = read_transactions_from_excel("missing.xlsx")
    assert result == []


@patch("src.utils.transactions_reader.pd.read_excel", side_effect=ValueError("bad excel"))
def test_read_transactions_from_excel_invalid_file(_: Any) -> None:
    result = read_transactions_from_excel("broken.xlsx")
    assert result == []
