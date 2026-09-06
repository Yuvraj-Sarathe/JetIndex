"""Unit tests for IndiGo raw JSON parser and scrape_date validation."""

from datetime import date, datetime

import pytest

from pipeline.parsers.indigo_parser import parse


@pytest.fixture
def valid_record():
    return {
        "source": "indigo",
        "route_code": "DEL-BOM",
        "origin": "DEL",
        "destination": "BOM",
        "carrier": "6E",
        "flight_no": "6E-101",
        "depart_date": "2026-10-13",
        "depart_time": "06:30",
        "scraped_at": datetime(2026, 10, 6, 2, 0, 0).isoformat(),
        "lead_time": 7,
        "total_fare": 4500.0,
        "base_fare": 3800.0,
        "fare_breakdown": {"Taxes": 700.0},
    }


def test_indigo_parse_with_job_meta_date(valid_record):
    job_meta = {
        "source": "indigo",
        "raw_ref": "data/raw/test.json",
        "scrape_date": date(2026, 10, 6),
    }
    quotes = parse([valid_record], job_meta)
    assert len(quotes) == 1
    assert quotes[0].scrape_date == date(2026, 10, 6)
    assert quotes[0].total_fare == 4500.0
    assert quotes[0].fare_breakdown["Base Fare"] == 3800.0


def test_indigo_parse_with_job_meta_iso_string(valid_record):
    job_meta = {
        "source": "indigo",
        "raw_ref": "data/raw/test.json",
        "scrape_date": "2026-10-06",
    }
    quotes = parse([valid_record], job_meta)
    assert len(quotes) == 1
    assert quotes[0].scrape_date == date(2026, 10, 6)


def test_indigo_parse_with_record_scrape_date_override(valid_record):
    valid_record["scrape_date"] = "2026-10-05"
    job_meta = {
        "source": "indigo",
        "raw_ref": "data/raw/test.json",
        "scrape_date": date(2026, 10, 6),
    }
    quotes = parse([valid_record], job_meta)
    assert len(quotes) == 1
    assert quotes[0].scrape_date == date(2026, 10, 5)


def test_indigo_parse_missing_scrape_date_raises_value_error(valid_record):
    """When records lack scrape_date and job_meta lacks scrape_date, raise ValueError."""
    job_meta = {
        "source": "indigo",
        "raw_ref": "data/raw/test.json",
    }
    with pytest.raises(ValueError, match="job_meta\\['scrape_date'\\] is required"):
        parse([valid_record], job_meta)


def test_indigo_parse_empty_payload_without_scrape_date():
    """Empty payload returns empty list without requiring scrape_date."""
    quotes = parse([], {})
    assert quotes == []
