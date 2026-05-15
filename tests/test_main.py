"""Tests for main.py Product/Category demo."""

from pathlib import Path

import pytest
import runpy

from src.category import Category


@pytest.fixture(autouse=True)
def reset_category_counters() -> None:
    """Reset class counters before running main.py."""
    Category.category_count = 0
    Category.product_count = 0


def test_main_runs_without_error(capsys: pytest.CaptureFixture[str]) -> None:
    main_path = Path(__file__).resolve().parents[1] / "main.py"
    runpy.run_path(str(main_path), run_name="__main__")
    out = capsys.readouterr().out

    assert "Samsung Galaxy S23 Ultra" in out
    assert "True" in out
    assert "Телевизоры" in out
    assert "2" in out
    assert "4" in out
