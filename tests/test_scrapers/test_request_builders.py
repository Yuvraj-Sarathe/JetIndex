"""Unit tests for IndiGo and MakeMyTrip request builders and response validators."""

import json
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scrapers.base_scraper import ScrapeJob
from scrapers.indigo import IndigoScraper
from scrapers.makemytrip import MakeMyTripScraper

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def sample_scrape_job() -> ScrapeJob:
    return ScrapeJob(
        source="indigo",
        origin="DEL",
        destination="BOM",
        depart_date=date(2026, 10, 13),
        lead_time=7,
        scrape_date=date(2026, 10, 6),
    )


@pytest.fixture
def mmt_scrape_job() -> ScrapeJob:
    return ScrapeJob(
        source="makemytrip",
        origin="DEL",
        destination="BOM",
        depart_date=date(2026, 10, 13),
        lead_time=7,
        scrape_date=date(2026, 10, 6),
    )


# ==============================================================================
# IndiGo Scraper Tests
# ==============================================================================


def test_indigo_build_request(sample_scrape_job, monkeypatch):
    monkeypatch.setenv("INDIGO_USER_KEY", "test_indigo_user_key_456")
    scraper = IndigoScraper()
    req = scraper.build_request(sample_scrape_job)

    assert req.method == "POST"
    assert req.url == "https://api-prod-flight-skyplus6e.goindigo.in/v2/flight/search"
    assert req.headers["content-type"] == "application/json"
    assert req.headers["user_key"] == "test_indigo_user_key_456"
    assert "origin" in req.headers
    assert "referer" in req.headers

    body = req.json_body
    assert body is not None
    assert body["codes"]["currency"] == "INR"
    assert body["tripCriteria"] == "oneWay"
    assert body["criteria"][0]["dates"]["beginDate"] == "2026-10-13"
    assert body["criteria"][0]["stations"]["originStationCodes"] == ["DEL"]
    assert body["criteria"][0]["stations"]["destinationStationCodes"] == ["BOM"]
    assert body["passengers"]["types"][0]["count"] == 1


def test_indigo_build_request_with_session_manager(sample_scrape_job, monkeypatch):
    monkeypatch.setenv("INDIGO_USER_KEY", "test_indigo_user_key_456")
    session_mgr = MagicMock()
    session_mgr.get_token.return_value = "mock_jwt_token_123"

    scraper = IndigoScraper(session_manager=session_mgr)
    req = scraper.build_request(sample_scrape_job)

    assert req.headers["authorization"] == "Bearer mock_jwt_token_123"
    assert req.headers["user_key"] == "test_indigo_user_key_456"


def test_indigo_build_request_missing_user_key_raises_error(sample_scrape_job, monkeypatch):
    monkeypatch.delenv("INDIGO_USER_KEY", raising=False)
    scraper = IndigoScraper(user_key="")
    scraper.USER_KEY = ""
    with pytest.raises(ValueError, match="INDIGO_USER_KEY"):
        scraper.build_request(sample_scrape_job)


def test_indigo_parse_ok_with_fixture():
    fixture_path = FIXTURES_DIR / "indigo_sample.json"
    assert fixture_path.exists(), "Indigo fixture file not found"

    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)

    scraper = IndigoScraper()
    assert scraper.parse_ok(data) is True


def test_indigo_parse_ok_with_dict_payloads():
    scraper = IndigoScraper()

    valid_dict = {"codes": {"currency": "INR"}, "trips": [{"flightFilter": {}}]}
    assert scraper.parse_ok(valid_dict) is True

    valid_data_dict = {"data": {"flights": [{"flight_no": "6E-101"}]}}
    assert scraper.parse_ok(valid_data_dict) is True

    # Error payload
    error_dict = {"errors": [{"code": "FLIGHT_NOT_FOUND", "message": "No flights"}]}
    assert scraper.parse_ok(error_dict) is False

    # None and empty
    assert scraper.parse_ok(None) is False
    assert scraper.parse_ok({}) is False
    assert scraper.parse_ok([]) is False


def test_indigo_parse_ok_with_response_object():
    scraper = IndigoScraper()

    resp_mock = MagicMock()
    resp_mock.status_code = 200
    resp_mock.json.return_value = {"trips": []}
    assert scraper.parse_ok(resp_mock) is True

    resp_error = MagicMock()
    resp_error.status_code = 403
    assert scraper.parse_ok(resp_error) is False


# ==============================================================================
# MakeMyTrip Scraper Tests
# ==============================================================================


def test_makemytrip_build_request(mmt_scrape_job):
    scraper = MakeMyTripScraper()
    req = scraper.build_request(mmt_scrape_job)

    assert req.method == "POST"
    assert req.url == "https://flights.makemytrip.com/makemytrip/flight/search"
    assert req.headers["content-type"] == "application/json"
    assert "makemytrip.com" in req.headers["origin"]

    body = req.json_body
    assert body is not None
    assert body["tripType"] == "OW"
    assert body["itinerary"][0]["from"] == "DEL"
    assert body["itinerary"][0]["to"] == "BOM"
    assert body["itinerary"][0]["departureDate"] == "2026-10-13"
    assert body["paxInfo"]["adults"] == 1
    assert body["cabinClass"] == "E"


def test_makemytrip_build_request_with_session_manager(mmt_scrape_job):
    session_mgr = MagicMock()
    session_mgr.get_token.return_value = "mock_mmt_token_456"

    scraper = MakeMyTripScraper(session_manager=session_mgr)
    req = scraper.build_request(mmt_scrape_job)

    assert req.headers["authorization"] == "Bearer mock_mmt_token_456"


def test_makemytrip_parse_ok_with_fixture():
    fixture_path = FIXTURES_DIR / "makemytrip_sample.json"
    assert fixture_path.exists(), "MMT fixture file not found"

    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)

    scraper = MakeMyTripScraper()
    assert scraper.parse_ok(data) is True


def test_makemytrip_parse_ok_with_dict_payloads():
    scraper = MakeMyTripScraper()

    valid_dict = {
        "searchResult": {
            "flightOffers": [
                {
                    "airline": {"code": "6E", "name": "IndiGo"},
                    "flightNumber": "6E-2054",
                    "fare": {"totalFare": 4500},
                }
            ]
        }
    }
    assert scraper.parse_ok(valid_dict) is True

    # Error payload
    error_dict = {"error": "Access Denied / Bot Detected"}
    assert scraper.parse_ok(error_dict) is False

    # None and empty
    assert scraper.parse_ok(None) is False
    assert scraper.parse_ok({}) is False
    assert scraper.parse_ok([]) is False


def test_makemytrip_parse_ok_with_response_object():
    scraper = MakeMyTripScraper()

    resp_mock = MagicMock()
    resp_mock.status_code = 200
    resp_mock.json.return_value = {"searchResult": {"flightOffers": []}}
    assert scraper.parse_ok(resp_mock) is True

    resp_error = MagicMock()
    resp_error.status_code = 500
    assert scraper.parse_ok(resp_error) is False
