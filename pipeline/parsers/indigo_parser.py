"""IndiGo raw JSON parser — converts scraper output to RawQuote list."""

from datetime import time

from loguru import logger

from pipeline.schemas import RawQuote


def parse(payload: list[dict], job_meta: dict) -> list[RawQuote]:
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

    quotes: list[RawQuote] = []
    for item in payload:
        try:
            fare_breakdown = dict(item.get("fare_breakdown", {}))

            if item.get("base_fare") is not None:
                has_base_fare = any(
                    "base" in str(label).lower() or str(label).lower() in {"fare", "airfare"}
                    for label in fare_breakdown
                )

                if not has_base_fare:
                    fare_breakdown["Base Fare"] = float(item["base_fare"])

            quote = RawQuote(
                source=item["source"],
                route_code=item["route_code"],
                origin=item["origin"],
                destination=item["destination"],
                carrier=item["carrier"],
                flight_no=item["flight_no"],
                depart_date=item["depart_date"],
                depart_time=_parse_depart_time(item.get("depart_time")),
                scrape_date=item.get("scrape_date") or job_meta.get("scrape_date"),
                scraped_at=item["scraped_at"],
                lead_time=item["lead_time"],
                fare_class=item.get("fare_class"),
                stops=item.get("stops", 0),
                is_refundable=item.get("is_refundable"),
                currency=item.get("currency", "INR"),
                total_fare=item["total_fare"],
                fare_breakdown=fare_breakdown,
                seats_left=item.get("seats_left"),
                sold_out=item.get("sold_out", False),
                raw_ref=job_meta.get("raw_ref", "indigo"),
            )

            quotes.append(quote)

        except (KeyError, TypeError, ValueError) as exc:
            logger.warning(f"Skipping invalid IndiGo record: {exc}")

    logger.info(f"IndiGo parser: parsed {len(quotes)} quotes")

    return quotes


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
