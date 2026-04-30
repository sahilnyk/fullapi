"""Database session template."""

DB_SESSION = '''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import get_settings

settings = get_settings()

# Database URL based on config
if "${db_type}" == "sqlite":
    DATABASE_URL = settings.DATABASE_URL or "sqlite:///./app.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
