# End-to-End Smoke Test Report

**Date:** September 7, 2026
**Commit:** `076f924`
**Branch:** `main`

---

## Executive Summary

The full data pipeline was verified end-to-end against a real TimescaleDB instance in Docker. The chain **Parse → Validate → Unbundle → Clean → Load → DB → Index → API** works correctly with real IndiGo flight data.

| Metric | Value |
|--------|-------|
| Flights parsed | 77 |
| Quotes loaded to DB | 28 (after dedup + IQR) |
| APIx index computed | 99.40 |
| API endpoints tested | ✓ Returning real data |
| Total time | ~30 min (including bug fixes) |

---

## Pipeline Execution Log

### 1. Infrastructure Setup

```bash
docker compose down -v && docker compose up -d
docker compose exec db psql -U apix -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
docker compose run --rm api alembic -c db/migrations/alembic.ini upgrade head
docker compose run --rm api python -m db.seed
```

**Result:** ✓ All containers started, migration applied, seed completed (6 routes, 6 weights, 20 benchmarks).

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
| Loaded | 28 | Inserted into fare_quotes |

### 3. Index Computation

```bash
docker compose run --rm api python -m engine.run --date 2026-09-06
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
docker compose exec api curl -s -H "Authorization: Bearer change-me-dev-token" \
  http://localhost:8000/api/v1/apix/daily
```

**Result:** ✓ API returns real data from database.

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

**Files modified:** `db/seed.py` (aggregation fix), `pipeline/loader.py` (raw SQL insert)

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

### Bug 3: `dgca_monthly_avg_fare.csv` has multiple routes per month

**Symptom:** `duplicate key value violates unique constraint "dgca_benchmark_pkey"`

**Root Cause:** CSV contains multiple routes per month (e.g., BLR-HYD and BOM-BLR both have 2024-12), but `DgcaBenchmark` model expects one row per month.

**Fix:** Aggregate fares by month before upsert:
```python
monthly_data = {}
for row in reader:
    month = row["month"]
    if month not in monthly_data:
        monthly_data[month] = {"fares": [], "source": source}
    monthly_data[month]["fares"].append(avg_fare)

for month, data in monthly_data.items():
    avg_fare = sum(data["fares"]) / len(data["fares"])
    # upsert with averaged fare
```

**Files modified:** `db/seed.py`

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

## Database State After Smoke Test

### Tables

| Table | Rows | Notes |
|-------|------|-------|
| `routes` | 6 | DEL-BOM, DEL-BLR, BOM-BLR, DEL-CCU, BLR-HYD, MAA-DEL |
| `dgca_weights` | 6 | Real FY 2024-25 passenger traffic |
| `dgca_benchmark` | 20 | Real monthly average fares |
| `fare_quotes` | 28 | 24 ok + 4 iqr_outlier |
| `apix_daily` | 1 | APIx = 99.40 for 2026-09-06 |
| `raw_quotes` | 0 | (not populated in this test) |

### Hypertable

```
hypertable_name | num_dimensions | primary_dimension
fare_quotes     | 1              | scraped_at
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

3. **CSV data aggregation:**
   - `dgca_monthly_avg_fare.csv` has multiple routes per month
   - Model expects one row per month — aggregate before upsert

4. **Bulk insert limitations:**
   - SQLAlchemy's `executemany` with `RETURNING` doesn't work on hypertables
   - Raw SQL INSERT with explicit `id` column works

---

## Next Steps

1. **Run the full smoke test in CI** — add integration test that runs the complete pipeline
2. **Fix the `scraped_at` date mismatch** — pipeline uses `scrape_date` from job_meta, not from the fixture
3. **Add `raw_quotes` DB insert** — currently only saves to disk
4. **Test with real scraping** — run `make scrape` against live IndiGo API
5. **Set up 30-day data collection** — start the Celery beat scheduler

---

*Report generated from end-to-end smoke test on September 7, 2026.*
