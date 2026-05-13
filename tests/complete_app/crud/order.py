"""Order CRUD operations."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.order import Order
from schemas.order import OrderCreate, OrderUpdate


class CRUDOrder(Generic[TypeVar("ModelType", bound=Order)]):
    """CRUD operations for Order."""

    def get(self, db: Session, id: Any) -> Optional[Order]:
        """Get order by ID."""
        return db.query(Order).filter(Order.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get multiple orders."""
        return db.query(Order).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: OrderCreate) -> Order:
        """Create new order."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Order(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Order,
        obj_in: Union[OrderUpdate, Dict[str, Any]]
    ) -> Order:
        """Update order."""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Order:
        """Remove order."""
        obj = db.query(Order).get(id)
        db.delete(obj)
        db.commit()
        return obj


# Create a singleton instance
order_crud = CRUDOrder()
