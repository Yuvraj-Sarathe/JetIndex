"""Tests for scrapers/storage.py — save_raw disk and DB write."""

from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scrapers.base_scraper import ScrapeJob, ScrapeResult
from scrapers.storage import save_raw


def test_save_raw_writes_disk_and_inserts_db(tmp_path):
    job = ScrapeJob(
        source="indigo",
        origin="DEL",
        destination="BOM",
        scrape_date=date(2026, 10, 13),
        depart_date=date(2026, 10, 20),
        lead_time=7,
    )
    result = ScrapeResult(
        job=job,
        ok=True,
        payload={"flights": [{"flight_no": "6E-101", "fare": 5000}]},
        fetched_at=datetime(2026, 10, 13, 10, 0, 0),
        status_code=200,
        method="curl_cffi",
    )

    mock_route = MagicMock()
    mock_route.id = 42

    mock_session = MagicMock()
    mock_session_ctx = MagicMock()
    mock_session_ctx.__enter__.return_value = mock_session
    mock_session_ctx.__exit__.return_value = None

    with (
        patch("scrapers.storage.settings.RAW_DATA_DIR", str(tmp_path)),
        patch("db.session.SessionLocal", return_value=mock_session_ctx),
        patch("db.queries.get_route_by_code", return_value=mock_route) as mock_get_route,
        patch("db.queries.insert_raw_quote") as mock_insert,
    ):
        saved_path = save_raw(result)

        assert saved_path.exists()
        assert result.raw_path == str(saved_path)

        mock_get_route.assert_called_once_with(mock_session, "DEL-BOM")
        mock_insert.assert_called_once()
        inserted_record = mock_insert.call_args[0][1]
        assert inserted_record["source"] == "indigo"
        assert inserted_record["route_id"] == 42
        assert inserted_record["lead_time"] == 7
        assert inserted_record["status_code"] == 200


def test_save_raw_db_failure_does_not_crash(tmp_path):
    job = ScrapeJob(
        source="indigo",
        origin="DEL",
        destination="BOM",
        scrape_date=date(2026, 10, 13),
        depart_date=date(2026, 10, 20),
        lead_time=7,
    )
    result = ScrapeResult(
        job=job,
        ok=True,
        payload={"data": "test"},
        fetched_at=datetime(2026, 10, 13, 10, 0, 0),
        status_code=200,
        method="curl_cffi",
    )

    with (
        patch("scrapers.storage.settings.RAW_DATA_DIR", str(tmp_path)),
        patch("db.session.SessionLocal", side_effect=Exception("DB connection refused")),
    ):
        # Operational outage should not crash disk save
        saved_path = save_raw(result)
        assert saved_path.exists()


def test_save_raw_missing_route_raises_value_error(tmp_path):
    job = ScrapeJob(
        source="indigo",
        origin="UNKNOWN",
        destination="ROUTE",
        scrape_date=date(2026, 10, 13),
        depart_date=date(2026, 10, 20),
        lead_time=7,
    )
    result = ScrapeResult(
        job=job,
        ok=True,
        payload={"data": "test"},
        fetched_at=datetime(2026, 10, 13, 10, 0, 0),
        status_code=200,
        method="curl_cffi",
    )

    mock_session = MagicMock()
    mock_session_ctx = MagicMock()
    mock_session_ctx.__enter__.return_value = mock_session
    mock_session_ctx.__exit__.return_value = None

    with (
        patch("scrapers.storage.settings.RAW_DATA_DIR", str(tmp_path)),
        patch("db.session.SessionLocal", return_value=mock_session_ctx),
        patch("db.queries.get_route_by_code", return_value=None),
    ):
        with pytest.raises(ValueError, match="UNKNOWN-ROUTE"):
            save_raw(result)

        # Confirm the file was still saved to disk before raising
        assert result.raw_path is not None
        assert Path(result.raw_path).exists()
