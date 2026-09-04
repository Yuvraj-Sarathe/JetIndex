"""MakeMyTrip raw JSON parser — converts scraper output to RawQuote list."""

from loguru import logger

from pipeline.schemas import RawQuote


def parse(payload: dict, job_meta: dict) -> list[RawQuote]:
    """
    Parse MakeMyTrip raw API response into a list of RawQuote objects.

    Args:
        payload: Raw JSON response from MakeMyTrip API
        job_meta: Metadata about the scrape job (source, route, dates, etc.)

    Returns:
        List of RawQuote objects, one per flight × fare family.
    """
    # TODO: Implement after endpoint recon
    # Expected MakeMyTrip response structure (varies by endpoint):
    # {
    #   "searchResult": {
    #     "flightOffers": [
    #       {
    #         "airline": {"code": "6E", "name": "IndiGo"},
    #         "flightNumber": "6E-123",
    #         "departure": "2025-01-15T06:30",
    #         "arrival": "2025-01-15T08:45",
    #         "fare": {
    #           "totalFare": 4500,
    #           "breakdown": {
    #             "baseFare": 3600,
    #             "taxes": 550,
    #             "convenienceFee": 350
    #           }
    #         },
    #         "refundable": false,
    #         "seatsLeft": 3
    #       }
    #     ]
    #   }
    # }

    logger.warning("MakeMyTrip parser not yet implemented — returning empty list")
    return []
