"""Order model."""

from sqlalchemy import Column, Integer, String
from db.base import Base


class Order(Base):
    """Order model."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # Add more fields as needed
