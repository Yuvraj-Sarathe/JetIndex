"""Pipeline loader — bulk-upsert fare quotes into the database."""

from loguru import logger


def load(df):
    """Load fare quotes from a DataFrame into the database.

    Resolves route_code → route_id via the routes table, strips columns
    that don't exist on FareQuote, and bulk-upserts via ON CONFLICT DO UPDATE.

    Returns the number of rows inserted/updated.
    """
    if df.is_empty():
        logger.info("Nothing to load — empty DataFrame")
        return 0

    from db.queries import get_route_by_code, upsert_fare_quotes
    from db.session import SessionLocal

    records = df.to_dicts()
    session = SessionLocal()
    try:
        # Cache route lookups to avoid N+1 queries
        route_cache: dict[str, int | None] = {}
        for rec in records:
            route_code = rec.get("route_code")
            if route_code not in route_cache:
                route = get_route_by_code(session, route_code) if route_code else None
                route_cache[route_code] = route.id if route else None

            route_id = route_cache[route_code]
            if route_id is None:
                logger.warning(f"Route not found in DB: {route_code!r} — skipping record")
                continue

            rec["route_id"] = route_id

            # Strip CleanQuote-only columns that don't exist on FareQuote
            for col in ("route_code", "scrape_date", "origin", "destination", "raw_ref"):
                rec.pop(col, None)

            # RawQuote FK is nullable; we don't have it from the pipeline path
            rec.setdefault("raw_quote_id", None)

        # Drop any records where route_id couldn't be resolved
        records = [r for r in records if "route_id" in r]

        if not records:
            logger.warning("No valid records to load (all routes unresolved)")
            return 0

        count = upsert_fare_quotes(session, records)
        return count
    finally:
        session.close()
