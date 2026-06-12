"""SQLAlchemy model templates."""

USER_MODEL = '''from sqlalchemy import Column, Integer, String, Boolean
from db.base import Base
from db.mixins import TimestampMixin, SoftDeleteMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(String, default="user", nullable=False)
'''
