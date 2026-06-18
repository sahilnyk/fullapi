"""Database mixin templates for common model patterns."""

# db/mixins.py
DB_MIXINS = '''"""Database mixins for common model patterns."""

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.sql import func
from typing import Optional


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns.
    
    Usage:
        class User(Base, TimestampMixin):
            __tablename__ = "users"
            # ... other columns
    """
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin that adds soft delete functionality instead of hard deletion.
    
    Usage:
        class User(Base, SoftDeleteMixin):
            __tablename__ = "users"
            # ... other columns
    
    Soft deleted records are marked with is_deleted=True and deleted_at timestamp
    instead of being removed from the database.
    """
    
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        """Mark this record as deleted."""
        from datetime import datetime, timezone
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
'''
