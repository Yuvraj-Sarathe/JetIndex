"""MakeMyTrip scraper.

RECON NOTES:
MMT uses heavier anti-bot (Akamai). Strategy:
1. Use Playwright for token bootstrap (get cookies/headers)
2. Reuse cookies with curl_cffi for subsequent requests
3. Expect Playwright fallback to be needed more often than IndiGo

Before implementing, capture the XHR endpoint via DevTools:
1. Open https://www.makemytrip.com in Chrome
2. DevTools → Network → filter XHR/Fetch
3. Perform a one-way search
4. Find the fare response, copy as cURL
5. Document in scrapers/recon/makemytrip_endpoint.md
"""

from scrapers.base_scraper import BaseScraper, RequestSpec, ScrapeJob


class MakeMyTripScraper(BaseScraper):
    """MakeMyTrip fare scraper using curl_cffi with Playwright fallback."""

    source = "makemytrip"
    rate_limit_rps = 0.33  # 1 req / 3s

    # TODO: Fill in after recon
    # ENDPOINT_URL = "https://<discovered-endpoint>"
    # ENDPOINT_NOTES = "See scrapers/recon/makemytrip_endpoint.md"

    def build_request(self, job: ScrapeJob) -> RequestSpec:
        """Build the MakeMyTrip fare search request."""
        # TODO: Implement after endpoint discovery
        raise NotImplementedError("Owner: Sourabh/Abhay — fill in endpoint from recon")

    def parse_ok(self, response) -> bool:
        """Check if MakeMyTrip response contains valid fare data."""
        # TODO: Implement after endpoint discovery
        raise NotImplementedError("Owner: Sourabh/Abhay")
