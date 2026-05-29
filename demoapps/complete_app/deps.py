from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
