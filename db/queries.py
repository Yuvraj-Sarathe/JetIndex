"""
Centralised database queries. Every SELECT/INSERT that touches
fare_quotes, apix_daily, routes, or dgca_weights lives here.
"""

from datetime import date, datetime, time

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.models import ApixDaily, DgcaBenchmark, DgcaWeight, FareQuote, RawQuote, Route

# ── Routes ──────────────────────────────────────────────────────


def get_active_routes(session: Session) -> list[Route]:
    """Return all active routes in the basket."""
    return session.scalars(select(Route).where(Route.active)).all()


def get_route_by_code(session: Session, route_code: str) -> Route | None:
    """Look up a single route by its code (e.g. 'DEL-BOM')."""
    return session.scalars(select(Route).where(Route.route_code == route_code)).first()


# ── Fare Quotes ─────────────────────────────────────────────────
def upsert_fare_quotes(session: Session, records: list[dict]) -> int:
    if not records:
        return 0

    allowed_columns = set(FareQuote.__table__.columns.keys())

    normalized_records = []
    for record in records:
        route_code = record.get("route_code")

        if not route_code:
            continue

        route = get_route_by_code(session, route_code)

        if not route:
            raise ValueError(f"Route not found: {route_code}")

        record["route_id"] = route.id

        normalized_record = {key: value for key, value in record.items() if key in allowed_columns}

        normalized_records.append(normalized_record)

    records = normalized_records

    for record in records:
        depart_time = record.get("depart_time")
        depart_date = record.get("depart_date")

        if isinstance(depart_time, time) and depart_date:
            record["depart_time"] = datetime.combine(depart_date, depart_time)

    stmt = pg_insert(FareQuote).values(records)

    result = session.execute(stmt)
    session.commit()
    return result.rowcount


def insert_raw_quote(session: Session, record: dict) -> int:
    """Insert into raw_quotes audit table. Returns the new row ID."""
    rq = RawQuote(**record)
    session.add(rq)
    session.commit()
    return rq.id


def get_median_fares_by_route(
    session: Session,
    scrape_date: date,
    lead_times: tuple[int, ...] = (1, 7, 15, 30, 45),
) -> list[dict]:
    """
    For each (route_id, lead_time) on a given scrape_date,
    return the median total_fare and median base_fare
    across all ok-flagged quotes.
    """
    stmt = text("""
        SELECT
            route_id,
            lead_time,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY total_fare) AS median_fare,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY base_fare) AS median_base_fare,
            count(*) AS n_quotes
        FROM fare_quotes
        WHERE scraped_at::date = :scrape_date
          AND lead_time = ANY(:lead_times)
          AND quality_flag = 'ok'
        GROUP BY route_id, lead_time
    """)
    rows = (
        session.execute(
            stmt,
            {
                "scrape_date": scrape_date,
                "lead_times": list(lead_times),
            },
        )
        .mappings()
        .all()
    )
    return [dict(r) for r in rows]


def get_base_period_prices(
    session: Session,
    n_days: int = 7,
) -> dict[int, float]:
    """
    Average total_fare per route over the first n_days of data.
    Used as P_i,0 in the Laspeyres index.
    """
    stmt = text("""
        WITH first_date AS (
            SELECT MIN(scraped_at::date) AS d FROM fare_quotes WHERE quality_flag = 'ok'
        )
        SELECT
            route_id,
            AVG(total_fare) AS avg_fare
        FROM fare_quotes, first_date
        WHERE scraped_at::date < first_date.d + :n_days
          AND quality_flag = 'ok'
        GROUP BY route_id
    """)
    rows = session.execute(stmt, {"n_days": n_days}).mappings().all()
    return {r["route_id"]: float(r["avg_fare"]) for r in rows}


# ── DGCA Weights ────────────────────────────────────────────────


def get_weights(session: Session) -> dict[int, float]:
    """Returns {route_id: normalised_weight}."""
    rows = session.scalars(select(DgcaWeight)).all()
    total = sum(r.weight for r in rows)
    if total == 0:
        return {}
    return {r.route_id: r.weight / total for r in rows}


# ── APIx Daily ──────────────────────────────────────────────────


def upsert_apix_daily(session: Session, record: dict):
    """Insert or update a daily index row."""
    stmt = pg_insert(ApixDaily).values(**record)
    stmt = stmt.on_conflict_do_update(
        index_elements=["date"],
        set_={
            "apix": stmt.excluded.apix,
            "apix_base_only": stmt.excluded.apix_base_only,
            "n_quotes": stmt.excluded.n_quotes,
            "n_routes": stmt.excluded.n_routes,
        },
    )
    session.execute(stmt)
    session.commit()


