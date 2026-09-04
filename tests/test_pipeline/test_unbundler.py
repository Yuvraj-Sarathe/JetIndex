"""Tests for pipeline/ package — unbundler and validators."""

from datetime import date, datetime

from pipeline.schemas import RawQuote
from pipeline.unbundler import unbundle
from pipeline.validators import validate_raw


def test_validate_raw_valid():
    """Valid raw quote should pass validation."""
    quote = RawQuote(
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
        total_fare=4500.0,
        fare_breakdown={"Base Fare": 4500.0},
        raw_ref="test.json",
    )
    result = validate_raw(quote)
    assert result is not None
    assert result.flight_no == "6E-123"


def test_validate_raw_negative_fare():
    """Quote with negative fare should be rejected."""
    quote = RawQuote(
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
        total_fare=-100.0,
        fare_breakdown={},
        raw_ref="test.json",
    )
    result = validate_raw(quote)
    assert result is None


def test_unbundle_basic():
    """Unbundle should map vendor labels to canonical components."""
    quote = RawQuote(
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
        total_fare=4500.0,
        fare_breakdown={
            "Base Fare": 3500.0,
            "UDF": 500.0,
            "GST": 300.0,
            "Convenience Fee": 200.0,
        },
        raw_ref="test.json",
    )
    clean = unbundle(quote)
    assert clean.base_fare == 3500.0
    assert clean.udf == 500.0
    assert clean.taxes == 300.0
    assert clean.convenience_fee == 200.0
    assert clean.total_fare == 4500.0
