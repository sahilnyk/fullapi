"""Product schemas."""

from typing import Optional
from pydantic import BaseModel


class ProductBase(BaseModel):
    """Base Product schema."""
    name: str
    # Add more fields as needed


class ProductCreate(ProductBase):
    """Product creation schema."""
    pass


class ProductUpdate(ProductBase):
    """Product update schema."""
    name: Optional[str] = None
    # Add more fields as needed


class Product(ProductBase):
    """Product response schema."""
    id: int

    class Config:
        from_attributes = True
