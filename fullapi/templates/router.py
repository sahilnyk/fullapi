"""Router templates."""

HEALTH_ROUTER = '''from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health check")
def health_check():
    return {"status": "ok"}
'''

USERS_ROUTER = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from schemas.user import UserCreate, UserResponse
from crud.user import create_user, get_user, get_users
from db.session import get_db
from deps import get_current_user

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get("/users/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)

@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
'''
