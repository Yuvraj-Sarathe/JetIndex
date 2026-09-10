"""Scraper registry — maps source names to scraper classes."""

from __future__ import annotations

from datetime import date

from scrapers.airindia import AirIndiaScraper
from scrapers.base_scraper import BaseScraper, ScrapeJob
from scrapers.indigo import IndigoScraper
from scrapers.makemytrip import MakeMyTripScraper

# Registry of all implemented scrapers
SCRAPERS: dict[str, type[BaseScraper]] = {
    "indigo": IndigoScraper,
    "makemytrip": MakeMyTripScraper,
    "airindia": AirIndiaScraper,
    # "google_flights": GoogleFlightsScraper,  # Async — run via google_flights.py directly
    # "akasa": AkasaScraper,       # Post-MVP: not yet implemented
    # "easemytrip": EaseMyTripScraper,  # Post-MVP: not yet implemented
}


def get_scraper(name: str) -> BaseScraper:
    """Get a scraper instance by source name."""
    if name not in SCRAPERS:
        raise ValueError(f"Unknown scraper source: {name}. Available: {list(SCRAPERS.keys())}")
    return SCRAPERS[name]()


def build_jobs_for_date(scrape_date: date | None = None) -> list[ScrapeJob]:
    """
    Build all scrape jobs for a given date from config/routes.yaml.

    Returns a flat list: 6 routes × 5 lead times × N enabled sources.
    """
    from datetime import date, timedelta

    import yaml

    if scrape_date is None:
        scrape_date = date.today()

    # Load routes config
    with open("config/routes.yaml") as f:
        config = yaml.safe_load(f)

    # Load sources config
    with open("config/sources.yaml") as f:
        sources_config = yaml.safe_load(f)

    enabled_sources = [name for name, cfg in sources_config.get("sources", {}).items() if cfg.get("enabled", False)]

    jobs = []
    for route in config.get("routes", []):
        origin = route["origin"]
        destination = route["destination"]
        for lead_time in route.get("lead_times", [1, 7, 15, 30, 45]):
            depart_date = scrape_date + timedelta(days=lead_time)
            for source in enabled_sources:
                jobs.append(
                    ScrapeJob(
                        source=source,
                        origin=origin,
                        destination=destination,
                        depart_date=depart_date,
                        lead_time=lead_time,
                        scrape_date=scrape_date,
                    )
                )

    return jobs
