# Your Personal Action Plan — Yuvraj (Team Lead + Infra/API + Scraping/Index/DB Support)

Everything below is scoped **only** to your ownership areas from the repo state you shared. Dashboard, cleaning, and unbundling are excluded.

---

## Part A — Your Role Map (What Touches You)

From the codebase, you own or co-own these exact files/areas:

| Area | Files you own outright | Files you co-own / wire together |
|---|---|---|
| **FastAPI + API endpoints** | `app/main.py`, `app/api/`, `app/schemas/`, `app/services/`, `app/core/` | — |
| **Celery orchestration** | `app/core/celery_app.py`, `app/tasks/*.py` | Sourabh/Abhay write task internals, you wire the chord |
| **Infrastructure** | `Dockerfile`, `docker-compose.yml`, `Makefile`, `.env*`, `.github/` | — |
| **Config** | `config/routes.yaml`, `config/sources.yaml`, `config/dgca_weights.csv` | — |
| **Scraping support** | `scrapers/base_scraper.py` (fetch loop), `scrapers/registry.py` | Sourabh/Abhay own individual scrapers |
| **DB support** | `db/session.py`, `app/api/deps.py` (consolidation) | Sourabh/Abhay own models/migrations/seed |
| **Engine support** | Wiring `engine/` outputs → API endpoints | Sourabh/Abhay own the math |

---

## Part B — Infrastructure Tasks (Do These First)

These are the foundation everything else sits on. Most are broken or incomplete right now.

### B1. Fix the `deps.py` / `session.py` duplication (30 min)

Right now `app/api/deps.py` and `db/session.py` both create their own engine and `SessionLocal`. This will cause two connection pools, potential mismatches, and confusion.

**What to do:**
```
# app/api/deps.py — delete the engine/SessionLocal creation, import from db/session.py

from db.session import SessionLocal

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
That's it. One engine, one session factory, one place to configure pool size.

---

### B2. Generate the first Alembic migration + hypertable (1–2 hours)

This is **blocking everything DB-related** — loader, real engine queries, seed verification.

**Step-by-step:**

```bash
# 1. Start just the DB
docker compose up db -d
docker compose exec db sh -c "psql -U apix -c 'CREATE EXTENSION IF NOT EXISTS timescaledb;'"

# 2. Generate migration from models
docker compose run --rm api alembic -c db/migrations/alembic.ini revision --autogenerate -m "initial_schema"

# 3. Edit the generated migration to add hypertable AFTER table creation:
```

In the generated migration file, append at the bottom of `upgrade()`:

```python
from alembic import op

def upgrade():
    # ... auto-generated table creates ...
    
    # Convert fare_quotes to hypertable
    op.execute("""
        SELECT create_hypertable(
            'fare_quotes', 
            'scraped_at',
            chunk_time_interval => INTERVAL '7 days',
            if_not_exists => TRUE
        );
    """)
    
    # Add composite indexes that the engine queries will need
    op.create_index(
        'ix_fare_quotes_route_lead_scrape',
        'fare_quotes',
        ['route_id', 'lead_time', 'scraped_at']
    )
    op.create_index(
        'ix_fare_quotes_quality',
        'fare_quotes',
        ['quality_flag']
    )
```

```bash
# 4. Run it
docker compose run --rm api alembic -c db/migrations/alembic.ini upgrade head

# 5. Seed
docker compose run --rm api python -m db.seed

# 6. Verify
docker compose exec db psql -U apix -c "\dt+"
docker compose exec db psql -U apix -c "SELECT * FROM routes;"
docker compose exec db psql -U apix -c "SELECT * FROM timescaledb_information.hypertables;"
```

**Update the Makefile** targets `migrate` and `seed` to use the correct alembic config path if needed. Verify `make migrate && make seed` works end-to-end.

---

### B3. Fix Docker health/startup ordering issues (45 min)

Looking at the compose file, several things need tightening:

**Problem 1:** The `api` service depends on `db` being healthy, but not on `redis`. If Redis isn't up when Celery tries to connect, the worker crashes silently.

```yaml
# docker-compose.yml changes
api:
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy

worker:
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy

beat:
  depends_on:
    worker:
      condition: service_started
    redis:
      condition: service_healthy

redis:
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 3s
    retries: 5
