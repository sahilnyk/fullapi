"""Schema templates."""

BASE_SCHEMA = '''from pydantic import BaseModel


class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}
'''

USER_SCHEMA = '''from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
'''
