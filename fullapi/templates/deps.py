"""Dependencies templates."""

DEPS_NO_AUTH = '''from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user():
    return None
'''

DEPS_WITH_AUTH = '''from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
'''