```

**Problem 2:** The `scripts/run_local_sweep.sh` invokes `python -m app.tasks.scrape_tasks` with args but the module has no `__main__` / argparse. Fix:

```python
# app/tasks/scrape_tasks.py — add at bottom
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", default="DEL-BOM")
    parser.add_argument("--lead", type=int, default=7)
    parser.add_argument("--source", default="indigo")
    args = parser.parse_args()
    result = scrape_route.delay(args.source, args.route, args.lead)
    print(f"Task submitted: {result.id}")
```

**Problem 3:** The Dockerfile installs Playwright by default (making the image ~1.5 GB). Until scraping is live, add a conditional:

```dockerfile
ARG INSTALL_PLAYWRIGHT=false
RUN if [ "$INSTALL_PLAYWRIGHT" = "true" ]; then \
      playwright install --with-deps chromium; \
    fi
```

And in compose, override the build-arg only for the `worker` service (which is the only one that scrapes):

```yaml
worker:
  build:
    context: .
    args:
      INSTALL_PLAYWRIGHT: "true"
```

---

### B4. Create `db/queries.py` — the shared query layer (2–3 hours)

This is the module that everyone (API endpoints, engine, tasks) will import instead of writing raw SQLAlchemy in 10 different places. **You** should own this file because you're the one wiring everything.

```python
# db/queries.py
"""
Centralised database queries. Every SELECT/INSERT that touches
fare_quotes, apix_daily, routes, or dgca_weights lives here.
"""

from datetime import date, datetime
from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.models import FareQuote, ApixDaily, Route, DGCAWeight, DGCABenchmark, RawQuote


# ── Routes ──────────────────────────────────────────────────────

def get_active_routes(session: Session) -> list[Route]:
    return session.scalars(
        select(Route).where(Route.active == True)
    ).all()


def get_route_by_code(session: Session, route_code: str) -> Route | None:
    return session.scalars(
        select(Route).where(Route.route_code == route_code)
    ).first()


# ── Fare Quotes ─────────────────────────────────────────────────

def upsert_fare_quotes(session: Session, records: list[dict]) -> int:
    """
    Bulk upsert into fare_quotes. Uses ON CONFLICT DO UPDATE
    on (source, route_id, carrier, flight_no, depart_date, scraped_at, fare_class).
    Returns number of rows affected.
    """
    if not records:
        return 0
    
    stmt = pg_insert(FareQuote).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=[
            'source', 'route_id', 'carrier', 'flight_no',
            'depart_date', 'scraped_at', 'fare_class'
        ],
        set_={
            'total_fare': stmt.excluded.total_fare,
            'base_fare': stmt.excluded.base_fare,
            'udf': stmt.excluded.udf,
            'taxes': stmt.excluded.taxes,
            'convenience_fee': stmt.excluded.convenience_fee,
            'other_fees': stmt.excluded.other_fees,
            'quality_flag': stmt.excluded.quality_flag,
        }
    )
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
    rows = session.execute(stmt, {
        "scrape_date": scrape_date,
        "lead_times": list(lead_times),
    }).mappings().all()
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
    rows = session.scalars(select(DGCAWeight)).all()
    total = sum(r.weight for r in rows)
    if total == 0:
        return {}
    return {r.route_id: r.weight / total for r in rows}


# ── APIx Daily ──────────────────────────────────────────────────

def upsert_apix_daily(session: Session, record: dict):
    stmt = pg_insert(ApixDaily).values(**record)
    stmt = stmt.on_conflict_do_update(
        index_elements=['date'],
        set_={
            'apix': stmt.excluded.apix,
            'apix_base_only': stmt.excluded.apix_base_only,
            'n_quotes': stmt.excluded.n_quotes,
            'n_routes': stmt.excluded.n_routes,
        }
    )
    session.execute(stmt)
    session.commit()


