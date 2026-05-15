"""Tests for Product, Category and JSON loading."""

from pathlib import Path

import pytest

from src.category import Category
from src.product import Product
from src.utils.products_loader import load_categories_from_json

PRODUCTS_JSON = Path(__file__).resolve().parents[1] / "data" / "products.json"


@pytest.fixture(autouse=True)
def reset_category_counters() -> None:
    """Reset class counters so tests do not affect each other."""
    Category.category_count = 0
    Category.product_count = 0


def test_product_initialization() -> None:
    product = Product(
        name="iPhone 15",
        description="128 ГБ",
        price=89990.50,
        quantity=14,
    )

    assert product.name == "iPhone 15"
    assert product.description == "128 ГБ"
    assert product.price == 89990.50
    assert product.quantity == 14


def test_category_initialization() -> None:
    product = Product("Наушники", "Беспроводные", 19990.0, 8)
    category = Category(
        name="Аудио",
        description="Звуковая техника",
        products=[product],
    )

    assert category.name == "Аудио"
    assert category.description == "Звуковая техника"
    assert category.products == [product]
    assert isinstance(category.products[0], Product)


def test_category_count() -> None:
    Category("Первая", "Описание", [])
    Category("Вторая", "Описание", [])
    Category("Третья", "Описание", [])

    assert Category.category_count == 3


def test_product_count() -> None:
    first_product = Product("Товар 1", "Описание", 1000.0, 1)
    second_product = Product("Товар 2", "Описание", 2000.0, 2)
    third_product = Product("Товар 3", "Описание", 3000.0, 3)

    Category("Категория 1", "Описание", [first_product, second_product])
    Category("Категория 2", "Описание", [third_product])

    assert Category.product_count == 3


def test_load_categories_from_json() -> None:
    categories = load_categories_from_json(str(PRODUCTS_JSON))

    assert len(categories) == 3
    assert categories[0].name == "Смартфоны"
    assert len(categories[0].products) == 2
    assert categories[0].products[0].name == "iPhone 15"
    assert categories[0].products[0].price == 89990.50
    assert categories[1].products[2].quantity == 5
    assert Category.category_count == 3
    assert Category.product_count == 6
