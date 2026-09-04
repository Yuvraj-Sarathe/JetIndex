"""Shared test fixtures for all test modules."""

import json
from datetime import date, datetime
from pathlib import Path

import pytest

from pipeline.schemas import CleanQuote, RawQuote


@pytest.fixture
def sample_raw_quote():
    """Sample RawQuote for testing."""
    return RawQuote(
        source="indigo",
        route_code="DEL-BOM",
        origin="DEL",
        destination="BOM",
        carrier="6E",
        flight_no="6E-123",
        depart_date=date(2025, 1, 15),
        scrape_date=date(2025, 1, 8),
        scraped_at=datetime(2025, 1, 8, 2, 0, 0),
        lead_time=7,
        fare_class="Saver",
        total_fare=4500.0,
        fare_breakdown={
            "Base Fare": 3500.0,
            "UDF": 500.0,
            "GST": 300.0,
            "Convenience Fee": 200.0,
        },
        raw_ref="data/raw/indigo/2025-01-08/DEL-BOM_T7.json",
    )


@pytest.fixture
def sample_clean_quote():
    """Sample CleanQuote for testing."""
    return CleanQuote(
        route_code="DEL-BOM",
        origin="DEL",
        destination="BOM",
        carrier="6E",
        flight_no="6E-123",
        depart_date=date(2025, 1, 15),
        scrape_date=date(2025, 1, 8),
        scraped_at=datetime(2025, 1, 8, 2, 0, 0),
        lead_time=7,
        fare_class="Saver",
        base_fare=3500.0,
        udf=500.0,
        taxes=300.0,
        convenience_fee=200.0,
        other_fees=0.0,
        total_fare=4500.0,
        source="indigo",
        raw_ref="data/raw/indigo/2025-01-08/DEL-BOM_T7.json",
    )


@pytest.fixture
def sample_indigo_fixture():
    """Load indigo_sample.json test fixture."""
    fixture_path = Path("tests/fixtures/indigo_sample.json")
    if fixture_path.exists():
        with open(fixture_path) as f:
            return json.load(f)
    return {}


@pytest.fixture
def sample_makemytrip_fixture():
    """Load makemytrip_sample.json test fixture."""
    fixture_path = Path("tests/fixtures/makemytrip_sample.json")
    if fixture_path.exists():
        with open(fixture_path) as f:
            return json.load(f)
    return {}
