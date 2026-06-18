"""Router templates with new architecture patterns."""

# routers/health.py - Simple health check (no database)
HEALTH_ROUTER_NO_DB = '''"""Health check router."""

from fastapi import APIRouter
from core.responses import StandardResponse, success_response
from core.config import settings

router = APIRouter()


@router.get(
    "/health",
    response_model=StandardResponse[dict],
    summary="Health check",
    description="Check application health status",
)
def health_check():
    """Check if the application is healthy."""
    health_data = {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }

    return success_response(
        data=health_data,
        message="Application is healthy",
    )


@router.get(
    "/",
    response_model=StandardResponse[dict],
    summary="Root endpoint",
)
def root():
    """Root endpoint with application information."""
    return success_response(
        data={
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "docs_url": "/docs" if settings.DEBUG else None,
        },
        message=f"Welcome to {settings.APP_NAME}",
    )
'''

# routers/health.py - Enhanced with StandardResponse and database check
HEALTH_ROUTER = '''"""Health check router with database connectivity check."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from dependencies.db import get_db
from core.responses import StandardResponse, success_response
from core.config import settings

router = APIRouter()


@router.get(
    "/health",
    response_model=StandardResponse[dict],
    summary="Health check",
    description="Check application and database health status",
)
def health_check(db: Session = Depends(get_db)):
    """Check if the application and database are healthy."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
        db_message = "Database connection successful"
    except Exception as e:
        db_status = "unhealthy"
        db_message = f"Database connection failed: {str(e)}"

    health_data = {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": {
            "status": db_status,
            "message": db_message,
        },
    }

    return success_response(
        data=health_data,
        message="Application is healthy" if db_status == "healthy" else "Database issues detected",
    )


@router.get(
    "/",
    response_model=StandardResponse[dict],
    summary="Root endpoint",
)
def root():
    """Root endpoint with application information."""
    return success_response(
        data={
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "docs_url": "/docs" if settings.DEBUG else None,
        },
        message=f"Welcome to {settings.APP_NAME}",
    )
'''

# routers/users.py - Full CRUD (no auth, open endpoints)
USERS_ROUTER_NO_AUTH = '''"""Users router with full CRUD operations."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from dependencies.db import get_db
from core.responses import StandardResponse, PaginatedResponse, success_response
from exceptions.errors import NotFoundError, ConflictError
from crud.user import UserCRUD
from schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()
user_crud = UserCRUD()


@router.post(
    "/",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """Create a new user account."""
    if user_crud.get_by_email(db, user_in.email):
        raise ConflictError(f"User with email \'{user_in.email}\' already exists")

    if user_crud.get_by_username(db, user_in.username):
        raise ConflictError(f"User with username \'{user_in.username}\' already exists")

    user = user_crud.create(db, obj_in=user_in.model_dump())

    return success_response(
        data=user,
        message="User created successfully",
    )


@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
    summary="List all users",
)
def list_users(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """Get a paginated list of all users."""
    users = user_crud.get_all(db, skip=skip, limit=limit)
    total = user_crud.count(db)

    return PaginatedResponse.create(
        data=users,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
    )


@router.get(
    "/{user_id}",
    response_model=StandardResponse[UserResponse],
    summary="Get user by ID",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific user by their ID."""
    user = user_crud.get(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    return success_response(
        data=user,
        message="User retrieved successfully",
    )


@router.patch(
    "/{user_id}",
    response_model=StandardResponse[UserResponse],
    summary="Update user",
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
):
    """Update a user\'s information."""
    user = user_crud.get(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    updated_user = user_crud.update(db, db_obj=user, obj_in=user_in.model_dump(exclude_unset=True))

    return success_response(
        data=updated_user,
        message="User updated successfully",
    )


@router.delete(
    "/{user_id}",
    response_model=StandardResponse,
    summary="Delete user",
    description="Soft delete a user",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Soft delete a user account."""
    user = user_crud.get(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    user_crud.delete(db, user_id)

    return success_response(
        message="User deleted successfully",
    )
'''

# routers/users.py - Full CRUD with auth
USERS_ROUTER = '''"""Users router with full CRUD operations."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from dependencies.db import get_db
from dependencies.auth import get_current_user
from core.responses import StandardResponse, PaginatedResponse, success_response
from exceptions.errors import NotFoundError, ConflictError, ForbiddenError
from crud.user import UserCRUD
from schemas.user import UserCreate, UserUpdate, UserResponse
from models.user import User

router = APIRouter()
user_crud = UserCRUD()


@router.post(
    "/",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """Create a new user account."""
    if user_crud.get_by_email(db, user_in.email):
        raise ConflictError(f"User with email \'{user_in.email}\' already exists")

    if user_crud.get_by_username(db, user_in.username):
        raise ConflictError(f"User with username \'{user_in.username}\' already exists")

    user = user_crud.create(db, obj_in=user_in.model_dump())

    return success_response(
        data=user,
        message="User created successfully",
    )


@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
    summary="List all users",
    description="Get a paginated list of users (requires authentication)",
)
def list_users(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a paginated list of all users."""
    users = user_crud.get_all(db, skip=skip, limit=limit)
    total = user_crud.count(db)

    return PaginatedResponse.create(
        data=users,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
    )


@router.get(
    "/me",
    response_model=StandardResponse[UserResponse],
    summary="Get current user",
    description="Get the currently authenticated user\'s information",
)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get the current authenticated user\'s information."""
    return success_response(
        data=current_user,
        message="Current user retrieved successfully",
    )


@router.get(
    "/{user_id}",
    response_model=StandardResponse[UserResponse],
    summary="Get user by ID",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific user by their ID."""
    user = user_crud.get(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    return success_response(
        data=user,
        message="User retrieved successfully",
    )


@router.patch(
    "/{user_id}",
    response_model=StandardResponse[UserResponse],
    summary="Update user",
    description="Update user information (own profile only, unless admin)",
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user\'s information."""
    user = user_crud.get(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    if current_user.id != user_id and current_user.role != "admin":
        raise ForbiddenError("You can only update your own profile")

    updated_user = user_crud.update(db, db_obj=user, obj_in=user_in.model_dump(exclude_unset=True))

    return success_response(
        data=updated_user,
        message="User updated successfully",
    )


@router.delete(
    "/{user_id}",
    response_model=StandardResponse,
    summary="Delete user",
    description="Soft delete a user (own account only, unless admin)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a user account."""
    user = user_crud.get(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    if current_user.id != user_id and current_user.role != "admin":
        raise ForbiddenError("You can only delete your own account")

    user_crud.delete(db, user_id)

    return success_response(
        message="User deleted successfully",
    )
'''

