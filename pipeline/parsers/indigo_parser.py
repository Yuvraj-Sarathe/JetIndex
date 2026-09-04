"""IndiGo raw JSON parser — converts scraper output to RawQuote list."""

from datetime import time

from loguru import logger

from pipeline.schemas import RawQuote


def parse(payload: dict, job_meta: dict) -> list[RawQuote]:
    """
    Parse IndiGo raw API response into a list of RawQuote objects.

    Args:
        payload: Raw JSON response from IndiGo API
        job_meta: Metadata about the scrape job (source, route, dates, etc.)

    Returns:
        List of RawQuote objects, one per flight × fare family.
    """
    # TODO: Implement after endpoint recon
    # Expected IndiGo response structure (varies by endpoint):
    # {
    #   "data": {
    #     "flights": [
    #       {
    #         "flightNumber": "6E-123",
    #         "carrier": "6E",
    #         "departure": "2025-01-15T06:30",
    #         "arrival": "2025-01-15T08:45",
    #         "fareFamilies": [
    #           {
    #             "name": "Saver",
    #             "totalFare": 4200,
    #             "baseFare": 3500,
    #             "taxes": 500,
    #             "fees": 200,
    #             "refundable": false,
    #             "seatsLeft": 5
    #           }
    #         ]
    #       }
    #     ]
    #   }
    # }

    logger.warning("IndiGo parser not yet implemented — returning empty list")
    return []


def _parse_depart_time(dt_str: str | None) -> time | None:
    """Parse departure time string to time object."""
    if not dt_str:
        return None
    try:
        # Handle various formats
        for _fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p"):
            try:
                return time.fromisoformat(dt_str)
            except ValueError:
                continue
    except Exception:
        pass
    return None
