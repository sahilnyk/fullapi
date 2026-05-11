"""Product CRUD operations."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.product import Product
from schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(Generic[TypeVar("ModelType", bound=Product)]):
    """CRUD operations for Product."""

    def get(self, db: Session, id: Any) -> Optional[Product]:
        """Get product by ID."""
        return db.query(Product).filter(Product.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Get multiple products."""
        return db.query(Product).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ProductCreate) -> Product:
        """Create new product."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Product(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Product,
        obj_in: Union[ProductUpdate, Dict[str, Any]]
    ) -> Product:
        """Update product."""
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

    def remove(self, db: Session, *, id: int) -> Product:
        """Remove product."""
        obj = db.query(Product).get(id)
        db.delete(obj)
        db.commit()
        return obj


# Create a singleton instance
product_crud = CRUDProduct()
