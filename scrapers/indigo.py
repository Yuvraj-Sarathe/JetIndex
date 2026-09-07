"""IndiGo Airlines scraper.

RECON NOTES:
Captured XHR endpoint: https://api-prod-flight-skyplus6e.goindigo.in/v2/flight/search
See details in scrapers/recon/indigo_endpoint.md
"""

import os
from typing import Any

from scrapers.base_scraper import BaseScraper, RequestSpec, ScrapeJob


class IndigoScraper(BaseScraper):
    """IndiGo fare scraper using curl_cffi with Playwright fallback."""

    source = "indigo"
    rate_limit_rps = 0.33  # 1 req / 3s

    ENDPOINT_URL = "https://api-prod-flight-skyplus6e.goindigo.in/v2/flight/search"
    USER_KEY = os.getenv("INDIGO_USER_KEY", "31e90be8fff2f5e2eea242c225f21b1a")

    def build_request(self, job: ScrapeJob) -> RequestSpec:
        """Build the IndiGo fare search request."""
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://www.goindigo.in",
            "pragma": "no-cache",
            "referer": "https://www.goindigo.in/",
            "user_key": self.USER_KEY,  # os.getenv("INDIGO_USER_KEY")
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }

        if self.session_manager and hasattr(self.session_manager, "get_token"):
            token = self.session_manager.get_token(self.source)
            if token:
                headers["authorization"] = f"Bearer {token}" if not token.startswith("Bearer ") else token

        json_body = {
            "codes": {
                "currency": "INR",
                "promotionCode": "",
            },
            "criteria": [
                {
                    "dates": {
                        "beginDate": job.depart_date.isoformat(),
                    },
                    "flightFilters": {
                        "type": "All",
                    },
                    "stations": {
                        "originStationCodes": [job.origin],
                        "destinationStationCodes": [job.destination],
                    },
                }
            ],
            "passengers": {
                "residentCountry": "IN",
                "types": [
                    {
                        "count": 1,
                        "discountCode": "",
                        "type": "ADT",
                    }
                ],
            },
            "taxesAndFees": "TaxesAndFees",
            "tripCriteria": "oneWay",
            "isRedeemTransaction": False,
        }

        return RequestSpec(
            url=self.ENDPOINT_URL,
            method="POST",
            headers=headers,
            json_body=json_body,
        )

    def parse_ok(self, response: Any) -> bool:
        """Check if IndiGo response contains valid fare data."""
        if response is None:
            return False

        if hasattr(response, "status_code") and response.status_code != 200:
            return False

        payload = response.json() if hasattr(response, "json") and callable(response.json) else response

        if isinstance(payload, list):
            return len(payload) > 0 and any(
                isinstance(item, dict) and ("total_fare" in item or "flight_no" in item or "carrier" in item)
                for item in payload
            )

        if isinstance(payload, dict):
            if payload.get("errors") or payload.get("error"):
                return False

            if any(k in payload for k in ("trips", "flightFilter", "flights", "fares", "codes", "data")):
                return True

        return False
