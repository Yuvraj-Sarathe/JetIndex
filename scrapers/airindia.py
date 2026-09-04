"""Air India scraper — stub, to be implemented after MVP."""

from scrapers.base_scraper import BaseScraper, RequestSpec, ScrapeJob


class AirIndiaScraper(BaseScraper):
    """Air India fare scraper — not yet implemented."""

    source = "airindia"
    rate_limit_rps = 0.33

    def build_request(self, job: ScrapeJob) -> RequestSpec:
        raise NotImplementedError("Owner: Sourabh/Abhay — post-MVP")

    def parse_ok(self, response) -> bool:
        raise NotImplementedError("Owner: Sourabh/Abhay — post-MVP")
