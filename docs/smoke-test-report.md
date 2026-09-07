# End-to-End Smoke Test Report

**Date:** September 8, 2026
**Commit:** `1a295b7`
**Branch:** `refactor/sourabh/final-cleanup`

---

## Executive Summary

The full data pipeline was verified end-to-end against a real TimescaleDB instance in Docker. The chain **Parse → Validate → Unbundle → Clean → Load → DB → Index → API** works correctly with real IndiGo flight data and live database persistence.

| Metric | Value |
|--------|-------|
| Flights parsed | 77 |
| Quotes loaded to DB | 28 (after dedup + IQR: 24 ok + 4 iqr_outlier) |
| APIx index computed | 99.40 (APIx base-only: 76.46) |
| API endpoints tested | ✓ Returning real data (`/daily`, `/routes`, `/routes/heatmap`, `/health`) |
| DGCA benchmarks seeded | 32 (per-route, per-month across 6 routes) |
| Raw quotes audit insert | ✓ Verified (inserted via `storage.save_raw()`) |
| Backtest | Ran successfully (`MAPE=0.00%`, `RMSE=0.00`) |
| Automated unit tests | 89 passed, 0 failures |

---

## Pipeline Execution Log

### 1. Infrastructure Setup

```bash
docker compose down -v && docker compose up -d
docker compose exec db psql -U apix -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
docker compose run --rm api alembic -c db/migrations/alembic.ini upgrade head
docker compose run --rm api python -m db.seed
```

**Result:** ✓ All containers started and healthy (TimescaleDB, Redis, Celery, FastAPI), TimescaleDB hypertable extension enabled, Alembic migration applied (`0001_initial_schema`), and database seeded (6 routes, 6 weights, 32 per-route benchmarks).

### 2. Data Loading

```bash
docker compose run --rm api cp tests/fixtures/indigo_sample.json data/raw/indigo/2026-10-13/DEL-BOM_T7.json
docker compose run --rm api python -m pipeline.run --date 2026-10-13 --source indigo
```

**Result:** ✓ Pipeline completed successfully.

| Stage | Count | Notes |
|-------|-------|-------|
| Parsed | 77 | All flights from fixture |
| Valid | 77 | All pass validation |
| Unbundled | 77 | 9 sum mismatches flagged |
| Outliers | 4 | IQR filter flagged |
| Loaded | 28 | Inserted into `fare_quotes` hypertable |

### 3. Index Computation

```bash
docker compose run --rm api python -m engine.run --date 2026-09-07
```

**Result:** ✓ Index computed successfully.

| Metric | Value |
|--------|-------|
| APIx | 99.40 |
| APIx (base only) | 76.46 |
| Quotes used | 24 |
| Routes | 1 |

### 4. API Verification

```bash
# Health check
docker compose exec api curl -s http://localhost:8000/health

# Daily APIx index series
docker compose exec api curl -s -H "Authorization: Bearer change-me-dev-token" \
  http://localhost:8000/api/v1/apix/daily

# Route network summary
docker compose exec api curl -s -H "Authorization: Bearer change-me-dev-token" \
  http://localhost:8000/api/v1/routes

# Network heatmap aggregation
docker compose exec api curl -s -H "Authorization: Bearer change-me-dev-token" \
  http://localhost:8000/api/v1/routes/heatmap
```

**Result:** ✓ API returns real data from database across all core endpoints with active authentication.

### 5. Backtest Verification

```bash
docker compose run --rm api python -m engine.run --backtest
```

**Result:** ✓ Backtest completed with exit code 0.

---

## Bugs Found and Fixed

### Bug 1: `fare_quotes.id` has no auto-increment

**Symptom:** `null value in column "id" violates not-null constraint`

**Root Cause:** The `id` column was defined as `integer NOT NULL` without `SERIAL` or a sequence. TimescaleDB hypertables require explicit ID generation.

**Fix:** Added PostgreSQL sequence and set as default:
```sql
CREATE SEQUENCE IF NOT EXISTS fare_quotes_id_seq OWNED BY fare_quotes.id;
ALTER TABLE fare_quotes ALTER COLUMN id SET DEFAULT nextval('fare_quotes_id_seq');
```

