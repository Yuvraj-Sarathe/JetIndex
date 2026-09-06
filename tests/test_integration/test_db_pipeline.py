"""Integration tests — DB round-trip, unbundler → DB, pipeline with real fixture.

All tests use an in-memory SQLite database (no PostgreSQL required).
Marked with @pytest.mark.integration — excluded from CI by default.
Run inside Docker: pytest -m integration
Run locally (if psycopg installed): pytest tests/test_integration/ -v
"""

import json
from datetime import date, datetime
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def _import_db():
    """Lazy-import DB modules so collection doesn't fail without psycopg."""
    from db.models import ApixDaily, FareQuote, RawQuote, Route
    from db.queries import get_active_routes, get_apix_daily, get_heatmap_data, get_quotes

    return {
        "ApixDaily": ApixDaily,
        "FareQuote": FareQuote,
        "RawQuote": RawQuote,
        "Route": Route,
        "get_active_routes": get_active_routes,
        "get_apix_daily": get_apix_daily,
        "get_heatmap_data": get_heatmap_data,
        "get_quotes": get_quotes,
    }


# ── Helper ──────────────────────────────────────────────────────


def _insert_route(session, route_code="DEL-BOM", origin="DEL", destination="BOM"):
    """Insert a route row and return it."""
    db = _import_db()
    route = db["Route"](
        route_code=route_code,
        origin=origin,
        destination=destination,
        o_lat=28.5562,
        o_lon=77.1000,
        d_lat=19.0896,
        d_lon=72.8656,
        active=True,
    )
    session.add(route)
    session.commit()
    return route


def _insert_fare_quote(session, route_id, **overrides):
    """Insert a fare_quote row with sensible defaults."""
    db = _import_db()
    defaults = dict(
        route_id=route_id,
        carrier="6E",
        flight_no="6E-123",
        depart_date=date(2025, 1, 15),
        lead_time=7,
        fare_class="Saver",
        base_fare=3500.0,
        udf=500.0,
        taxes=300.0,
        convenience_fee=200.0,
        other_fees=0.0,
        total_fare=4500.0,
        source="indigo",
        scraped_at=datetime(2025, 1, 8, 2, 0, 0),
        quality_flag="ok",
    )
    defaults.update(overrides)
    fq = db["FareQuote"](**defaults)
    session.add(fq)
    session.commit()
    return fq


# ── Tests: Route CRUD ───────────────────────────────────────────


class TestRouteCRUD:
    """Insert route → query back → verify fields."""

    def test_insert_and_query_route(self, db_session):
        db = _import_db()
        _insert_route(db_session, "DEL-BOM", "DEL", "BOM")

        results = db["get_active_routes"](db_session)
        assert len(results) == 1
        assert results[0].route_code == "DEL-BOM"
        assert results[0].origin == "DEL"
        assert results[0].destination == "BOM"
        assert results[0].active is True

    def test_multiple_routes(self, db_session):
        db = _import_db()
        _insert_route(db_session, "DEL-BOM", "DEL", "BOM")
        _insert_route(db_session, "DEL-BLR", "DEL", "BLR")
        _insert_route(db_session, "BOM-BLR", "BOM", "BLR")

        results = db["get_active_routes"](db_session)
        assert len(results) == 3
        codes = {r.route_code for r in results}
        assert codes == {"DEL-BOM", "DEL-BLR", "BOM-BLR"}


# ── Tests: FareQuote round-trip ─────────────────────────────────


