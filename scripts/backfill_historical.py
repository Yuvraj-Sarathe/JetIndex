"""Backfill fare_quotes with historical DGCA monthly average fares.

Reads config/dgca_monthly_avg_fare.csv (32 data points, 6 routes, 2024-2025),
inserts synthetic fare_quote rows, then runs compute_daily() for each month
to populate apix_daily. This enables run_backtest() to find overlapping months
between apix_daily and dgca_benchmark, producing real MAPE/RMSE/corr values.

Usage:
    docker compose exec api python scripts/backfill_historical.py
    python scripts/backfill_historical.py  (if DB is reachable locally)
"""

import csv
from datetime import date, datetime
from pathlib import Path

from loguru import logger


def backfill_fare_quotes(session) -> int:
    """Insert historical fare quotes from DGCA monthly average fares CSV."""
    from sqlalchemy import select

    from db.models import FareQuote, Route

    csv_path = Path("config/dgca_monthly_avg_fare.csv")
    if not csv_path.exists():
        logger.error(f"CSV not found: {csv_path}")
        return 0

    # Build route_code → route_id map
    route_map: dict[str, int] = {}
    for route in session.scalars(select(Route)).all():
        route_map[route.route_code] = route.id

    count = 0
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            route_code = row["route_code"]
            month_str = row["month"]  # "2024-03"
            avg_fare = float(row["avg_fare_inr"])

            route_id = route_map.get(route_code)
            if route_id is None:
                logger.warning(f"Route {route_code} not found in DB, skipping")
                continue

            # Parse month → 15th of that month as the representative date
            year, month = month_str.split("-")
            representative_date = date(int(year), int(month), 15)
            scraped_at = datetime(int(year), int(month), 15, 2, 0, 0)  # 02:00 IST sentinel

            # Check if already backfilled for this route+date
            existing = session.execute(
                select(FareQuote).where(
                    FareQuote.route_id == route_id,
                    FareQuote.source == "dgca_backfill",
                    FareQuote.depart_date == representative_date,
                )
            ).first()
            if existing:
                continue

            fq = FareQuote(
                route_id=route_id,
                carrier="DGCA",
                flight_no=None,
                depart_date=representative_date,
                lead_time=7,  # Must match the default query tuple (1,7,15,30,45)
                fare_class=None,
                base_fare=0.0,
                udf=0.0,
                taxes=0.0,
                convenience_fee=0.0,
                other_fees=0.0,
                total_fare=avg_fare,
                currency="INR",
                is_refundable=None,
                stops=0,
                source="dgca_backfill",
                scraped_at=scraped_at,
                raw_quote_id=None,
                quality_flag="ok",  # Must be 'ok' to pass get_median_fares_by_route filter
            )
            session.add(fq)
            count += 1

    session.commit()
    logger.info(f"Backfilled {count} historical fare quotes from DGCA data")
    return count


def compute_monthly_indices(session) -> int:
    """Run compute_daily() for each month that has backfilled data."""
    from sqlalchemy import text

    from engine.index_calculator import compute_daily

    # Get distinct months from backfilled data
    rows = session.execute(
        text("""
            SELECT DISTINCT date_trunc('month', scraped_at::date)::date AS month_start
            FROM fare_quotes
            WHERE source = 'dgca_backfill'
            ORDER BY month_start
        """)
    ).all()

    computed = 0
    for row in rows:
        month_start = row[0]
        # Use the 15th of each month as the compute date
        compute_date = date(month_start.year, month_start.month, 15)
        try:
            result = compute_daily(compute_date, session)
            if result["n_routes"] > 0:
                logger.info(
                    f"  {compute_date}: APIx={result['apix']:.4f} "
                    f"({result['n_quotes']} quotes, {result['n_routes']} routes)"
                )
                computed += 1
            else:
                logger.warning(f"  {compute_date}: no routes with prices")
        except Exception as e:
            logger.error(f"  {compute_date}: failed — {e}")

    logger.info(f"Computed {computed}/{len(rows)} monthly indices")
    return computed


def main():
    """Run the full backfill: insert historical data → compute indices."""
    from db.session import SessionLocal

    logger.info("=== Historical Backfill ===")
    logger.info("Step 1: Inserting historical fare quotes from DGCA data")

    session = SessionLocal()
    try:
        n_inserted = backfill_fare_quotes(session)
        if n_inserted == 0:
            logger.info("No new rows inserted (already backfilled or CSV empty)")

        logger.info("Step 2: Computing monthly APIx indices")
        n_computed = compute_monthly_indices(session)

        logger.info("=== Backfill Complete ===")
        logger.info(f"  Fare quotes inserted: {n_inserted}")
        logger.info(f"  Monthly indices computed: {n_computed}")

        # Show what's in apix_daily now
        from sqlalchemy import text

        rows = session.execute(text("SELECT date, apix, n_quotes, n_routes FROM apix_daily ORDER BY date")).all()
        logger.info(f"  apix_daily now has {len(rows)} rows:")
        for r in rows:
            logger.info(f"    {r[0]}: APIx={r[1]:.4f} ({r[2]} quotes, {r[3]} routes)")

    finally:
        session.close()


if __name__ == "__main__":
    main()
