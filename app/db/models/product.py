from pydantic import BaseModel
from typing import Dict


class AddProduct(BaseModel):
    """
    Model for adding a new product.
    """

    product_name: str
    product_description: str
    image: str
    category: str
    brand: str
    colour: str
    dimensions: str
    box_includes: str
    dynamic_attributes: Dict[str, str]
    amount_in_stock: int
    price: int


class GetProduct(BaseModel):
    """
    Model for retrieving a product from the database.
    """

    id: str  # Stringified ObjectId
    product_name: str
    product_description: str
    image: str
    category: str
    brand: str
    colour: str
    dimensions: str
    box_includes: str
    dynamic_attributes: Dict[str, str]
    amount_in_stock: int
    price: int
