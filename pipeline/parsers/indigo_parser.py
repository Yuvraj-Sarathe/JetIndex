"""IndiGo raw JSON parser — converts scraper output to RawQuote list."""

from datetime import date, time

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
    # Resolve default scrape_date from job_meta
    meta_scrape_date: date | None = None
    if isinstance(job_meta, dict) and job_meta.get("scrape_date"):
        raw_meta_date = job_meta["scrape_date"]
        if isinstance(raw_meta_date, str):
            try:
                meta_scrape_date = date.fromisoformat(raw_meta_date)
            except ValueError:
                meta_scrape_date = None
        elif isinstance(raw_meta_date, date):
            meta_scrape_date = raw_meta_date

    # Reject early if scrape_date is missing in job_meta and required by payload
    if meta_scrape_date is None:
        has_records_without_date = any(isinstance(item, dict) and not item.get("scrape_date") for item in payload)
        if has_records_without_date:
            raise ValueError(
                "job_meta['scrape_date'] is required and must be a valid date when payload records omit 'scrape_date'"
            )

    quotes: list[RawQuote] = []
    for item in payload:
        try:
            item_scrape_date = item.get("scrape_date")
            if isinstance(item_scrape_date, str):
                try:
                    record_scrape_date = date.fromisoformat(item_scrape_date)
                except ValueError:
                    record_scrape_date = meta_scrape_date
            elif isinstance(item_scrape_date, date):
                record_scrape_date = item_scrape_date
            else:
                record_scrape_date = meta_scrape_date

            if record_scrape_date is None:
                logger.warning(f"Skipping IndiGo record without valid scrape_date: flight_no={item.get('flight_no')}")
                continue

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
                scrape_date=record_scrape_date,
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
                raw_ref=job_meta.get("raw_ref", "indigo") if isinstance(job_meta, dict) else "indigo",
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
