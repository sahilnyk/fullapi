"""Response wrapper templates for standardized API responses."""

# core/responses.py
RESPONSES = '''"""Standardized API response wrappers."""

from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Optional, Any, List
from datetime import datetime

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """Standard response wrapper for all API endpoints."""
    
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": None,
                "message": "Operation completed successfully",
                "timestamp": "2024-01-01T00:00:00",
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper for list endpoints."""
    
    success: bool = True
    data: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def create(
        cls,
        data: List[T],
        total: int,
        page: int,
        per_page: int,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response with calculated total pages."""
        total_pages = (total + per_page - 1) // per_page
        return cls(
            data=data,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )


def success_response(
    data: Optional[Any] = None,
    message: Optional[str] = None,
) -> StandardResponse:
    """Create a successful response."""
    return StandardResponse(
        success=True,
        data=data,
        message=message,
    )


def error_response(
    message: str,
    error_code: Optional[str] = None,
    error_details: Optional[dict] = None,
) -> StandardResponse:
    """Create an error response."""
    error = {"message": message}
    if error_code:
        error["code"] = error_code
    if error_details:
        error["details"] = error_details
    
    return StandardResponse(
        success=False,
        error=error,
        message=message,
    )
'''
