"""MakeMyTrip scraper.

RECON NOTES:
Real endpoint: https://flights-cb.makemytrip.com/api/postSearch
Requires x-flt Base64 header + rkeys from initial search.
Akamai bot protection — Playwright fallback often needed.
See details in scrapers/recon/makemytrip_endpoint.md
"""

import base64
import json
import uuid
from datetime import datetime
from typing import Any

from scrapers.base_scraper import BaseScraper, RequestSpec, ScrapeJob


class MakeMyTripScraper(BaseScraper):
    """MakeMyTrip fare scraper using curl_cffi with Playwright fallback."""

    source = "makemytrip"
    rate_limit_rps = 0.33  # 1 req / 3s

    # Real API endpoint (postSearch requires rkeys from initial search)
    ENDPOINT_URL = "https://flights-cb.makemytrip.com/api/postSearch"
    CR_ID = "f22d4102-dbca-4611-9f79-08fbfe782a56"

    def _build_x_flt_header(self, origin: str, destination: str, depart_date: str) -> str:
        """Build the x-flt Base64 header with search metadata."""
        payload = {
            "c": "E",  # cabin class
            "p": "A-1_C-0_I-0",  # pax
            "t": "",
            "s": f"{origin}-{destination}-{depart_date.replace('-', '')}",
            "ItineraryId": f"{origin}-{destination}-06/{depart_date.replace('-', '/')}",
            "TripType": "O",
            "PaxType": "A-1_C-0_I-0",
            "Intl": False,
            "CabinClass": "E",
            "Ccd": "in",
            "Pft": "",
            "Pfs": "",
            "ForwardFlowRequired": True,
            "CmpId": "",
        }
        return base64.b64encode(json.dumps(payload).encode()).decode()

    def build_request(self, job: ScrapeJob) -> RequestSpec:
        """Build the MakeMyTrip fare search request."""
        depart_date_str = job.depart_date.strftime("%Y%m%d")
        depart_date_iso = job.depart_date.isoformat()
        it_str = f"{job.origin}-{job.destination}-{depart_date_str}"

        device_id = str(uuid.uuid4())
        api_call_ts = int(datetime.now().timestamp() * 1000)

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://www.makemytrip.com",
            "referer": "https://www.makemytrip.com/",
            "user-agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "x-flt": self._build_x_flt_header(job.origin, job.destination, depart_date_iso),
            "os": "Mac OS",
            "domain": "in",
            "mcid": device_id,
            "src": "mmt",
            "device-id": device_id,
            "profile-type": "PERSONAL",
            "app-ver": "1.0.0",
            "pfm": "DESKTOP",
            "region": "in",
            "currency": "INR",
            "language": "eng",
            "entity-name": "india",
            "user-country": "IN",
            "User-Currency": "INR",
        }

        json_body = {
            "pax": "A-1_C-0_I-0",
            "cc": "E",
            "src": "",
            "crId": self.CR_ID,
            "pfm": "DESKTOP",
            "cur": "INR",
            "shd": True,
            "isGrpBkg": False,
            "dfs": 0,
            "it": it_str,
            "sortBy": "rhino",
            "apiCallTimestamp": api_call_ts,
            "creditShellInfo": "",
            "forwardFlowRequired": True,
            "rkeys": [],  # Empty on first call — Playwright needed for initial search
        }

        url = f"{self.ENDPOINT_URL}?crId={self.CR_ID}&region=in&currency=INR&language=eng&cmpId="

        return RequestSpec(
            url=url,
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