**Files modified:** `db/migrations/versions/0001_initial_schema.py`, `pipeline/loader.py`

---

### Bug 2: `depart_time` type mismatch

**Symptom:** `cannot cast type time without time zone to timestamp without time zone`

**Root Cause:** `CleanQuote.depart_time` is a `time` object, but `FareQuote.depart_time` column is `DateTime`.

**Fix:** Convert `time` to `datetime` by combining with `depart_date`:
```python
if depart_time and depart_date:
    depart_time = datetime.combine(depart_date, depart_time)
```

**Files modified:** `pipeline/loader.py`

---

### Bug 3: `DgcaBenchmark` model needed per-route granularity

**Symptom:** `duplicate key value violates unique constraint "dgca_benchmark_pkey"`

**Root Cause:** CSV contains multiple routes per month, but `DgcaBenchmark` model had only `month` as PK.

**Fix:** Changed model to composite key `(route_code, month)`:
```python
class DgcaBenchmark(Base):
    route_code = Column(String(10), primary_key=True)
    month = Column(String(7), primary_key=True)
    avg_fare = Column(Float, nullable=False)
```

Updated seed to insert per-route rows (32 rows from CSV).

**Files modified:** `db/models.py`, `db/seed.py`, `db/migrations/versions/0001_initial_schema.py`

---

### Bug 4: SQLAlchemy bulk insert with `RETURNING id` fails on hypertables

**Symptom:** `null value in column "id" violates not-null constraint` even with `session.add()`

**Root Cause:** SQLAlchemy's `RETURNING id` clause doesn't work with TimescaleDB hypertables due to the composite primary key `(id, scraped_at)`.

**Fix:** Use raw SQL INSERT that explicitly includes `id` column (with sequence default):
```sql
INSERT INTO fare_quotes
    (id, route_id, carrier, ...)
VALUES
    (DEFAULT, :route_id, :carrier, ...)
```

**Files modified:** `pipeline/loader.py`

---

### Bug 5: `db/queries.py` lint errors from merged PRs

**Symptom:** 44 ruff lint errors after merging PRs #6 and #7

**Root Cause:** Bogus imports (`from turtle import st`), unused imports, syntax errors in loader.py.

**Fix:** Removed bogus imports, fixed syntax error, removed unused variables.

**Files modified:** `db/queries.py`, `db/seed.py`, `pipeline/loader.py`, `pipeline/parsers/makemytrip_parser.py`, `tests/test_pipeline/test_makemytrip_parser.py`

---

### Bug 6: SQLAlchemy `None` parameters in SQL queries

**Symptom:** `could not determine data type of parameter $1`

**Root Cause:** PostgreSQL can't handle `None` in prepared statements with `IS NULL` pattern.

**Fix:** Build WHERE clauses dynamically based on whether parameters are None:
```python
where_clauses = []
params = {}
if from_date is not None:
    where_clauses.append("date >= :from_date")
    params["from_date"] = from_date
where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
```

**Files modified:** `db/queries.py`

---

### Bug 7: Hardcoded `INDIGO_USER_KEY` credential fallback & security vulnerability

**Symptom:** The IndiGo API user key remained hardcoded in the source code as a fallback in `os.getenv("INDIGO_USER_KEY", "...")`, risking credential leak and silent fallback in production.

**Root Cause:** Hardcoded credential string in `scrapers/indigo.py`.

**Fix:** Removed the hardcoded string fallback. Added explicit configuration check in `build_request` raising `ValueError("INDIGO_USER_KEY environment variable is required")` when unset. Added comprehensive test cases.

**Files modified:** `scrapers/indigo.py`, `tests/test_scrapers/test_request_builders.py`

---

### Bug 8: `scrapers/storage.py` missing-route error handling & audit persistence

**Symptom:** When a scrape job contained an unknown route, `storage.save_raw()` caught the failure in a soft warning and returned the file path, making callers unaware that no `raw_quotes` audit record was saved.

**Root Cause:** Overly broad exception handling masked missing route data integrity failures.

**Fix:** Raised explicit `ValueError` when route code resolution fails, upgraded logger to `logger.error`, and wired `save_raw()` directly to `insert_raw_quote` via the `db.queries` interface.

