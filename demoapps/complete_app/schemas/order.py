"""Order schemas."""

from typing import Optional
from pydantic import BaseModel


class OrderBase(BaseModel):
    """Base Order schema."""
    name: str
    # Add more fields as needed


class OrderCreate(OrderBase):
    """Order creation schema."""
    pass


class OrderUpdate(OrderBase):
    """Order update schema."""
    name: Optional[str] = None
    # Add more fields as needed


class Order(OrderBase):
    """Order response schema."""
    id: int

    class Config:
        from_attributes = True
