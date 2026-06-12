"""Dependency injection templates for the new dependencies package structure."""

# dependencies/__init__.py
DEPENDENCIES_INIT = '''"""Dependency injection package for FastAPI."""

from .db import get_db
from .auth import get_current_user, require_role, oauth2_scheme
from .cache import get_redis_client, get_cache_manager

__all__ = [
    "get_db",
    "get_current_user",
    "require_role",
    "oauth2_scheme",
    "get_redis_client",
    "get_cache_manager",
]
'''

# dependencies/__init__.py (no auth)
DEPENDENCIES_INIT_NO_AUTH = '''"""Dependency injection package for FastAPI."""

from .db import get_db

__all__ = ["get_db"]
'''

# dependencies/__init__.py (with auth, no redis)
DEPENDENCIES_INIT_AUTH_ONLY = '''"""Dependency injection package for FastAPI."""

from .db import get_db
from .auth import get_current_user, require_role, oauth2_scheme

__all__ = [
    "get_db",
    "get_current_user",
    "require_role",
    "oauth2_scheme",
]
'''

# dependencies/__init__.py (no auth, with redis)
DEPENDENCIES_INIT_REDIS_ONLY = '''"""Dependency injection package for FastAPI."""

from .db import get_db
from .cache import get_redis_client, get_cache_manager

__all__ = [
    "get_db",
    "get_redis_client",
    "get_cache_manager",
]
'''

# dependencies/db.py
DEPENDENCIES_DB = '''"""Database session dependency."""

from typing import Generator
from sqlalchemy.orm import Session
from db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency.
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

# dependencies/auth.py
DEPENDENCIES_AUTH = '''"""Authentication dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.security import verify_token
from crud.user import user_crud
from dependencies.db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Get the currently authenticated user.
    
    Usage:
        @router.get("/me")
        def get_current_user_info(user=Depends(get_current_user)):
            return user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = user_crud.get(db, int(user_id))
    if user is None:
        raise credentials_exception
    
    return user


def require_role(role: str):
    """Dependency factory for role-based access control.
    
    Usage:
        @router.delete("/users/{id}")
        def delete_user(
            user=Depends(require_role("admin"))
        ):
            # Only admins can delete users
            pass
    """
    def role_checker(current_user=Depends(get_current_user)):
        if not hasattr(current_user, "role"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User model does not have role attribute",
            )
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {role} role",
            )
        return current_user
    
    return role_checker
'''

# dependencies/cache.py
DEPENDENCIES_CACHE = '''"""Redis cache dependencies."""

from typing import Optional
from fastapi import HTTPException, status
from core.redis_config import redis_client
from core.redis_utils import CacheManager


def get_redis_client():
    """Get Redis client dependency.
    
    Usage:
        @router.get("/cache/health")
        def check_cache(redis=Depends(get_redis_client)):
            return redis.ping()
    """
    try:
        client = redis_client.client
        if not redis_client.is_connected():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis is not available",
            )
        return client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis connection failed: {str(e)}",
        )


def get_cache_manager(prefix: str = "app") -> CacheManager:
    """Get cache manager dependency.
    
    Usage:
        @router.get("/items/{id}")
        def get_item(id: int, cache=Depends(get_cache_manager)):
            cached = cache.get(f"item:{id}")
            if cached:
                return cached
            # ... fetch from DB
    """
    return CacheManager(prefix)
'''
