"""Database session template."""

DB_SESSION = '''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import get_settings

settings = get_settings()

# Database URL based on config
if "${db_type}" == "sqlite":
    DATABASE_URL = settings.DATABASE_URL or "sqlite:///./app.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    DATABASE_URL = settings.DATABASE_URL
    # Connection pooling for production
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,          # Number of connections to keep open
        max_overflow=10,       # Max connections beyond pool_size
        pool_pre_ping=True,    # Verify connections before using
        pool_recycle=3600      # Recycle connections after 1 hour
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
