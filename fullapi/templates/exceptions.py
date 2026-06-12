"""Exception templates for structured error handling."""

# exceptions/__init__.py
EXCEPTIONS_INIT = '''"""Custom exceptions for the application."""

from .errors import (
    AppException,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    ValidationError,
    ServiceUnavailableError,
)

__all__ = [
    "AppException",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "ValidationError",
    "ServiceUnavailableError",
]
'''

# exceptions/errors.py
EXCEPTIONS_ERRORS = '''"""Custom exception classes for structured error handling."""

from fastapi import HTTPException
from typing import Any, Optional


class AppException(HTTPException):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or self.__class__.__name__.upper()


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            status_code=404,
            detail=f"{resource} with id '{resource_id}' not found",
            error_code="NOT_FOUND",
        )


class UnauthorizedError(AppException):
    """Raised when authentication fails or is missing."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=401,
            detail=message,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(AppException):
    """Raised when user lacks permission for the action."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            status_code=403,
            detail=message,
            error_code="FORBIDDEN",
        )


class ConflictError(AppException):
    """Raised when there's a resource conflict (e.g., duplicate email)."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=409,
            detail=message,
            error_code="CONFLICT",
        )


class ValidationError(AppException):
    """Raised for custom validation errors beyond Pydantic's built-in validation."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        detail = f"{field}: {message}" if field else message
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


class ServiceUnavailableError(AppException):
    """Raised when an external service is unavailable."""
    
    def __init__(self, service: str = "Service"):
        super().__init__(
            status_code=503,
            detail=f"{service} is currently unavailable",
            error_code="SERVICE_UNAVAILABLE",
        )
'''

# exceptions/handlers.py
EXCEPTIONS_HANDLERS = '''"""Exception handlers for FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from .errors import AppException
import logging

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers with the FastAPI app."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle custom application exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail,
                },
            },
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": errors,
                },
            },
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors (unique constraints, etc.)."""
        logger.error(f"Database integrity error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_INTEGRITY_ERROR",
                    "message": "A resource with this data already exists",
                },
            },
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError):
        """Handle general database errors."""
        logger.error(f"Database error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "An unexpected database error occurred",
                },
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                },
            },
        )
'''
