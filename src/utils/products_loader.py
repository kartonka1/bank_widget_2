"""Load categories and products from JSON."""

import json
from pathlib import Path

from src.category import Category
from src.product import Product


def load_categories_from_json(file_path: str) -> list[Category]:
    """Read a JSON file and return a list of Category objects with Product items."""
    path = Path(file_path)
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    categories: list[Category] = []
    for item in data:
        products = [
            Product(
                name=product["name"],
                description=product["description"],
                price=float(product["price"]),
                quantity=int(product["quantity"]),
            )
            for product in item["products"]
        ]
        categories.append(
            Category(
                name=item["name"],
                description=item["description"],
                products=products,
            )
        )
    return categories