def get_apix_daily(
    session: Session,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    """Return daily index rows, optionally filtered by date range."""
    stmt = select(ApixDaily).order_by(ApixDaily.date)
    if from_date:
        stmt = stmt.where(ApixDaily.date >= from_date)
    if to_date:
        stmt = stmt.where(ApixDaily.date <= to_date)
    rows = session.scalars(stmt).all()
    return [
        {
            "date": r.date.isoformat(),
            "apix": round(r.apix, 4),
            "apix_base_only": round(r.apix_base_only, 4) if r.apix_base_only else None,
            "n_quotes": r.n_quotes,
            "n_routes": r.n_routes,
        }
        for r in rows
    ]


def get_apix_weekly(
    session: Session,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    """Weekly rollup of the daily index."""
    where_clauses = []
    params = {}
    if from_date is not None:
        where_clauses.append("date >= :from_date")
        params["from_date"] = from_date
    if to_date is not None:
        where_clauses.append("date <= :to_date")
        params["to_date"] = to_date

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    stmt = text(f"""
        SELECT
            date_trunc('week', date)::date AS week_start,
            ROUND(AVG(apix)::numeric, 4) AS apix,
            ROUND(AVG(apix_base_only)::numeric, 4) AS apix_base_only,
            SUM(n_quotes) AS n_quotes,
            MAX(n_routes) AS n_routes
        FROM apix_daily
        {where_sql}
        GROUP BY date_trunc('week', date)
        ORDER BY week_start
    """)
    rows = session.execute(stmt, params).mappings().all()
    return [dict(r) for r in rows]


def get_apix_monthly(
    session: Session,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    """Monthly rollup of the daily index."""
    where_clauses = []
    params = {}
    if from_date is not None:
        where_clauses.append("date >= :from_date")
        params["from_date"] = from_date
    if to_date is not None:
        where_clauses.append("date <= :to_date")
        params["to_date"] = to_date

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    stmt = text(f"""
        SELECT
            date_trunc('month', date)::date AS month_start,
            ROUND(AVG(apix)::numeric, 4) AS apix,
            ROUND(AVG(apix_base_only)::numeric, 4) AS apix_base_only,
            SUM(n_quotes) AS n_quotes,
            MAX(n_routes) AS n_routes
        FROM apix_daily
        {where_sql}
        GROUP BY date_trunc('month', date)
        ORDER BY month_start
    """)
    rows = session.execute(stmt, params).mappings().all()
    return [dict(r) for r in rows]


# ── Quotes for API ──────────────────────────────────────────────


def get_quotes(
    session: Session,
    route_id: int | None = None,
    route_date: date | None = None,
    lead_time: int | None = None,
    carrier: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Flexible quote query with optional filters."""
    stmt = select(FareQuote).where(FareQuote.quality_flag == "ok")
    if route_id:
        stmt = stmt.where(FareQuote.route_id == route_id)
    if route_date:
        stmt = stmt.where(func.cast(FareQuote.scraped_at, date) == route_date)
    if lead_time:
        stmt = stmt.where(FareQuote.lead_time == lead_time)
    if carrier:
        stmt = stmt.where(FareQuote.carrier == carrier)
    stmt = stmt.order_by(FareQuote.scraped_at.desc()).limit(limit)
    rows = session.scalars(stmt).all()
    return [_quote_to_dict(r) for r in rows]


def _quote_to_dict(q: FareQuote) -> dict:
    """Serialise a FareQuote ORM object to a flat dict."""
    return {
        "source": q.source,
        "route_code": q.route.route_code if q.route else None,
        "carrier": q.carrier,
        "flight_no": q.flight_no,
        "depart_date": q.depart_date.isoformat(),
        "lead_time": q.lead_time,
        "fare_class": q.fare_class,
        "base_fare": q.base_fare,
        "udf": q.udf,
        "taxes": q.taxes,
        "convenience_fee": q.convenience_fee,
        "other_fees": q.other_fees,
        "total_fare": q.total_fare,
        "quality_flag": q.quality_flag,
        "scraped_at": q.scraped_at.isoformat(),
    }


# ── Heatmap ─────────────────────────────────────────────────────


def get_heatmap_data(session: Session, route_date: date | None = None) -> list[dict]:
    """Per-route stats for the heatmap: avg fare, stddev (volatility), quote count."""
    date_filter = route_date or date.today()
    stmt = text("""
        SELECT
            r.route_code, r.origin, r.destination,
            r.o_lat, r.o_lon, r.d_lat, r.d_lon,
            ROUND(AVG(fq.total_fare)::numeric, 2) AS avg_fare,
            ROUND(STDDEV(fq.total_fare)::numeric, 2) AS volatility,
            COUNT(*) AS n_quotes
        FROM fare_quotes fq
        JOIN routes r ON fq.route_id = r.id
        WHERE fq.scraped_at::date = :route_date
          AND fq.quality_flag = 'ok'
        GROUP BY r.id
    """)
    rows = session.execute(stmt, {"route_date": date_filter}).mappings().all()
    return [dict(r) for r in rows]


# ── Elasticity ──────────────────────────────────────────────────


def get_elasticity_data(
    session: Session,
    route_id: int,
    route_date: date | None = None,
) -> list[dict]:
    """Median fare per lead_time bucket for a given route."""
    date_filter = route_date or date.today()
    stmt = text("""
        SELECT
            lead_time,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY total_fare) AS median_fare,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY base_fare) AS median_base_fare,
            count(*) AS n_quotes
        FROM fare_quotes
        WHERE route_id = :route_id
          AND scraped_at::date = :route_date
          AND quality_flag = 'ok'
        GROUP BY lead_time
        ORDER BY lead_time
    """)
    rows = session.execute(stmt, {"route_id": route_id, "route_date": date_filter}).mappings().all()
    return [dict(r) for r in rows]


# ── Backtest ────────────────────────────────────────────────────


def get_dgca_benchmarks(session: Session) -> list[dict]:
    """Return all DGCA monthly average fare benchmarks (per route)."""
    rows = session.scalars(select(DgcaBenchmark).order_by(DgcaBenchmark.route_code, DgcaBenchmark.month)).all()
    return [{"route_code": r.route_code, "month": r.month, "avg_fare": r.avg_fare} for r in rows]
