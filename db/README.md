# `db/` — TimescaleDB models, migrations, seeds

**Owners: Sourabh + Abhay** (Yuvraj supports)

## Mission
Define the storage layer: SQLAlchemy 2 models, Timescale hypertable for quotes, Alembic migrations, and seed data (routes, DGCA weights).

## Tables
| Table | Key columns | Notes |
|---|---|---|
| `routes` | `id, route_code, origin, destination, o_lat, o_lon, d_lat, d_lon, active` | seeded from `config/routes.yaml` |
| `raw_quotes` | `id, source, route_id, scrape_date, depart_date, lead_time, fetched_at, status_code, method, proxy_used, raw_path, payload JSONB?` | landing/audit table written by `scrapers/storage.py` |
| `fare_quotes` **(hypertable on `scraped_at`)** | all `CleanQuote` fields + `route_id FK, raw_quote_id FK, quality_flag` | index `(route_id, lead_time, carrier, scraped_at DESC)` |
| `apix_daily` | `date PK, apix, apix_base_only, n_quotes, n_routes, method, base_period` | written by `engine/` |
| `dgca_weights` | `route_id, period, passengers, weight` | seeded from `config/dgca_weights.csv` |
| `dgca_benchmark` | `month PK, avg_fare, source_url` | from `data/reference/dgca_monthly_avg_fare.csv` |

## Files
| File | What to build |
|---|---|
| `session.py` | engine from `settings.DATABASE_URL`, `SessionLocal`, `get_db()` |
| `models.py` | the tables above; keep column names identical to `pipeline/schemas.py` |
| `init.sql` | `CREATE EXTENSION IF NOT EXISTS timescaledb;` (runs on first container start) |
| `migrations/` | Alembic; first migration creates tables + `SELECT create_hypertable('fare_quotes','scraped_at', if_not_exists => TRUE);` |
| `seed.py` | `python -m db.seed` loads routes, weights, benchmark |

## Step-by-step
1. `make up` → `make migrate` → `make seed`; confirm with `make psql` → `\dt` and `SELECT * FROM timescaledb_information.hypertables;`.
2. Add a continuous aggregate (optional, nice demo): daily median `total_fare` per `(route_id, lead_time)`.
3. Provide helper queries in `db/queries.py` (create it) that `engine/` and `app/` call: `get_daily_prices(date)`, `get_base_prices()`, `get_quotes(filters)`.
4. Write `tests/test_db/` using SQLite in-memory for model creation (skip Timescale-specific parts with `pytest.mark.integration`).

## Rules
- Schema changes → Alembic migration + PR tagged `db`. Never edit tables by hand in the container.
- UTC everywhere; convert to IST only in the frontend.