class TestFareQuoteRoundTrip:
    """Insert fare_quote → query with db/queries.py → verify data."""

    def test_insert_and_query_quotes(self, db_session):
        db = _import_db()
        route = _insert_route(db_session)
        _insert_fare_quote(db_session, route.id, flight_no="6E-101", total_fare=4500.0)
        _insert_fare_quote(db_session, route.id, flight_no="6E-102", total_fare=5200.0)

        quotes = db["get_quotes"](db_session, route_id=route.id)
        assert len(quotes) == 2
        fares = {q["total_fare"] for q in quotes}
        assert 4500.0 in fares
        assert 5200.0 in fares

    def test_query_quotes_filter_by_carrier(self, db_session):
        db = _import_db()
        route = _insert_route(db_session)
        _insert_fare_quote(db_session, route.id, carrier="6E", flight_no="6E-101")
        _insert_fare_quote(db_session, route.id, carrier="AI", flight_no="AI-201")

        indigo_quotes = db["get_quotes"](db_session, route_id=route.id, carrier="6E")
        assert len(indigo_quotes) == 1
        assert indigo_quotes[0]["carrier"] == "6E"

    def test_query_quotes_filter_by_lead_time(self, db_session):
        db = _import_db()
        route = _insert_route(db_session)
        _insert_fare_quote(db_session, route.id, lead_time=1, flight_no="6E-101")
        _insert_fare_quote(db_session, route.id, lead_time=7, flight_no="6E-102")
        _insert_fare_quote(db_session, route.id, lead_time=15, flight_no="6E-103")

        lt7 = db["get_quotes"](db_session, route_id=route.id, lead_time=7)
        assert len(lt7) == 1
        assert lt7[0]["lead_time"] == 7

    def test_query_quotes_with_limit(self, db_session):
        db = _import_db()
        route = _insert_route(db_session)
        for i in range(10):
            _insert_fare_quote(db_session, route.id, flight_no=f"6E-{100 + i}")

        quotes = db["get_quotes"](db_session, route_id=route.id, limit=3)
        assert len(quotes) == 3


# ── Tests: Unbundler → DB round-trip ────────────────────────────


class TestUnbundlerRoundTrip:
    """Unbundle a RawQuote → insert into DB → query back."""

    def test_unbundle_then_insert(self, db_session):
        from pipeline.schemas import RawQuote as RawQuoteSchema
        from pipeline.unbundler import unbundle

        db = _import_db()
        route = _insert_route(db_session)

        raw = RawQuoteSchema(
            source="indigo",
            route_code="DEL-BOM",
            origin="DEL",
            destination="BOM",
            carrier="6E",
            flight_no="6E-789",
            depart_date=date(2025, 1, 15),
            scrape_date=date(2025, 1, 8),
            scraped_at=datetime(2025, 1, 8, 2, 0, 0),
            lead_time=7,
            total_fare=4500.0,
            fare_breakdown={
                "Base Fare": 3500.0,
                "UDF": 500.0,
                "GST": 300.0,
                "Convenience Fee": 200.0,
            },
            raw_ref="data/raw/indigo/2025-01-08/DEL-BOM_T7.json",
        )

        clean = unbundle(raw)

        assert clean.base_fare == 3500.0
        assert clean.udf == 500.0
        assert clean.taxes == 300.0
        assert clean.convenience_fee == 200.0
        assert clean.quality_flag == "ok"

        fq = db["FareQuote"](
            route_id=route.id,
            carrier=clean.carrier,
            flight_no=clean.flight_no,
            depart_date=clean.depart_date,
            lead_time=clean.lead_time,
            fare_class=clean.fare_class,
            base_fare=clean.base_fare,
            udf=clean.udf,
            taxes=clean.taxes,
            convenience_fee=clean.convenience_fee,
            other_fees=clean.other_fees,
            total_fare=clean.total_fare,
            source=clean.source,
            scraped_at=clean.scraped_at,
            quality_flag=clean.quality_flag,
        )
        db_session.add(fq)
        db_session.commit()

        quotes = db["get_quotes"](db_session, route_id=route.id)
        assert len(quotes) == 1
        assert quotes[0]["base_fare"] == 3500.0
        assert quotes[0]["total_fare"] == 4500.0

    def test_unbundle_sum_mismatch_flagged(self):
        from pipeline.schemas import RawQuote as RawQuoteSchema
        from pipeline.unbundler import unbundle

        raw = RawQuoteSchema(
            source="indigo",
            route_code="DEL-BOM",
            origin="DEL",
            destination="BOM",
            carrier="6E",
            flight_no="6E-999",
            depart_date=date(2025, 1, 15),
            scrape_date=date(2025, 1, 8),
            scraped_at=datetime(2025, 1, 8, 2, 0, 0),
            lead_time=7,
            total_fare=10000.0,
            fare_breakdown={
                "Base Fare": 3500.0,
            },
            raw_ref="data/raw/test.json",
        )

        clean = unbundle(raw)
        assert clean.quality_flag == "sum_mismatch"


