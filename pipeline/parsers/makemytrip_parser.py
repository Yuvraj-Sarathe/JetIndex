"""MakeMyTrip raw JSON parser — converts scraper output to RawQuote list."""

from datetime import datetime, time

from loguru import logger

from pipeline.schemas import RawQuote


def parse(payload: dict, job_meta: dict) -> list[RawQuote]:
    """
    Parse MakeMyTrip raw API response into a list of RawQuote objects.
    """

    quotes: list[RawQuote] = []

    try:
        offers = payload.get("searchResult", {}).get("flightOffers", [])
    except AttributeError:
        logger.warning("Invalid MakeMyTrip payload")
        return quotes

    for item in offers:
        try:
            airline = item.get("airline", {})
            fare = item.get("fare", {})
            breakdown = dict(fare.get("breakdown", {}))

            departure = item.get("departure")

            depart_date = None
            depart_time = None

            if departure:
                dt = datetime.fromisoformat(
                    departure.replace("Z", "+00:00")
                )
                depart_date = dt.date()
                depart_time = dt.time()

            base_fare = breakdown.get("baseFare")
            total_fare = fare.get("totalFare")

            if base_fare is not None:
                has_base_fare = any(
                    "base" in str(label).lower()
                    or str(label).lower() in {"fare", "airfare"}
                    for label in breakdown
                )

                if not has_base_fare:
                    breakdown["Base Fare"] = float(base_fare)

            quote = RawQuote(
                source=job_meta.get("source", "makemytrip"),
                route_code=job_meta["route_code"],
                origin=job_meta["origin"],
                destination=job_meta["destination"],
                carrier=airline.get("code"),
                flight_no=item.get("flightNumber"),
                depart_date=depart_date,
                depart_time=depart_time,
                scrape_date=job_meta["scrape_date"],
                scraped_at=job_meta["scraped_at"],
                lead_time=job_meta["lead_time"],
                fare_class=item.get("fareClass"),
                stops=item.get("stops", 0),
                is_refundable=item.get("refundable"),
                currency=fare.get("currency", "INR"),
                total_fare=total_fare,
                fare_breakdown=breakdown,
                seats_left=item.get("seatsLeft"),
                sold_out=item.get("soldOut", False),
                raw_ref=job_meta.get("raw_ref", "makemytrip"),
            )

            quotes.append(quote)

        except (KeyError, TypeError, ValueError) as exc:
            logger.warning(
                f"Skipping invalid MakeMyTrip record: {exc}"
            )

    logger.info(
        f"MakeMyTrip parser: parsed {len(quotes)} quotes"
    )

    return quotes


def _parse_depart_time(dt_str: str | None) -> time | None:
    """Parse departure time string to time object."""

    if not dt_str:
        return None

    try:
        dt = datetime.fromisoformat(
            dt_str.replace("Z", "+00:00")
        )
        return dt.time()
    except (ValueError, TypeError):
        return None