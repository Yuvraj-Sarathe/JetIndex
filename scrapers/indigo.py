"""IndiGo Airlines scraper.

RECON NOTES:
Before implementing, capture the XHR endpoint via DevTools:
1. Open https://www.goindigo.in in Chrome
2. DevTools → Network → filter XHR/Fetch
3. Perform a one-way search (e.g., DEL → BOM)
4. Find the response containing fare data
5. Right-click → "Copy as cURL (bash)"
6. Paste the cURL command below and extract:
   - URL, method, required headers, body template
   - Auth/token flow (where tokens come from, TTL, refresh)
   - Response shape (fare array path, base/tax/fee fields, sold-out marker)
   - Anti-bot observations (Cloudflare/Akamai, challenge pages, rate limits)

Document findings in scrapers/recon/indigo_endpoint.md
"""

from scrapers.base_scraper import BaseScraper, RequestSpec, ScrapeJob


class IndigoScraper(BaseScraper):
    """IndiGo fare scraper using curl_cffi with Playwright fallback."""

    source = "indigo"
    rate_limit_rps = 0.33  # 1 req / 3s

    # TODO: Fill in after recon
    # ENDPOINT_URL = "https://<discovered-endpoint>"
    # ENDPOINT_NOTES = "See scrapers/recon/indigo_endpoint.md"

    def build_request(self, job: ScrapeJob) -> RequestSpec:
        """Build the IndiGo fare search request."""
        # TODO: Implement after endpoint discovery
        # return RequestSpec(
        #     url=self.ENDPOINT_URL,
        #     method="POST",
        #     headers={...},
        #     json_body={
        #         "origin": job.origin,
        #         "destination": job.destination,
        #         "departDate": job.depart_date.isoformat(),
        #         ...
        #     },
        # )
        raise NotImplementedError("Owner: Sourabh/Abhay — fill in endpoint from recon")

    def parse_ok(self, response) -> bool:
        """Check if IndiGo response contains valid fare data."""
        # TODO: Implement after endpoint discovery
        # return isinstance(response, dict) and "flights" in response
        raise NotImplementedError("Owner: Sourabh/Abhay")