# ── Tests: Heatmap query ────────────────────────────────────────


class TestHeatmapQuery:
    """Insert multiple quotes → verify heatmap aggregation."""

    def test_heatmap_data(self, db_session):
        db = _import_db()
        route = _insert_route(db_session)

        for i, fare in enumerate([4000.0, 4500.0, 5000.0]):
            _insert_fare_quote(
                db_session,
                route.id,
                flight_no=f"6E-{200 + i}",
                total_fare=fare,
                scraped_at=datetime(2025, 1, 8, 2, 0, 0),
            )

        heatmap = db["get_heatmap_data"](db_session, route_date=date(2025, 1, 8))
        assert len(heatmap) == 1
        assert heatmap[0]["route_code"] == "DEL-BOM"
        assert heatmap[0]["avg_fare"] is not None


# ── Tests: APIx daily round-trip ────────────────────────────────


class TestApixDailyRoundTrip:
    """Insert apix_daily row → query back → verify."""

    def test_insert_and_query_apix_daily(self, db_session):
        from db.models import ApixDaily
        from db.queries import get_apix_daily

        row = ApixDaily(
            date=date(2025, 1, 8),
            apix=102.3456,
            apix_base_only=101.8923,
            n_quotes=24,
            n_routes=6,
        )
        db_session.add(row)
        db_session.commit()

        results = get_apix_daily(db_session, from_date=date(2025, 1, 1), to_date=date(2025, 1, 31))
        assert len(results) == 1
        assert results[0]["date"] == "2025-01-08"
        assert results[0]["apix"] == 102.3456


# ── Tests: Real fixture parsing ─────────────────────────────────


class TestRealFixturePipeline:
    """Load real IndiGo fixture → parse → unbundle → verify data shape."""

    def test_indigo_fixture_parse_and_unbundle(self, db_session):
        """Parse the real IndiGo fixture and verify unbundling works end-to-end."""
        from pipeline.parsers.indigo_parser import parse as parse_indigo
        from pipeline.unbundler import unbundle

        db = _import_db()

        fixture_path = FIXTURES_DIR / "indigo_sample.json"
        if not fixture_path.exists():
            pytest.skip("IndiGo fixture not found")

        with open(fixture_path) as f:
            payload = json.load(f)

        if not isinstance(payload, list) or len(payload) == 0:
            pytest.skip("Fixture is empty or not a list")

        job_meta = {
            "source": "indigo",
            "raw_ref": str(fixture_path),
            "scrape_date": date(2025, 1, 8),
        }

        raw_quotes = parse_indigo(payload, job_meta)
        assert len(raw_quotes) > 0, "Parser should extract at least one quote"

        route = _insert_route(db_session)

        unbundled = []
        for rq in raw_quotes:
            try:
                clean = unbundle(rq)
                fq = db["FareQuote"](
                    route_id=route.id,
                    carrier=clean.carrier,
                    flight_no=clean.flight_no,
                    depart_date=clean.depart_date,
                    lead_time=clean.lead_time,
                    fare_class=clean.fare_class,
                    base_fare=clean.base_fare,
                    udf=clean.udf,
                    taxes=clean.taxes,
                    convenience_fee=clean.convenience_fee,
                    other_fees=clean.other_fees,
                    total_fare=clean.total_fare,
                    source=clean.source,
                    scraped_at=clean.scraped_at,
                    quality_flag=clean.quality_flag,
                )
                db_session.add(fq)
                unbundled.append(clean)
            except Exception:
                continue

        db_session.commit()

        assert len(unbundled) > 0
        assert len(unbundled) == len(raw_quotes)

        quotes = db["get_quotes"](db_session, route_id=route.id)
        assert len(quotes) > 0

        for q in quotes:
            assert q["total_fare"] > 0
            assert q["base_fare"] >= 0
            assert q["carrier"] == "6E"
