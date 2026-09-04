"""Tests for db/ package — model creation."""

import pytest

# Skip these tests if psycopg is not installed (local dev without Docker)
pytest.importorskip("psycopg")

from db.models import ApixDaily, DgcaBenchmark, DgcaWeight, FareQuote, RawQuote, Route  # noqa: E402


def test_models_import():
    """All models should be importable."""
    assert Route is not None
    assert RawQuote is not None
    assert FareQuote is not None
    assert ApixDaily is not None
    assert DgcaWeight is not None
    assert DgcaBenchmark is not None


def test_models_table_names():
    """Models should have correct table names."""
    assert Route.__tablename__ == "routes"
    assert RawQuote.__tablename__ == "raw_quotes"
    assert FareQuote.__tablename__ == "fare_quotes"
    assert ApixDaily.__tablename__ == "apix_daily"
    assert DgcaWeight.__tablename__ == "dgca_weights"
    assert DgcaBenchmark.__tablename__ == "dgca_benchmark"
