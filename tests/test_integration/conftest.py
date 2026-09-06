"""Fixtures for integration tests — SQLite in-memory DB (no PostgreSQL needed).

These tests import db.models directly, which triggers db.session engine creation.
If psycopg is not installed locally, tests are skipped automatically.
Run inside Docker: pytest -m integration
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from db.models import Base

    _DB_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _DB_AVAILABLE = False


@pytest.fixture()
def db_session():
    """Create an in-memory SQLite database with full schema, yield a session, tear down."""
    if not _DB_AVAILABLE:
        pytest.skip("Database modules not available (psycopg not installed)")

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()
    engine.dispose()
