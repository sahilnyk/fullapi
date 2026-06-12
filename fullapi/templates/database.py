"""Database session template."""

DB_BASE = '''from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
'''

DB_SESSION_SQLITE = '''from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL or "sqlite:///./app.db",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Verify DB connection on startup. Called from main.py lifespan."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.critical(f"Database connection failed: {e}")
        raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

DB_SESSION_POSTGRESQL_MYSQL = '''from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=settings.DB_POOL_TIMEOUT,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.critical(f"Database connection failed: {e}")
        raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
