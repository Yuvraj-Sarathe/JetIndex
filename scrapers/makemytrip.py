"""MakeMyTrip scraper.

RECON NOTES:
Captured XHR endpoint: https://flights.makemytrip.com/makemytrip/flight/search
See details in scrapers/recon/makemytrip_endpoint.md
"""

from typing import Any

from scrapers.base_scraper import BaseScraper, RequestSpec, ScrapeJob


class MakeMyTripScraper(BaseScraper):
    """MakeMyTrip fare scraper using curl_cffi with Playwright fallback."""

    source = "makemytrip"
    rate_limit_rps = 0.33  # 1 req / 3s

    ENDPOINT_URL = "https://flights.makemytrip.com/makemytrip/flight/search"

    def build_request(self, job: ScrapeJob) -> RequestSpec:
        """Build the MakeMyTrip fare search request."""
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://www.makemytrip.com",
            "referer": "https://www.makemytrip.com/flight/search",
            "user-agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }

        if self.session_manager and hasattr(self.session_manager, "get_token"):
            token = self.session_manager.get_token(self.source)
            if token:
                headers["authorization"] = f"Bearer {token}" if not token.startswith("Bearer ") else token

        json_body = {
            "tripType": "OW",
            "itinerary": [
                {
                    "from": job.origin,
                    "to": job.destination,
                    "departureDate": job.depart_date.isoformat(),
                }
            ],
            "paxInfo": {
                "adults": 1,
                "children": 0,
                "infants": 0,
            },
            "cabinClass": "E",
        }

        return RequestSpec(
            url=self.ENDPOINT_URL,
            method="POST",
            headers=headers,
            json_body=json_body,
        )

    def parse_ok(self, response: Any) -> bool:
        """Check if MakeMyTrip response contains valid fare data."""
        if response is None:
            return False

        if hasattr(response, "status_code") and response.status_code != 200:
            return False

        payload = response.json() if hasattr(response, "json") and callable(response.json) else response

        if isinstance(payload, list):
            return len(payload) > 0 and any(
                isinstance(item, dict)
                and (
                    "total_fare" in item
                    or "flight_no" in item
                    or "flightNumber" in item
                    or "carrier" in item
                    or "airline" in item
                )
                for item in payload
            )

        if isinstance(payload, dict):
            if payload.get("error") or payload.get("errors"):
                return False

            if "searchResult" in payload:
                sr = payload["searchResult"]
                if isinstance(sr, dict) and "flightOffers" in sr:
                    return len(sr["flightOffers"]) > 0 or isinstance(sr["flightOffers"], list)
                return True

            if any(k in payload for k in ("flightOffers", "flights", "journeys", "data", "results")):
                return True

        return False
