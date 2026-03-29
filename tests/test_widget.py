from typing import List, Tuple

import pytest

from src.widget import mask_account_card, get_date


@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
        ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
        ("Счет 73654108430135874305", "Счет **4305"),
    ],
)
def test_mask_account_card(input_value: str, expected: str) -> None:
    assert mask_account_card(input_value) == expected


@pytest.fixture
def sample_dates() -> List[Tuple[str, str]]:
    return [
        ("2024-03-11T02:26:18.671407", "11.03.2024"),
        ("2023-12-25T15:45:00.000000", "25.12.2023"),
    ]


def test_get_date(sample_dates: List[Tuple[str, str]]) -> None:
    for input_value, expected in sample_dates:
        assert get_date(input_value) == expected