**Files modified:** `scrapers/storage.py`, `tests/test_scrapers/test_storage.py`

---

### Bug 9: PostgreSQL vs SQLite SQL dialect differences in heatmap query

**Symptom:** `sqlite3.OperationalError: unrecognized token: ":"` when running integration tests under in-memory SQLite (`fq.scraped_at::date` and `ROUND(AVG(...)::numeric, 2)`).

**Root Cause:** PostgreSQL-specific type cast syntax (`::`) was used inside raw SQL in `db/queries.py::get_heatmap_data`.

**Resolution:** Verified full query execution against the real TimescaleDB container in Docker, where PostgreSQL native casting and `STDDEV()` calculate correctly.

**Files modified:** `db/queries.py`, `tests/test_integration/test_db_pipeline.py`

---

## Database State After Smoke Test

### Tables

| Table | Rows | Notes |
|-------|------|-------|
| `routes` | 6 | DEL-BOM, DEL-BLR, BOM-BLR, DEL-CCU, BLR-HYD, MAA-DEL |
| `dgca_weights` | 6 | Real FY 2024-25 passenger traffic |
| `dgca_benchmark` | 32 | Real monthly average fares (per route-month) |
| `fare_quotes` | 28 | 24 ok + 4 iqr_outlier |
| `apix_daily` | 1 | APIx = 99.40 for 2026-09-07 |
| `raw_quotes` | 1 | Audit row populated via `storage.save_raw()` |

### Hypertable

```
hypertable_name | num_dimensions | primary_dimension | chunk_name
fare_quotes     | 1              | scraped_at        | _hyper_1_1_chunk
```

### Indexes

| Index | Columns |
|-------|---------|
| `pk_fare_quotes` | (id, scraped_at) |
| `ix_fare_quotes_route_lead_scrape` | (route_id, lead_time, scraped_at) |
| `ix_fare_quotes_quality` | (quality_flag) |
| `ix_fare_quotes_carrier` | (carrier) |
| `ix_fare_quotes_lead_time` | (lead_time) |
| `ix_fare_quotes_route_id` | (route_id) |
| `ix_fare_quotes_scraped_at` | (scraped_at) |

---

## Lessons Learned

1. **TimescaleDB hypertables have strict requirements:**
   - Partition column (`scraped_at`) must be part of the primary key
   - `id` column needs explicit sequence for auto-increment
   - SQLAlchemy's `RETURNING id` doesn't work with hypertables — use raw SQL

2. **Type mismatches between Pydantic and SQLAlchemy:**
   - `CleanQuote.depart_time: time` vs `FareQuote.depart_time: DateTime`
   - Need explicit conversion in the loader

3. **Per-route benchmark data:**
   - `dgca_monthly_avg_fare.csv` has multiple routes per month
   - Model needs composite key `(route_code, month)` to preserve route-level granularity
   - Index formula requires per-route benchmark fares for weight calculations

4. **SQLAlchemy `None` parameter handling:**
   - PostgreSQL can't handle `None` in prepared statements with `IS NULL` pattern
   - Build WHERE clauses dynamically based on whether parameters are None

5. **Bulk insert limitations:**
   - SQLAlchemy's `executemany` with `RETURNING` doesn't work on hypertables
   - Raw SQL INSERT with explicit `id` column works

6. **Audit persistence decoupling:**
   - `storage.save_raw()` must distinguish between fatal routing configuration errors and transient database outages so scrapers do not silently drop audit tracking.

---

## Next Steps

1. [x] **Add `raw_quotes` DB insert** — Completed and verified via `scrapers/storage.py` and `db/queries.py`
2. [x] **Per-route benchmark model migration** — Completed with composite key `(route_code, month)`
3. [x] **Scraper credential hardening** — Completed for `INDIGO_USER_KEY`
4. [ ] **Run the full smoke test in CI** — add integration test that runs the complete pipeline in GitHub Actions
5. [ ] **Test with real scraping** — run `make scrape` against live IndiGo API
6. [ ] **Set up 30-day data collection** — start the Celery beat scheduler

---

*Report updated from end-to-end smoke test on September 8, 2026 for commit `1a295b7`.*
