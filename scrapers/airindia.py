"""Air India scraper.

RECON NOTES:
Real endpoint: https://api.airindia.com/cbiz-booking/v2/prime/search/air-calendar
Requires JWT Bearer token from guest session.
Akamai bot protection — Playwright fallback needed for token acquisition.
See details in scrapers/recon/airindia_endpoint.md
"""

import os
from typing import Any

from loguru import logger

from scrapers.base_scraper import BaseScraper, RequestSpec, ScrapeJob


class AirIndiaScraper(BaseScraper):
    """Air India fare scraper using curl_cffi with Playwright fallback."""

    source = "airindia"
    rate_limit_rps = 0.33  # 1 req / 3s

    ENDPOINT_URL = "https://api.airindia.com/cbiz-booking/v2/prime/search/air-calendar"
    SESSION_URL = "https://api.airindia.com/cbiz-booking/v2/guest/session"

    def __init__(self, proxy_manager=None, session_manager=None):
        super().__init__(proxy_manager=proxy_manager, session_manager=session_manager)
        self._jwt_token: str | None = None

    def _get_jwt_token(self) -> str:
        """Get or refresh JWT token from AirIndia guest session."""
        # Check session manager first
        if self.session_manager:
            session_data = self.session_manager.get_or_refresh(self.source)
            if session_data and "jwt_token" in session_data:
                self._jwt_token = session_data["jwt_token"]
                return self._jwt_token

        # Check environment variable
        env_token = os.getenv("AIRINDIA_JWT_TOKEN", "")
        if env_token:
            self._jwt_token = env_token
            return self._jwt_token

        # Try to fetch fresh token from guest session endpoint
        try:
            import curl_cffi.requests as cffi_requests

            from scrapers.fingerprints import random_fingerprint

            fp = random_fingerprint()
            resp = cffi_requests.post(
                self.SESSION_URL,
                headers={
                    "accept": "application/json",
                    "content-type": "application/json",
                    "origin": "https://www.airindia.com",
                    "referer": "https://www.airindia.com/",
                    "user-agent": fp["user_agent"],
                    "originCountryCode": "IN",
                },
                json={
                    "clientId": "web-pb",
                    "countryCode": "IN",
                    "currencyCode": "INR",
                    "customerType": "GUEST",
                },
                timeout=10,
                impersonate=fp["impersonate"],
            )
            if resp.status_code == 200:
                data = resp.json()
                self._jwt_token = data.get("token") or data.get("jwtToken") or data.get("accessToken")
                if self._jwt_token:
                    logger.info("AirIndia: Fresh JWT token acquired")
                    if self.session_manager:
                        self.session_manager.save(self.source, {"jwt_token": self._jwt_token})
                    return self._jwt_token
        except Exception as e:
            logger.warning(f"AirIndia: Failed to fetch JWT token: {e}")

        raise ValueError(
            "AirIndia JWT token not available. Set AIRINDIA_JWT_TOKEN env var "
            "or ensure session manager has a valid token."
        )

    def build_request(self, job: ScrapeJob) -> RequestSpec:
        """Build the Air India fare search request."""
        jwt_token = self._get_jwt_token()

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://www.airindia.com",
            "referer": "https://www.airindia.com/",
            "authorization": f"Bearer {jwt_token}",
            "originCountryCode": "IN",
            "user-agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }

        json_body = {
            "cabin": "ECONOMY",
            "itineraries": [
                {
                    "departureDateTime": job.depart_date.isoformat(),
                    "originLocationCode": job.origin.lower(),
                    "destinationLocationCode": job.destination.lower(),
                    "isRequestedBound": True,
                    "flexibility": 0,
                }
            ],
            "searchPreferences": {
                "showUnavailableEntries": True,
            },
            "travelers": [
                {"passengerTypeCode": "ADT"}
            ],
        }

        return RequestSpec(
            url=self.ENDPOINT_URL,
            method="POST",
            headers=headers,
            json_body=json_body,
        )

    def parse_ok(self, response: Any) -> bool:
        """Check if Air India response contains valid fare data."""
        if response is None:
            return False

        if hasattr(response, "status_code") and response.status_code != 200:
            return False

        payload = (
            response.json()
            if hasattr(response, "json") and callable(response.json)
            else response
        )

        if isinstance(payload, dict):
            if payload.get("error") or payload.get("errors"):
                return False

            # AirIndia returns flight offers in various structures
            if any(
                k in payload
                for k in (
                    "flightOffers",
                    "flights",
                    "journeys",
                    "data",
                    "results",
                    "itineraries",
                )
            ):
                return True

        if isinstance(payload, list):
            return len(payload) > 0 and any(
                isinstance(item, dict)
                and any(
                    k in item
                    for k in ("totalFare", "total_fare", "price", "fare")
                )
                for item in payload
            )

        return False
