"""Schema templates."""

BASE_SCHEMA = '''from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
'''

USER_SCHEMA = '''from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
'''
