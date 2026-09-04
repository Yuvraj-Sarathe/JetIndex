"""Database session and engine configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# Base class for models (must be defined before engine)
class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""

    pass


# SQLAlchemy engine (lazy — only connects when used)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
