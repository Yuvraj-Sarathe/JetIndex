"""Tests for scrapers/ package — base scraper and registry."""

from datetime import date

from scrapers.base_scraper import ScrapeJob, ScrapeResult


def test_scrape_job_creation():
    """ScrapeJob should be creatable with required fields."""
    job = ScrapeJob(
        source="indigo",
        origin="DEL",
        destination="BOM",
        depart_date=date(2026, 10, 20),
        lead_time=7,
        scrape_date=date(2026, 10, 13),
    )
    assert job.source == "indigo"
    assert job.lead_time == 7


def test_scrape_result_creation():
    """ScrapeResult should be creatable with required fields."""
    job = ScrapeJob(
        source="indigo",
        origin="DEL",
        destination="BOM",
        depart_date=date(2026, 10, 20),
        lead_time=7,
        scrape_date=date(2026, 10, 13),
    )
    result = ScrapeResult(job=job, ok=True, status_code=200)
    assert result.ok is True
    assert result.status_code == 200


def test_registry_has_indigo():
    """Registry should include indigo scraper."""
    from scrapers.registry import SCRAPERS

    assert "indigo" in SCRAPERS


def test_registry_has_makemytrip():
    """Registry should include makemytrip scraper."""
    from scrapers.registry import SCRAPERS

    assert "makemytrip" in SCRAPERS
