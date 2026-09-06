"""Shared dependencies for API routes."""

from collections.abc import AsyncGenerator

from sqlalchemy.orm import Session

from db.session import SessionLocal


async def get_db() -> AsyncGenerator[Session, None]:
    """Yield a database session, closing it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
