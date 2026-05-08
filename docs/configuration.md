# Configuration Options

## Mode Selection

### Basic Mode

Minimal structure for small APIs or learning FastAPI.

Generated files:
- `main.py` - Application entry point
- `routers/health.py` - Health check endpoint
- `schemas/base.py` - Base Pydantic schema
- `core/config.py` - Configuration settings
- `requirements.txt` - Dependencies

### Full Mode

Production-ready structure with all components.

Additional files in full mode:
- `models/user.py` - SQLAlchemy user model
- `schemas/user.py` - User Pydantic schemas
- `crud/user.py` - Database operations
- `routers/users.py` - User endpoints
- `db/session.py` - Database connection
- `deps.py` - Dependency injection
- `tests/test_main.py` - Test placeholder

## Database Options

### None
No database configuration. Suitable for simple APIs that don't need persistence.

### SQLite
Embedded database, good for development and small applications.
- File-based, no server required
- Zero configuration
- Single-user only

### PostgreSQL
Production-grade relational database.
- Concurrent connections
- Advanced features (JSON, arrays, etc.)
- Industry standard for web applications

### MySQL
Popular open-source database.
- Widely supported
- Good performance
- Common in shared hosting environments

## Authentication

### None
No authentication system. All endpoints are public.

### JWT
JSON Web Token authentication using OAuth2.

Features included:
- Password hashing with bcrypt
- Token creation and verification
- OAuth2 password flow
- Protected route dependency

To use authentication in your routes:

```python
from fastapi import Depends, APIRouter
from deps import get_current_user

router = APIRouter()

@router.get("/protected")
def protected_route(user = Depends(get_current_user)):
    return {"message": f"Hello {user}"}
```

## Docker Support

When enabled, generates:

### Dockerfile
- Python 3.11 slim base image
- Installs dependencies
- Runs uvicorn

### docker-compose.yml
- App service configuration
- PostgreSQL database service (if selected)
- Volume persistence
- Environment variable support

To use Docker:

```bash
docker-compose up --build
```

Your API will be available at `http://localhost:8000`