# routers/auth.py - Authentication endpoints
AUTH_ROUTER = '''"""Authentication router with login, register, and token refresh."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from dependencies.db import get_db
from dependencies.auth import get_current_user
from core.responses import StandardResponse, success_response
from core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from core.config import settings
from exceptions.errors import UnauthorizedError, ConflictError
from crud.user import UserCRUD
from schemas.auth import TokenResponse, TokenRefresh
from schemas.user import UserCreate, UserResponse
from models.user import User

router = APIRouter()
user_crud = UserCRUD()


@router.post(
    "/login",
    response_model=StandardResponse[TokenResponse],
    summary="Login with email/username and password",
    description="Authenticate user and return access and refresh tokens",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user and return JWT tokens."""
    user = user_crud.get_by_email(db, form_data.username)
    if not user:
        user = user_crud.get_by_username(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedError("Incorrect email/username or password")

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return success_response(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        ),
        message="Login successful",
    )


@router.post(
    "/register",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account",
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user account."""
    if user_crud.get_by_email(db, user_in.email):
        raise ConflictError(f"User with email \'{user_in.email}\' already exists")

    if user_crud.get_by_username(db, user_in.username):
        raise ConflictError(f"User with username \'{user_in.username}\' already exists")

    user = user_crud.create(db, obj_in=user_in.model_dump())

    return success_response(
        data=user,
        message="User registered successfully",
    )


@router.post(
    "/refresh",
    response_model=StandardResponse[TokenResponse],
    summary="Refresh access token",
    description="Use refresh token to get a new access token",
)
def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
):
    """Refresh an expired access token using a refresh token."""
    payload = verify_token(token_data.refresh_token)
    if not payload:
        raise UnauthorizedError("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")

    user = user_crud.get(db, int(user_id))
    if not user:
        raise UnauthorizedError("User no longer exists")

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return success_response(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        ),
        message="Token refreshed successfully",
    )


@router.post(
    "/logout",
    response_model=StandardResponse,
    summary="Logout",
    description="Logout current user (client should discard tokens)",
)
def logout(
    current_user: User = Depends(get_current_user),
):
    """Logout the current user. JWT tokens are stateless — discard tokens client-side."""
    return success_response(
        message="Logout successful. Please discard your tokens.",
    )
'''

# routers/redis.py - Redis management endpoints
REDIS_ROUTER = '''"""Redis management router."""

from fastapi import APIRouter, Depends
from dependencies.cache import get_redis_client, get_cache_manager
from core.responses import StandardResponse, success_response
from core.redis_utils import CacheManager
from exceptions.errors import ServiceUnavailableError
import redis

router = APIRouter()


@router.get(
    "/health",
    response_model=StandardResponse[dict],
    summary="Redis health check",
    description="Check if Redis is connected and responsive",
)
def redis_health(
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """Check Redis connection health."""
    try:
        redis_client.ping()
        info = redis_client.info()
        health_data = {
            "status": "healthy",
            "version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
            "uptime_in_seconds": info.get("uptime_in_seconds"),
        }
        return success_response(
            data=health_data,
            message="Redis is healthy",
        )
    except Exception as e:
        raise ServiceUnavailableError(f"Redis health check failed: {str(e)}")


@router.delete(
    "/cache/{prefix}",
    response_model=StandardResponse,
    summary="Clear cache by prefix",
    description="Delete all cache entries with the specified prefix",
)
def clear_cache(
    prefix: str,
    cache: CacheManager = Depends(get_cache_manager),
):
    """Clear all cache entries with a specific prefix."""
    count = cache.clear(prefix)
    return success_response(
        message=f"Cleared {count} cache entries with prefix \'{prefix}\'",
    )


@router.get(
    "/cache/stats",
    response_model=StandardResponse[dict],
    summary="Cache statistics",
    description="Get Redis cache statistics",
)
def cache_stats(
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """Get Redis cache statistics."""
    info = redis_client.info()
    hits = info.get("keyspace_hits", 0)
    misses = info.get("keyspace_misses", 0)
    total = hits + misses
    stats = {
        "keyspace_hits": hits,
        "keyspace_misses": misses,
        "hit_rate_percent": round(hits / total * 100, 2) if total > 0 else 0,
        "used_memory_human": info.get("used_memory_human"),
        "total_connections_received": info.get("total_connections_received"),
        "total_commands_processed": info.get("total_commands_processed"),
    }
    return success_response(
        data=stats,
        message="Cache statistics retrieved successfully",
    )
'''
