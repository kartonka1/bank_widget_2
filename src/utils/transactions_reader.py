"""Helpers for reading transaction data from CSV and Excel files."""

from typing import Any, cast

import pandas as pd

from src.logger_config import get_file_logger

logger = get_file_logger("src.utils", "utils.log")


def _dataframe_to_records(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a DataFrame to transaction records and replace NaN values with None."""
    prepared_dataframe = dataframe.where(pd.notna(dataframe), None)
    return cast(list[dict[str, Any]], prepared_dataframe.to_dict(orient="records"))


def read_transactions_from_csv(file_path: str) -> list[dict[str, Any]]:
    """Return transactions from a CSV file or an empty list on failure."""
    try:
        dataframe = pd.read_csv(file_path)
    except FileNotFoundError:
        logger.error("CSV file not found: %s", file_path)
        return []
    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty: %s", file_path)
        return []
    except (pd.errors.ParserError, OSError, ValueError) as error:
        logger.error("Failed to read CSV file %s: %s", file_path, error)
        return []

    records = _dataframe_to_records(dataframe)
    logger.debug("Loaded %s transaction records from CSV %s", len(records), file_path)
    return records


def read_transactions_from_excel(file_path: str) -> list[dict[str, Any]]:
    """Return transactions from an Excel file or an empty list on failure."""
    try:
        dataframe = pd.read_excel(file_path)
    except FileNotFoundError:
        logger.error("Excel file not found: %s", file_path)
        return []
    except ValueError as error:
        logger.error("Failed to parse Excel file %s: %s", file_path, error)
        return []
    except OSError as error:
        logger.error("Failed to read Excel file %s: %s", file_path, error)
        return []

    records = _dataframe_to_records(dataframe)
    logger.debug("Loaded %s transaction records from Excel %s", len(records), file_path)
    return records
