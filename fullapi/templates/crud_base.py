"""Base CRUD template for generic database operations."""

# crud/base.py
CRUD_BASE = '''"""Base CRUD class for generic database operations."""

from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseCRUD(Generic[ModelType]):
    """Base CRUD class with common database operations.
    
    Provides generic methods for create, read, update, and delete operations
    that work with any SQLAlchemy model.
    
    Usage:
        class UserCRUD(BaseCRUD[User]):
            pass
        
        user_crud = UserCRUD(User)
        user = user_crud.get(db, 1)
    """
    
    def __init__(self, model: Type[ModelType]):
        """Initialize CRUD with the model class."""
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single record by ID, excluding soft-deleted records."""
        query = db.query(self.model).filter(self.model.id == id)
        
        # Filter out soft-deleted records if model has soft delete
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)
        
        return query.first()
    
    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        query = db.query(self.model)
        
        # Filter out soft-deleted records if model has soft delete
        if hasattr(self.model, "is_deleted") and not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, db: Session, include_deleted: bool = False) -> int:
        """Count total records."""
        query = db.query(self.model)
        
        if hasattr(self.model, "is_deleted") and not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        
        return query.count()
    
    def create(self, db: Session, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        obj = self.model(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def update(
        self,
        db: Session,
        obj_in: Dict[str, Any],
        id: Optional[int] = None,
        db_obj: Optional[ModelType] = None,
    ) -> Optional[ModelType]:
        """Update an existing record.
        
        Args:
            db: Database session
            obj_in: Dictionary of attributes to update
            id: Record ID (used if db_obj not provided)
            db_obj: Existing record object (avoids extra query)
        """
        if db_obj is None:
            if id is None:
                raise ValueError("Either id or db_obj must be provided")
            db_obj = self.get(db, id)
            if not db_obj:
                return None
        
        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int, hard_delete: bool = False) -> bool:
        """Delete a record (soft delete by default if model supports it).
        
        Args:
            db: Database session
            id: Record ID
            hard_delete: If True, permanently delete. If False, soft delete
                        (only works if model has SoftDeleteMixin)
        
        Returns:
            True if deleted, False if record not found
        """
        obj = self.get(db, id)
        if not obj:
            return False
        
        # Soft delete if model supports it and hard_delete is False
        if hasattr(obj, "soft_delete") and not hard_delete:
            obj.soft_delete()
            db.commit()
        else:
            db.delete(obj)
            db.commit()
        
        return True
    
    def restore(self, db: Session, id: int) -> Optional[ModelType]:
        """Restore a soft-deleted record."""
        if not hasattr(self.model, "restore"):
            return None
        
        # Query including deleted records
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            return None
        
        obj.restore()
        db.commit()
        db.refresh(obj)
        return obj
    
    def get_deleted(self, db: Session, skip: int = 0, limit: int = 20) -> List[ModelType]:
        """Get soft-deleted records."""
        if not hasattr(self.model, "is_deleted"):
            return []
        
        return (
            db.query(self.model)
            .filter(self.model.is_deleted == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
'''
