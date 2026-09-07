"""Pipeline loader — bulk-upsert fare quotes into the database."""

from loguru import logger


def load(df):
    """Load fare quotes from a DataFrame into the database.

    Resolves route_code → route_id via the routes table, strips columns
    that don't exist on FareQuote, and inserts via raw SQL.

    Returns the number of rows inserted.
    """
    if df.is_empty():
        logger.info("Nothing to load — empty DataFrame")
        return 0

    from datetime import datetime

    from sqlalchemy import text

    from db.queries import get_route_by_code
    from db.session import SessionLocal

    records = df.to_dicts()
    session = SessionLocal()
    try:
        # Cache route lookups to avoid N+1 queries
        route_cache = {}
        count = 0

        # Prepare insert SQL — use DEFAULT for id to let PostgreSQL auto-generate
        insert_sql = text("""
            INSERT INTO fare_quotes
                (route_id, carrier, flight_no, depart_date, depart_time,
                 lead_time, fare_class, base_fare, udf, taxes, convenience_fee,
                 other_fees, total_fare, currency, is_refundable, stops, source,
                 scraped_at, raw_quote_id, quality_flag)
            VALUES
                (:route_id, :carrier, :flight_no, :depart_date, :depart_time,
                 :lead_time, :fare_class, :base_fare, :udf, :taxes, :convenience_fee,
                 :other_fees, :total_fare, :currency, :is_refundable, :stops, :source,
                 :scraped_at, :raw_quote_id, :quality_flag)
        """)

        for rec in records:
            route_code = rec.get("route_code")
            if route_code not in route_cache:
                route = get_route_by_code(session, route_code) if route_code else None
                route_cache[route_code] = route.id if route else None

            route_id = route_cache[route_code]
            if route_id is None:
                logger.warning(f"Route not found in DB: {route_code!r} — skipping record")
                continue

            # Convert depart_time (time) to datetime by combining with depart_date
            depart_time = rec.get("depart_time")
            depart_date = rec.get("depart_date")
            if depart_time and depart_date:
                depart_time = datetime.combine(depart_date, depart_time)

            params = {
                "route_id": route_id,
                "carrier": rec.get("carrier"),
                "flight_no": rec.get("flight_no"),
                "depart_date": depart_date,
                "depart_time": depart_time,
                "lead_time": rec.get("lead_time"),
                "fare_class": rec.get("fare_class"),
                "base_fare": rec.get("base_fare"),
                "udf": rec.get("udf", 0),
                "taxes": rec.get("taxes", 0),
                "convenience_fee": rec.get("convenience_fee", 0),
                "other_fees": rec.get("other_fees", 0),
                "total_fare": rec.get("total_fare"),
                "currency": rec.get("currency", "INR"),
                "is_refundable": rec.get("is_refundable"),
                "stops": rec.get("stops", 0),
                "source": rec.get("source"),
                "scraped_at": rec.get("scraped_at"),
                "raw_quote_id": rec.get("raw_quote_id"),
                "quality_flag": rec.get("quality_flag", "ok"),
            }

            session.execute(insert_sql, params)
            count += 1

        session.commit()
        logger.info(f"Loaded {count} fare quotes into database")
        return count
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to load fare quotes: {e}")
        raise
    finally:
        session.close()
