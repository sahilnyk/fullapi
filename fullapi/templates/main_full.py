"""Main.py template for full mode with all features."""

# main.py template - will be dynamically built based on config
MAIN_FULL_TEMPLATE = '''"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.config import settings
${IMPORTS_SECTION}

${SETUP_SECTION}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
${STARTUP_SECTION}
    yield
    # Shutdown
${SHUTDOWN_SECTION}

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

${MIDDLEWARE_SECTION}

${EXCEPTION_HANDLERS_SECTION}

# Include routers
${ROUTERS_SECTION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
'''

# Imports section templates
IMPORTS_LOGGING = "from core.logging import setup_logging, get_logger"
IMPORTS_MIDDLEWARE = "from core.middleware import setup_middleware"
IMPORTS_EXCEPTIONS = "from exceptions.handlers import register_exception_handlers"
IMPORTS_DB = "from db.session import init_db"
IMPORTS_REDIS = "from core.redis_config import redis_client"

IMPORTS_ROUTER_HEALTH = "from routers.health import router as health_router"
IMPORTS_ROUTER_USERS = "from routers.users import router as users_router"
IMPORTS_ROUTER_AUTH = "from routers.auth import router as auth_router"
IMPORTS_ROUTER_REDIS = "from routers.redis import router as redis_router"

# Setup section templates
SETUP_LOGGING = """# Setup logging
setup_logging()
logger = get_logger(__name__)"""

# Startup section templates
STARTUP_DB = """    # Initialize database connection
    init_db()
    print("Database connection established")"""

STARTUP_REDIS = """    # Initialize Redis connection
    redis_client.client
    logger.info("Redis connection established")"""

STARTUP_BASIC = """    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")"""

# Shutdown section templates
SHUTDOWN_REDIS = """    # Close Redis connection
    redis_client.disconnect()
    logger.info("Redis connection closed")"""

SHUTDOWN_BASIC = """    logger.info(f"Shutting down {settings.APP_NAME}")"""

# Middleware section template
MIDDLEWARE_SETUP = """# Setup middleware
setup_middleware(app)"""

# Exception handlers section template
EXCEPTION_HANDLERS_SETUP = """# Register exception handlers
register_exception_handlers(app)"""

# Router section templates
ROUTER_HEALTH = 'app.include_router(health_router, tags=["health"])'
ROUTER_USERS = 'app.include_router(users_router, prefix="/users", tags=["users"])'
ROUTER_AUTH = 'app.include_router(auth_router, prefix="/auth", tags=["auth"])'
ROUTER_REDIS = 'app.include_router(redis_router, prefix="/redis", tags=["redis"])'


def build_main_py(
    project_name: str,
    has_logging: bool = True,
    has_middleware: bool = True,
    has_exceptions: bool = True,
    has_database: bool = True,
    has_redis: bool = False,
    has_auth: bool = False,
) -> str:
    """Build main.py content based on configuration.
    
    Args:
        project_name: Name of the project
        has_logging: Include logging setup
        has_middleware: Include middleware setup
        has_exceptions: Include exception handlers
        has_database: Include database initialization
        has_redis: Include Redis setup
        has_auth: Include auth router
    
    Returns:
        Complete main.py content as string
    """
    # Build imports section
    imports = []
    if has_logging:
        imports.append(IMPORTS_LOGGING)
    if has_middleware:
        imports.append(IMPORTS_MIDDLEWARE)
    if has_exceptions:
        imports.append(IMPORTS_EXCEPTIONS)
    if has_database:
        imports.append(IMPORTS_DB)
    if has_redis:
        imports.append(IMPORTS_REDIS)
    
    # Always include routers
    imports.append("")  # Empty line before routers
    imports.append(IMPORTS_ROUTER_HEALTH)
    if has_database:
        imports.append(IMPORTS_ROUTER_USERS)
    if has_auth:
        imports.append(IMPORTS_ROUTER_AUTH)
    if has_redis:
        imports.append(IMPORTS_ROUTER_REDIS)
    
    imports_section = "\n".join(imports)
    
    # Build setup section
    setup_lines = []
    if has_logging:
        setup_lines.append(SETUP_LOGGING)
    setup_section = "\n\n".join(setup_lines) if setup_lines else "# No additional setup required"
    
    # Build startup section
    startup_lines = []
    if has_database:
        startup_lines.append(STARTUP_DB)
    if has_redis:
        startup_lines.append(STARTUP_REDIS)
    if has_logging:
        startup_lines.append(STARTUP_BASIC)
    else:
        startup_lines.append('    print(f"Starting {settings.APP_NAME}")')
    startup_section = "\n".join(startup_lines)
    
    # Build shutdown section
    shutdown_lines = []
    if has_redis:
        shutdown_lines.append(SHUTDOWN_REDIS)
    if has_logging:
        shutdown_lines.append(SHUTDOWN_BASIC)
    else:
        shutdown_lines.append('    print(f"Shutting down {settings.APP_NAME}")')
    shutdown_section = "\n".join(shutdown_lines)
    
    # Build middleware section
    middleware_section = MIDDLEWARE_SETUP if has_middleware else "# Middleware not configured"
    
    # Build exception handlers section
    exception_handlers_section = EXCEPTION_HANDLERS_SETUP if has_exceptions else "# Exception handlers not configured"
    
    # Build routers section
    routers = [ROUTER_HEALTH]
    if has_database:
        routers.append(ROUTER_USERS)
    if has_auth:
        routers.append(ROUTER_AUTH)
    if has_redis:
        routers.append(ROUTER_REDIS)
    routers_section = "\n".join(routers)
    
    # Build final main.py
    main_content = MAIN_FULL_TEMPLATE
    main_content = main_content.replace("${IMPORTS_SECTION}", imports_section)
    main_content = main_content.replace("${SETUP_SECTION}", setup_section)
    main_content = main_content.replace("${STARTUP_SECTION}", startup_section)
    main_content = main_content.replace("${SHUTDOWN_SECTION}", shutdown_section)
    main_content = main_content.replace("${MIDDLEWARE_SECTION}", middleware_section)
    main_content = main_content.replace("${EXCEPTION_HANDLERS_SECTION}", exception_handlers_section)
    main_content = main_content.replace("${ROUTERS_SECTION}", routers_section)
    
    return main_content
