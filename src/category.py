"""Category model for catalog homework."""

from src.product import Product


class Category:
    """Represents a product category with a list of products."""

    category_count: int = 0
    product_count: int = 0

    name: str
    description: str
    products: list[Product]

    def __init__(self, name: str, description: str, products: list[Product]) -> None:
        self.name = name
        self.description = description
        self.products = products
        Category.category_count += 1
        Category.product_count += len(products)
