# Project Structure

## Basic Mode Structure

```
my_project/
├── main.py              # FastAPI application instance
├── routers/
│   └── health.py        # Health check endpoint
├── schemas/
│   └── base.py          # Base Pydantic models
├── core/
│   └── config.py        # Configuration management
└── requirements.txt     # Python dependencies
```

## Full Mode Structure

```
my_project/
├── main.py              # Application entry point with router imports
├── routers/
│   ├── __init__.py
│   ├── health.py        # Health check endpoint
│   └── users.py         # User CRUD endpoints (if DB selected)
├── models/
│   ├── __init__.py
│   └── user.py          # SQLAlchemy user model
├── schemas/
│   ├── __init__.py
│   ├── base.py          # Base Pydantic schema
│   └── user.py          # User schemas (create, response, update)
├── crud/
│   ├── __init__.py
│   └── user.py          # Database operations for users
├── core/
│   ├── __init__.py
│   ├── config.py        # Settings management with pydantic-settings
│   └── security.py      # JWT utilities (if --auth)
├── db/
│   ├── __init__.py
│   └── session.py       # Database engine and session (if --db)
├── tests/
│   └── test_main.py     # Test placeholder
├── deps.py              # FastAPI dependencies
├── .env.example         # Environment variable template
├── requirements.txt     # Dependencies
├── Dockerfile           # Container build (if --docker)
└── docker-compose.yml   # Container orchestration (if --docker)
```

## File Descriptions

### main.py
Application entry point. Creates FastAPI instance and includes routers.

### routers/
API endpoint definitions organized by resource.

### models/
SQLAlchemy ORM models defining database tables.

### schemas/
Pydantic models for request/response validation and serialization.

### crud/
Database Create, Read, Update, Delete operations.

### core/
Configuration and security utilities.

### db/
Database connection and session management.

### tests/
Test files. Uses pytest by convention.

### deps.py
FastAPI dependency injection definitions.

### .env.example
Template for environment variables. Copy to `.env` and customize.