def get_apix_daily(
    session: Session,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
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


def get_apix_weekly(session: Session, from_date=None, to_date=None) -> list[dict]:
    stmt = text("""
        SELECT 
            date_trunc('week', date)::date AS week_start,
            ROUND(AVG(apix)::numeric, 4) AS apix,
            ROUND(AVG(apix_base_only)::numeric, 4) AS apix_base_only,
            SUM(n_quotes) AS n_quotes,
            MAX(n_routes) AS n_routes
        FROM apix_daily
        WHERE (:from_date IS NULL OR date >= :from_date)
          AND (:to_date IS NULL OR date <= :to_date)
        GROUP BY date_trunc('week', date)
        ORDER BY week_start
    """)
    rows = session.execute(stmt, {
        "from_date": from_date, "to_date": to_date
    }).mappings().all()
    return [dict(r) for r in rows]


def get_apix_monthly(session: Session, from_date=None, to_date=None) -> list[dict]:
    stmt = text("""
        SELECT 
            date_trunc('month', date)::date AS month_start,
            ROUND(AVG(apix)::numeric, 4) AS apix,
            ROUND(AVG(apix_base_only)::numeric, 4) AS apix_base_only,
            SUM(n_quotes) AS n_quotes,
            MAX(n_routes) AS n_routes
        FROM apix_daily
        WHERE (:from_date IS NULL OR date >= :from_date)
          AND (:to_date IS NULL OR date <= :to_date)
        GROUP BY date_trunc('month', date)
        ORDER BY month_start
    """)
    rows = session.execute(stmt, {
        "from_date": from_date, "to_date": to_date
    }).mappings().all()
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
    stmt = select(FareQuote).where(FareQuote.quality_flag == 'ok')
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
    rows = session.execute(stmt, {
        "route_id": route_id, "route_date": date_filter
    }).mappings().all()
    return [dict(r) for r in rows]


# ── Backtest ────────────────────────────────────────────────────

def get_dgca_benchmarks(session: Session) -> list[dict]:
    rows = session.scalars(
        select(DGCABenchmark).order_by(DGCABenchmark.month)
    ).all()
    return [{"month": r.month, "avg_fare": r.avg_fare} for r in rows]
```

This module is the single interface between DB and everything else. Endpoints call these functions; engine calls these functions; tasks call these functions.

---

### B5. Wire `MOCK_MODE` toggle properly in every endpoint (1–2 hours)

Right now every endpoint only has the mock branch. You need to add the real branch that calls `db/queries.py`. The pattern for every endpoint file:

```python
# app/api/v1/apix.py — example transformation
from fastapi import APIRouter, Depends, Query
from datetime import date
from app.core.config import settings
from app.core.security import require_token
from app.api.deps import get_db
from app.services.mock_service import get_mock_apix_daily
from db.queries import get_apix_daily as db_get_apix_daily

router = APIRouter(prefix="/apix", tags=["APIx Index"])

@router.get("/daily", dependencies=[Depends(require_token)])
def apix_daily(
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    db=Depends(get_db),
):
    if settings.MOCK_MODE:
        return get_mock_apix_daily(from_date, to_date)
    
    return db_get_apix_daily(db, from_date, to_date)
```

Do this for **all 9 endpoints** (`daily`, `weekly`, `monthly`, `routes`, `heatmap`, `elasticity`, `quotes`, `backtest`, `trigger-sweep`). The mock branch stays forever (demo safety net), but the real branch is now one `MOCK_MODE=false` toggle away.

---

### B6. Register the `POST /admin/trigger-sweep` endpoint (30 min)

The frontend already calls `triggerSweep()` but the route doesn't exist server-side.

```python
# app/api/v1/admin.py (new file)
from fastapi import APIRouter, Depends
from app.core.security import require_token
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/trigger-sweep", dependencies=[Depends(require_token)])
def trigger_sweep():
    if settings.MOCK_MODE:
        return {"status": "mock_mode", "detail": "Sweep simulated (mock mode)"}
    
    from app.tasks.scrape_tasks import run_daily_sweep
    task = run_daily_sweep.delay()
    return {"status": "queued", "task_id": task.id}
```

Register in `app/api/v1/router.py`:
```python
from app.api.v1.admin import router as admin_router
api_router.include_router(admin_router)
```

---

## Part C — Celery Chord Wiring (The Orchestration Core)

This is the most critical thing only **you** can do, because it connects Sourabh/Abhay's scrapers → Vanshika's pipeline → Sourabh/Abhay's engine. Nobody else sees the full picture.

### C1. Design the task chain

```python
# app/tasks/scrape_tasks.py — YOUR implementation

from celery import group, chord
from datetime import date, timedelta
from app.core.celery_app import celery
from scrapers.registry import build_jobs_for_date, get_scraper
from app.core.logging import logger


@celery.task(name="tasks.run_daily_sweep", bind=True, max_retries=1)
def run_daily_sweep(self):
    """
    Nightly entry point (02:00 IST via beat).
    1. Build all scrape jobs for today
    2. Fan-out as a Celery group
    3. On completion, trigger clean_and_load → compute_daily_index
    """
    today = date.today()
    jobs = list(build_jobs_for_date(today))
    logger.info(f"Daily sweep: {len(jobs)} jobs for {today}")
    
    if not jobs:
        logger.warning("No jobs generated — check routes.yaml / sources.yaml")
        return {"status": "no_jobs", "date": str(today)}
    
    # Fan out scraping, then chain: clean → index
    scrape_group = group(
        scrape_route.s(
            source=j.source,
            route_code=f"{j.origin}-{j.destination}",
            lead_time=j.lead_time,
        )
        for j in jobs
    )
    
    callback = chain(
        clean_and_load.si(str(today)),        # si = immutable sig (ignores group results)
        compute_daily_index.si(str(today)),
    )
    
    workflow = chord(scrape_group, callback)
    workflow.apply_async()
    
    return {
        "status": "dispatched",
        "date": str(today),
        "n_jobs": len(jobs),
    }


@celery.task(
    name="tasks.scrape_route",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    reject_on_worker_lost=True,
)
def scrape_route(self, source: str, route_code: str, lead_time: int):
    """
    Scrape a single (source, route, lead_time) combination.
    Returns a dict summary (for monitoring), not the raw data
    (raw data goes to disk + raw_quotes table).
    """
    from scrapers.registry import get_scraper
    from scrapers.base_scraper import ScrapeJob
    from datetime import date, timedelta
    
    today = date.today()
    origin, destination = route_code.split("-")
    depart_date = today + timedelta(days=lead_time)
    
    job = ScrapeJob(
        source=source,
        origin=origin,
        destination=destination,
        depart_date=depart_date,
        lead_time=lead_time,
        scrape_date=today,
    )
    
    scraper = get_scraper(source)
    results = scraper.run_jobs([job])  # returns list[ScrapeResult]
    result = results[0]
    
    if not result.ok:
        logger.error(
            f"Scrape failed: {source}/{route_code}/T+{lead_time}: {result.error}"
        )
        # Retry on transient failures
        if result.status_code in (429, 503, 502):
            raise self.retry(exc=Exception(result.error))
        
    return {
        "source": source,
        "route_code": route_code,
        "lead_time": lead_time,
        "ok": result.ok,
        "status_code": result.status_code,
        "method": result.method,
        "raw_path": result.raw_path,
    }
```

```python
# app/tasks/pipeline_tasks.py — YOUR wiring, Vanshika fills internals

from app.core.celery_app import celery
from app.core.logging import logger


@celery.task(name="tasks.clean_and_load", bind=True)
def clean_and_load(self, scrape_date_str: str):
    """
    Run the full cleaning pipeline for a given scrape date.
    Calls pipeline.run logic programmatically (not CLI).
    """
    from datetime import date
    from pipeline.run import run_pipeline  # Vanshika exposes this function
    
    scrape_date = date.fromisoformat(scrape_date_str)
    
    stats = run_pipeline(scrape_date)
    # stats = {"parsed": N, "valid": N, "loaded": N, "outliers": N}
    
    logger.info(f"Pipeline complete for {scrape_date}: {stats}")
    return stats
```

```python
# app/tasks/index_tasks.py — YOUR wiring, Sourabh/Abhay fill engine internals

from app.core.celery_app import celery
from app.core.logging import logger


@celery.task(name="tasks.compute_daily_index", bind=True)
def compute_daily_index(self, compute_date_str: str):
    """Compute Laspeyres index for the given date, write to apix_daily."""
    from datetime import date
    from db.session import SessionLocal
    from engine.index_calculator import compute_daily
    
    compute_date = date.fromisoformat(compute_date_str)
    
    session = SessionLocal()
    try:
        result = compute_daily(compute_date, session)
        logger.info(f"Index computed for {compute_date}: APIx={result['apix']}")
        return result
    finally:
        session.close()
```

**Key design decisions I'm encoding here:**
- `chord` not `chain`: scrape jobs run **in parallel**, then the callback fires only when all finish
- `si()` (immutable signature) on the callback prevents Celery from injecting group results as an argument
- `acks_late=True` + `reject_on_worker_lost=True` on scrape_route: if a worker dies mid-scrape, the task goes back to the queue
- Raw data goes to disk+DB in the scraper layer, not passed through Celery (payloads are too large for Redis)

### C2. Ask Vanshika to expose `run_pipeline()` as a callable function

Right now `pipeline/run.py` only works as a CLI (`python -m pipeline.run --date ...`). You need her to refactor so there's a function you can call from the Celery task:

```python
# pipeline/run.py — what you need her to add/expose

def run_pipeline(
    scrape_date: date,
    source: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Programmatic entry point (called by Celery task).
    Returns {"parsed": int, "valid": int, "loaded": int, "outliers": int}
    """
    # ... existing CLI logic refactored into this function ...
```

The existing `if __name__ == "__main__"` argparse block then just calls this function.

---

## Part D — Scraping Infrastructure (Your Support for Sourabh/Abhay)

You're not writing IndiGo/MMT parsers, but you own the **framework** they plug into.

### D1. Implement `BaseScraper.fetch()` — the retry loop (2–3 hours)

This is the most important stub in the scraping layer. Sourabh/Abhay implement `build_request()` and `parse_ok()`, but the retry/proxy/fallback logic is infra:

```python
# scrapers/base_scraper.py — flesh out fetch()

import time
import random
from datetime import datetime
from curl_cffi import requests as curl_requests
from scrapers.proxy_manager import ProxyManager
from scrapers.fingerprints import get_random_profile, get_headers_for_profile
from scrapers.storage import save_raw
from app.core.logging import logger
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)

class BaseScraper(ABC):
    rate_limit_rps = 0.33  # 1 req / 3s
    max_retries = 4
    _last_request_time = 0.0
    
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.session_manager = SessionManager(self.source_name)
    
    @property
    @abstractmethod
    def source_name(self) -> str: ...
    
    @abstractmethod
    def build_request(self, job: ScrapeJob) -> RequestSpec: ...
    
    @abstractmethod
    def parse_ok(self, status_code: int, body: dict | str) -> bool: ...
    
    def _rate_limit(self):
        """Enforce per-source rate limit with jitter."""
        elapsed = time.monotonic() - self._last_request_time
        min_interval = 1.0 / self.rate_limit_rps
        jitter = random.uniform(1.0, 4.0)
        wait = max(0, min_interval - elapsed) + jitter
        if wait > 0:
            logger.debug(f"Rate limit: sleeping {wait:.1f}s")
            time.sleep(wait)
        self._last_request_time = time.monotonic()
    
    def fetch(self, job: ScrapeJob) -> ScrapeResult:
        """
        Core fetch loop:
        1. Build request spec from subclass
        2. Try curl_cffi with TLS impersonation + proxy rotation
        3. On 403/429/5xx: rotate proxy, retry (up to max_retries)
        4. On total curl_cffi failure: fall back to Playwright
        5. Save raw payload to disk (+ raw_quotes table later)
        """
        spec = self.build_request(job)
        last_error = None
        last_status = None
        
        # ── curl_cffi attempts ──
        for attempt in range(1, self.max_retries + 1):
            self._rate_limit()
            
            profile = get_random_profile()
            headers = get_headers_for_profile(profile)
            headers.update(spec.headers or {})
            proxy = self.proxy_manager.get()
            
            try:
                logger.info(
                    f"[{self.source_name}] Attempt {attempt}/{self.max_retries} "
                    f"| {job.origin}-{job.destination} T+{job.lead_time} "
                    f"| proxy={'direct' if not proxy else '***'} | profile={profile}"
                )
                
                response = curl_requests.request(
                    method=spec.method,
                    url=spec.url,
                    headers=headers,
                    json=spec.json_body if spec.method == "POST" else None,
                    params=spec.params if spec.method == "GET" else None,
                    impersonate=profile,
                    proxies={"https": proxy, "http": proxy} if proxy else None,
                    timeout=30,
                )
                
                last_status = response.status_code
                
                if self.parse_ok(response.status_code, response.text):
                    result = ScrapeResult(
                        job=job,
                        ok=True,
                        status_code=response.status_code,
                        payload=response.text,
                        fetched_at=datetime.utcnow(),
                        method="curl_cffi",
                        proxy_used=bool(proxy),
                    )
                    save_raw(result)
                    return result
                
                # Not OK — mark proxy bad, backoff, continue
                logger.warning(
                    f"[{self.source_name}] Attempt {attempt} got {response.status_code}"
                )
                if proxy:
                    cooldown = self.proxy_manager.backoff(response.status_code)
                    self.proxy_manager.mark_bad(proxy, cooldown)
                    
            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"[{self.source_name}] Attempt {attempt} exception: {e}"
                )
                if proxy:
                    self.proxy_manager.mark_bad(proxy, 60)
        
        # ── Playwright fallback ──
        logger.info(f"[{self.source_name}] curl_cffi exhausted, trying Playwright")
        try:
            from scrapers.playwright_fallback import fetch_with_browser
            import asyncio
            
            pw_result = asyncio.get_event_loop().run_until_complete(
                fetch_with_browser(job, self)
            )
            if pw_result and pw_result.ok:
                save_raw(pw_result)
                return pw_result
        except Exception as e:
            last_error = f"Playwright fallback failed: {e}"
            logger.error(last_error)
        
        # ── Total failure ──
        return ScrapeResult(
            job=job,
            ok=False,
            status_code=last_status,
            payload=None,
            error=last_error or f"All {self.max_retries} attempts failed",
            fetched_at=datetime.utcnow(),
            method="curl_cffi",
            proxy_used=False,
        )
```

### D2. Unblock Sourabh/Abhay on endpoint recon

They need to capture real XHR endpoints before they can write `build_request()` / `parse_ok()`. As lead, **you should do the recon for at least one source** (IndiGo is easiest) to set the pattern, then hand the template to them for MakeMyTrip.

**IndiGo recon steps (do this today):**

1. Open Chrome → `https://www.goindigo.in` → DevTools → Network tab → check "Preserve log" + "XHR" filter
2. Search for a flight: DEL → BOM, date = today+7
3. Look for a POST to something like `https://www.goindigo.in/api/...` or `https://digitalapi.goindigo.in/...`
4. Right-click the XHR → Copy → Copy as cURL
5. Save the curl command in `scrapers/recon/indigo_endpoint.md`
6. Document: URL, method, headers (which ones matter), request body shape, response body shape
7. Save a real response JSON as `tests/fixtures/indigo_sample.json`

This unblocks:
- Sourabh/Abhay: they implement `IndigoScraper.build_request()` / `parse_ok()`
- Vanshika: she implements `indigo_parser.parse()` using the real response shape
- Tests: real fixtures replace the placeholder ones

---

## Part E — Your Day-by-Day Sprint Plan

Given you're probably 2-4 weeks from the hackathon presentation, here's the priority order:

### Week 1 (Unblock Everyone + Foundation)

| Day | Task | Unblocks |
|---|---|---|
| **Day 1** | B2 (Alembic migration + hypertable + seed) | Everything DB |
| **Day 1** | B1 (Fix deps.py duplication) | Clean DB access |
| **Day 1** | D2 (IndiGo recon — do it yourself) | Sourabh/Abhay scrapers + Vanshika parsers |
| **Day 2** | B4 (Create `db/queries.py` — all queries) | API real mode + engine |
| **Day 2** | B3 (Docker compose fixes) | Stable local dev for team |
| **Day 3** | C1 (Celery chord — `run_daily_sweep` + `scrape_route` + wiring) | End-to-end pipeline |
| **Day 3** | B6 (Register trigger-sweep endpoint) | Frontend demo button |
| **Day 3** | C2 (Ask Vanshika for `run_pipeline()` function) | Pipeline task |
| **Day 4** | D1 (Implement `BaseScraper.fetch()` retry loop) | Scraper execution |
| **Day 4** | B5 (Wire MOCK_MODE toggle in all endpoints) | API real mode |

### Week 2 (Integration + Real Data)

| Day | Task |
|---|---|
| **Day 5–6** | Integration test: trigger-sweep → scrape (IndiGo at minimum) → pipeline → index → API. Debug the full chain. |
| **Day 6** | Fix whatever breaks. Expect: cookie/session issues, payload shape mismatches, missing DB columns. |
| **Day 7** | Start the 30-day data collection clock. Set up a cron (or leave Celery beat running on a VPS/cloud VM). Even if only IndiGo works, start collecting. |

### Week 3 (Stabilise + Harden)

| Day | Task |
|---|---|
| **Day 8–9** | Add integration tests (`pytest -m integration`): DB round-trip, full pipeline with real fixtures, index calculation. |
| **Day 10** | API response validation: make sure real DB responses actually match `app/schemas/responses.py`. Fix any field mismatches. |
| **Day 11** | Monitoring: add a `/api/v1/admin/status` endpoint showing last scrape time, quote counts per route, coverage %. Judges love this. |
| **Day 12** | Help Sneh with `docs/architecture.md` and `docs/index_methodology.md` — you know the system best. |

### Week 4 (Demo Prep)

| Day | Task |
|---|---|
| **Day 13** | Ensure `MOCK_MODE=true` demo path is bulletproof (this is your stage demo safety net). |
| **Day 14** | Do a live demo rehearsal: start with mock mode, show dashboard, then switch to real mode and show actual data. |
| **Day 15** | Have Sourabh/Abhay run `engine/backtest.py` against collected data + DGCA monthly. Generate `data/backtest_results.json` with real numbers. |

---

## Part F — Critical Decisions Only You Can Make

As lead, these are the judgment calls you need to make and communicate to the team:

### F1. Real DGCA weights
`config/dgca_weights.csv` has **placeholder values**. You need real passenger traffic data from DGCA monthly reports. **DGCA data sources for real weights:**

- DGCA publishes **city pair wise monthly domestic passenger traffic statistics** directly on their portal at `dgca.gov.in/digigov-portal/`. Navigate to Monthly Statistics → City Pair Wise. Download the PDFs for your 6 routes for the most recent available months.

- There's also a GitHub dataset (`Vonter/india-aviation-traffic`) with monthly carrier-wise passenger and freight traffic sourced from DGCA, covering domestic, international, cargo, and on-time performance data. This is easier to work with than PDFs — clone it, filter for your 6 city pairs, and extract passenger numbers.

- IndiaS​tat also carries state/city pair-wise scheduled domestic traffic data monthly for 2025 (though it may require a subscription).

**Your action:** Download real passenger counts for DEL-BOM, DEL-BLR, BOM-BLR, DEL-CCU, BLR-HYD, MAA-DEL. Compute weights as `passengers_on_route / total_passengers_across_all_6`. Update `config/dgca_weights.csv`. This is a 2-hour task max and judges **will** ask where your weights come from.

---

### F2. Define the base period

Your index formula needs `P_i,0` — the base-period price. Right now the engine stub uses "first 7 days of data." You need to decide:
- **Option A (recommended for SIH):** Use the first 7 days of your live collection as the base period. Index = 100 on day 7, then moves from there. Simple, defensible.
- **Option B (if you have more history):** Use a full calendar month as the base (e.g., your first complete month of scraping).

Document this in `config/` as a new entry in `routes.yaml` or a separate `base_period.yaml`:
```yaml
base_period:
  method: "first_n_days"
  n_days: 7
  # Alternatively:
  # method: "fixed_month"
  # month: "2026-08"
```

### F3. Communicate interface contracts to your team

Send this to Sourabh/Abhay today:

> **What I need from you:**
> 1. `IndigoScraper.build_request(job) → RequestSpec` and `parse_ok(status, body) → bool` — fill these from the recon I'll share
> 2. `engine/index_calculator.compute_daily()` — replace the stub with real DB queries using `db/queries.py` functions I'm writing
> 3. `engine/aggregator.weekly_rollup()` and `monthly_rollup()` — uncomment the SQL, use `db/queries.get_apix_weekly/monthly()`
> 4. `engine/backtest.run_backtest()` — use real `apix_daily` data vs `dgca_benchmark` table
> 5. First Alembic migration (I'll handle this, but review it)

Send this to Vanshika:

> **What I need from you:**
> 1. Expose `run_pipeline(date) → dict` as a callable function in `pipeline/run.py` (not just CLI)
> 2. Implement `loader.load(df) → int` using `db.queries.upsert_fare_quotes()` — I'll have that function ready
> 3. Implement `indigo_parser.parse()` once I share the real fixture from recon

---

## Part G — Admin/Monitoring Endpoint (Judges Love This)

Add a system health/status endpoint that shows operational state:

```python
# app/api/v1/admin.py — add to the file you created in B6

from datetime import date
from sqlalchemy import func, select
from db.models import FareQuote, ApixDaily, RawQuote

@router.get("/status", dependencies=[Depends(require_token)])
def system_status(db=Depends(get_db)):
    if settings.MOCK_MODE:
        return {
            "mode": "mock",
            "scraping": {"status": "simulated"},
            "database": {"status": "mock_data"},
        }
    
    # Latest scrape
    latest_raw = db.scalar(
        select(func.max(RawQuote.fetched_at))
    )
    
    # Today's quote count
    today_quotes = db.scalar(
        select(func.count(FareQuote.id))
        .where(func.cast(FareQuote.scraped_at, date) == date.today())
    )
    
    # Total quotes
    total_quotes = db.scalar(select(func.count(FareQuote.id)))
    
    # Latest index
    latest_index = db.scalar(
        select(ApixDaily.apix).order_by(ApixDaily.date.desc()).limit(1)
    )
    latest_index_date = db.scalar(
        select(ApixDaily.date).order_by(ApixDaily.date.desc()).limit(1)
    )
    
    # Coverage: how many of the 6 routes have data today
    routes_covered = db.scalar(
        select(func.count(func.distinct(FareQuote.route_id)))
        .where(func.cast(FareQuote.scraped_at, date) == date.today())
        .where(FareQuote.quality_flag == 'ok')
    )
    
    # Quality distribution
    quality_dist = dict(
        db.execute(
            select(FareQuote.quality_flag, func.count())
            .group_by(FareQuote.quality_flag)
        ).all()
    )
    
    return {
        "mode": "live",
        "scraping": {
            "last_scrape_at": latest_raw.isoformat() if latest_raw else None,
            "quotes_today": today_quotes or 0,
            "total_quotes": total_quotes or 0,
        },
        "index": {
            "latest_apix": latest_index,
            "latest_date": latest_index_date.isoformat() if latest_index_date else None,
        },
        "coverage": {
            "routes_today": routes_covered or 0,
            "routes_total": 6,
            "pct": round((routes_covered or 0) / 6 * 100, 1),
        },
        "quality": quality_dist,
    }
```

Register in `router.py` alongside the other routers.

---

## Part H — Your Personal Checklist (Print This)

```
INFRASTRUCTURE
  [x] Fix deps.py / session.py duplication
  [x] Generate first Alembic migration + hypertable
  [x] Fix Docker compose health/ordering
  [x] Create db/queries.py (full query layer)
  [x] Fix run_local_sweep.sh (add argparse to scrape_tasks)
  [x] Slim Docker image (Playwright only in worker)

API ENDPOINTS  
  [x] Wire MOCK_MODE toggle in all 9 endpoints
  [x] Register POST /admin/trigger-sweep
  [x] Add GET /admin/status monitoring endpoint
  [ ] Verify response schemas match real DB output

CELERY ORCHESTRATION
  [x] Implement run_daily_sweep (chord: group → clean → index)
  [x] Implement scrape_route task wrapper
  [x] Wire clean_and_load to Vanshika's run_pipeline()
  [x] Wire compute_daily_index to engine

SCRAPING SUPPORT
  [ ] Implement BaseScraper.fetch() retry loop
  [x] Do IndiGo endpoint recon (DevTools → recon/indigo_endpoint.md)
  [x] Save real fixture → tests/fixtures/indigo_sample.json
  [x] Implement IndiGo build_request/parse_ok (done by Abhay)
  [x] Implement MakeMyTrip build_request/parse_ok (done by Abhay)

DATA / CONFIG
  [x] Download real DGCA city-pair passenger traffic
  [x] Compute and update dgca_weights.csv with real weights
  [ ] Define and document base_period config
  [x] Download DGCA monthly average fare data for backtest

TEAM COORDINATION
  [X] Tell Vanshika: expose run_pipeline() as function
  [X] Tell Vanshika: implement loader.load() using db.queries
  [x] Tell Sourabh/Abhay: fill build_request/parse_ok after recon
  [ ] Tell Sourabh/Abhay: wire engine to db/queries.py
  [X] Tell Sneh: start docs/architecture.md and index_methodology.md
  [ ] Daily 10-min sync: done / doing / blocked
``

---

This is the complete scope of work for your role. Everything here is derived directly from the current state of your repository. The highest-leverage items are **B2** (migration — unblocks everyone), **D2** (recon — unblocks scrapers + parsers), and **C1** (Celery chord — connects the whole pipeline). Do those three in the first 3 days and the rest of the team can run in parallel.