"""Main application with middleware support."""

from fastapi import FastAPI
from core.middleware_config import get_middleware_config
from core.middleware_setup import setup_middleware
from routers.health import router as health_router
from routers.users import router as users_router


def create_app() -> FastAPI:
    """Create FastAPI application with middleware."""
    app = FastAPI(
        title="FastAPI Project",
        description="FastAPI project with middleware support"
    )
    
    # Setup middleware
    config = get_middleware_config()
    setup_middleware(app, config)
    
    # Include routers
    app.include_router(health_router, tags=["health"])
    app.include_router(users_router, tags=["users"])
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
