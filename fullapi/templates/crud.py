"""CRUD operation templates."""

USER_CRUD = '''from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from crud.base import BaseCRUD
from models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD(BaseCRUD[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(
            User.username == username,
            User.is_deleted == False
        ).first()

    def create(self, db: Session, obj_in: Dict[str, Any]) -> User:
        if "password" in obj_in and "hashed_password" not in obj_in:
            obj_in["hashed_password"] = pwd_context.hash(obj_in.pop("password"))
        return super().create(db, obj_in)


user_crud = UserCRUD()
'''
