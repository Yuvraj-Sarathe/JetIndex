# JetIndex (APIx) — Complete Project Documentation (A–Z)

> **One file, every fact.** This document captures the *entire* state of the repository as of
> **September 6, 2026** (branch `main`, HEAD `693f1bb`): vision, architecture, tech stack,
> every module and file, the data contract, the index math, the API, the frontend, tests,
> CI/CD, team, current coding stage (what is done vs. stubbed), and what comes next.
>
> **Security note:** a live API token exists in `.env.local` and `instructions-for-team.md`.
> It is intentionally **not** reproduced in this document.

---

## Table of Contents

1. [Project Identity & Problem Statement](#1-project-identity--problem-statement)
2. [The Solution: APIx](#2-the-solution-apix)
3. [Repository Snapshot & Current Coding Stage](#3-repository-snapshot--current-coding-stage)
4. [Tech Stack (Full Inventory)](#4-tech-stack-full-inventory)
5. [High-Level Architecture](#5-high-level-architecture)
6. [The Data Contract (FROZEN)](#6-the-data-contract-frozen)
7. [Directory-by-Directory Deep Dive](#7-directory-by-directory-deep-dive)
   - 7.1 `app/` — FastAPI + Celery orchestration
   - 7.2 `scrapers/` — stealth scraping engine
   - 7.3 `pipeline/` — cleaning, validation & unbundling
   - 7.4 `db/` — TimescaleDB models, migrations, seeds
   - 7.5 `engine/` — index math, elasticity & backtest
   - 7.6 `config/` — static configuration
   - 7.7 `frontend/` — React dashboard
   - 7.8 `data/` — datasets
   - 7.9 `tests/` — pytest suite
   - 7.10 `scripts/` — helper scripts
   - 7.11 `docs/`, `slides/`, `demo/` — deliverables
   - 7.12 `.github/` — CI/CD & templates
8. [Index Methodology & Math](#8-index-methodology--math)
9. [API Reference](#9-api-reference)
10. [Celery Task Orchestration](#10-celery-task-orchestration)
11. [Docker Infrastructure](#11-docker-infrastructure)
12. [Configuration & Environment Variables](#12-configuration--environment-variables)
13. [Makefile & Developer Commands](#13-makefile--developer-commands)
14. [Testing Landscape](#14-testing-landscape)
15. [CI/CD Pipeline](#15-cicd-pipeline)
16. [Team, Ownership & Workflow](#16-team-ownership--workflow)
17. [Ethics & Compliance](#17-ethics--compliance)
18. [Implementation Status: Done vs. Stub (Critical)](#18-implementation-status-done-vs-stub-critical)
19. [Deliverables Checklist State](#19-deliverables-checklist-state)
20. [Known Gaps, TODOs & Roadmap](#20-known-gaps-todos--roadmap)

---

## 1. Project Identity & Problem Statement

| Field | Value |
|---|---|
| **Repository** | `JetIndex` (GitHub: `Yuvraj-Sarathe/JetIndex`) |
| **Product name** | **APIx** — Airfare Price Index |
| **Tagline** | Real-time Airfare Price Index for India |
| **Competition** | Smart India Hackathon 2026 (SIH26056) |
| **Sponsor / Ministry** | MoSPI / NSO (Ministry of Statistics & Programme Implementation / National Statistical Office) |
| **Track** | Smart Automation / Macroeconomic Data Engineering |
| **License** | MIT (© 2026 JetIndex Team, SIH 2026) |
| **Language/version** | Python ≥ 3.11 (backend), Node.js 20 (frontend) |

### The problem
India's Consumer Price Index (CPI) computes airfare from **manual ticket-counter price collection**:

- **Slow** — monthly collection misses daily price swings of 200–400 %.
- **Incomplete** — covers only ~30 % of bookings (offline counter sales).
- **Outdated** — data reaches MoSPI/RBI already stale.
- **Expensive** — manual labor at airport counters across India.

Meanwhile **~90 % of flight bookings now happen online**, so the largest share of the market is a
blind spot in macroeconomic data. The project's mission: **automate the collection and index
computation of airfare prices for India's CPI.**

---

## 2. The Solution: APIx

A fully automated pipeline replacing manual collection:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Scrape    │───▶│   Clean     │───▶│   Store     │───▶│   Compute   │───▶│   Serve   │
│  (IndiGo,   │    │  (Unbundle, │    │ (TimescaleDB│    │ (Laspeyres  │    │ (FastAPI +  │
│  MakeMyTrip)│    │   IQR, etc) │    │  hypertable)│    │   Index)    │    │  Dashboard) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Key innovation: fare unbundling
Instead of scraping a single total price, APIx **decomposes every quote** into canonical
components — a first for India's airfare data — enabling **component-level inflation tracking**:

- **Base Fare** — the actual ticket price
- **UDF** — User Development Fee (airport charges)
- **Taxes** — GST, PSF (Passenger Service Fee), ASF (Aviation Security Fee)
- **Convenience Fee** — OTA platform charges
- **Other Fees** — fuel surcharge, meals, seats, insurance

### The index
A **DGCA passenger-weighted Laspeyres price index** over a fixed basket of 6 high-traffic
domestic routes, published daily (with weekly/monthly rollups), validated by backtesting
against DGCA monthly average fares (MAPE / RMSE / Pearson correlation).

---

## 3. Repository Snapshot & Current Coding Stage

### Git state (Sept 6, 2026)
- **Branch:** `main`
- **HEAD:** `23420f5` — *"fix: remove redundant .github/README.md"*
- **Recent commits:** DB migrations, deps.py fix, Docker improvements, Celery tasks, admin endpoint, queries layer, real Indigo fixture

### Coding stage in one paragraph
This is a **Day-1+ scaffold** with significant real implementations added:
- **Done:** DB migration + hypertable, deps.py single source of truth, Celery chord workflow (scrape → clean → index), centralised query layer (`db/queries.py`), admin endpoint, Redis healthcheck, conditional Playwright, real Indigo fixture (77 flights), **MOCK_MODE toggle wired in all 9 endpoints** (mock branch stays as demo safety net; real branch calls `db/queries.py`).
- **Still stubbed:** `playwright_fallback`, `raw_quotes` DB insert in `storage.py`, `loader.load()` DB upsert, engine `compute_daily`/`get_base_period_prices` DB paths.
See [§18](#18-implementation-status-done-vs-stub-critical) for the precise inventory.

---

## 4. Tech Stack (Full Inventory)

### Backend (Python 3.11+)
| Technology | Purpose | Where |
|---|---|---|
| **FastAPI + Uvicorn** | Async REST API, auto Swagger at `/docs` | `app/` |
| **Pydantic v2 + pydantic-settings** | Validation; `.env`-driven settings | `app/core/config.py`, `pipeline/schemas.py` |
| **SQLAlchemy 2** (class-based `DeclarativeBase`) | ORM, models | `db/` |
| **psycopg (binary)** | PostgreSQL driver (`postgresql+psycopg://`) | `db/session.py` |
| **Alembic** | DB migrations | `db/migrations/` |
| **Celery[redis] + Redis** | Distributed task queue + beat scheduler | `app/core/celery_app.py` |
| **Flower** | Celery monitoring UI | compose service |
| **curl_cffi** | TLS-fingerprint-impersonating HTTP client | `scrapers/` |
| **Playwright + playwright-stealth** | Stealth browser fallback | `scrapers/playwright_fallback.py` |
| **Polars** | High-speed data cleaning (dedupe, IQR) | `pipeline/cleaner.py` |
| **NumPy / SciPy / Pandas** | Stats: linregress, MAPE/RMSE/correlation | `engine/` |
| **PyYAML** | Config files | `config/`, `db/seed.py`, `scrapers/registry.py` |
| **loguru** | Structured logging | `app/core/logging.py` |
| **tenacity** | Retry/backoff for scraper fetch loop | `scrapers/base_scraper.py` |

### Frontend (Node 20)
| Technology | Purpose |
|---|---|
| **React 18.3** (JSX) | SPA |
| **Vite 5** | Dev server (port 5173) + build |
| **TailwindCSS 3.4** | Styling |
| **Recharts 2.12** | Line/Scatter charts |
| **react-leaflet 4 + Leaflet 1.9** | Route heatmap map |
| **papaparse 5** | CSV export |
| **ESLint 8 + Prettier 3** | Lint/format |

### Dev / QA
| Technology | Purpose |
|---|---|
| **pytest + pytest-cov** | Test runner & coverage |
| **ruff** | Python lint + format |
| **pre-commit** | Hooks: ruff, ruff-format, end-of-file, trailing-whitespace |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker Compose** | 8-service dev stack |
| **TimescaleDB `latest-pg16`** | Time-series DB with hypertables |
| **Redis 7-alpine** | Celery broker/backend (with healthcheck) |
| **GitHub Actions** | Backend CI (ruff + pytest), Frontend CI (eslint + build) |

---

## 5. High-Level Architecture

```
                            ┌──────────────────────────────────────────┐
                            │           Celery Beat (02:00 IST)        │
                            └──────────────────┬───────────────────────┘
                                               │
                                               ▼
                            ┌──────────────────────────────────────────┐
                            │              Scrapers Layer              │
                            │  ┌─────────┐  ┌──────────┐  ┌────────┐ │
                            │  │ IndiGo  │  │ MakeMyTrip│  │ AirIndia│ │
                            │  │ curl_cffi│  │ curl_cffi │  │ (stub) │ │
                            │  └────┬────┘  └─────┬─────┘  └────────┘ │
                            │       │             │                    │
                            │       ▼             ▼                    │
                            │  ┌─────────────────────────┐            │
                            │  │  Playwright Fallback     │            │
                            │  │  (stealth browser)       │            │
                            │  └────────────┬────────────┘            │
                            └───────────────┼─────────────────────────┘
                                            │  raw JSON → data/raw/ + raw_quotes
                                            ▼
                            ┌──────────────────────────────────────────┐
                            │           Data Pipeline                  │
                            │  Parse → Validate → Unbundle → IQR      │
                            │  pipeline/schemas.py (FROZEN)            │
                            │  RawQuote → CleanQuote                   │
                            └───────────────┬─────────────────────────┘
                                            │
                                            ▼
                            ┌──────────────────────────────────────────┐
                            │         TimescaleDB (PostgreSQL 16)      │
                            │  raw_quotes (audit) / fare_quotes (hypertable)
                            │  routes / dgca_weights / apix_daily / dgca_benchmark
                            └───────────────┬─────────────────────────┘
                                            │
                                            ▼
                            ┌──────────────────────────────────────────┐
                            │            Index Engine                   │
                            │  DGCA-weighted Laspeyres index           │
                            │  I_t = Σ(P_it × Q_i0) / Σ(P_i0 × Q_i0) × 100
                            │  Weekly/Monthly rollups                  │
                            │  Lead-time elasticity matrix             │
                            │  DGCA backtest (MAPE, RMSE, r)           │
                            └───────────────┬─────────────────────────┘
                                            │
                                            ▼
                            ┌──────────────────────────────────────────┐
                            │     FastAPI (/api/v1) + React Dashboard   │
                            │  Swagger + Bearer-token auth             │
                            └──────────────────────────────────────────┘
```

**Data flow, step by step:**
1. **Celery Beat** fires `run_daily_sweep` daily at **02:00 IST**.
2. The sweep builds ~60 jobs (`6 routes × 5 lead times × 2 enabled sources`) and fans out
   `scrape_route` tasks as a Celery group (parallel execution).
3. Raw payloads are saved to `data/raw/{source}/{scrape_date}/{ORIGIN}-{DEST}_T{lead}.json`
   **and** mirrored into the `raw_quotes` audit table.
4. When ALL scrape jobs complete, the chord callback fires: `clean_and_load` runs the pipeline
   (source parsers → validators → unbundler → dedupe + IQR → upsert into `fare_quotes`).
5. `compute_daily_index` computes the DGCA-weighted Laspeyres index and writes `apix_daily`.
6. FastAPI serves everything to the React dashboard, all behind a single Bearer token.

---

## 6. The Data Contract (FROZEN)

`pipeline/schemas.py` is the **single source of truth** (frozen after Day-1 review; changes
require a `data-contract` PR and approval from Yuvraj + Vanshika). Everything else — parsers,
DB models, API responses, frontend — builds against it. Pydantic `model_config =
ConfigDict(extra="forbid")` on both models rejects unknown fields.

### `RawQuote` — vendor output, unnormalised
| Field | Type | Notes |
|---|---|---|
| `source` | `Literal["indigo","makemytrip","airindia","akasa","easemytrip"]` | |
| `route_code` | `str` | e.g. `"DEL-BOM"` |
| `origin` / `destination` | `str` | IATA codes |
| `carrier` | `str` | e.g. `"6E"`, `"AI"` |
| `flight_no` | `str` | |
| `depart_date` | `date` | |
| `depart_time` | `time \| None` | |
| `scrape_date` | `date` | |
| `scraped_at` | `datetime` | |
| `lead_time` | `int` | days between scrape and depart |
| `fare_class` | `str \| None` | "Saver", "Flexi", "Economy" |
| `stops` | `int = 0` | |
| `is_refundable` | `bool \| None` | |
| `currency` | `str = "INR"` | |
| `total_fare` | `float` | as reported |
| `fare_breakdown` | `dict[str, float]` | **vendor labels untouched** |
| `seats_left` | `int \| None` | |
| `sold_out` | `bool = False` | |
| `raw_ref` | `str` | path to raw payload (audit) |

### `CleanQuote` (alias `FlightQuote`) — normalised
Identity fields mirror `RawQuote` plus:
| Field | Type | Notes |
|---|---|---|
| `base_fare` | `float` | |
| `udf` | `float = 0` | |
| `taxes` | `float = 0` | GST + PSF + ASF etc. |
| `convenience_fee` | `float = 0` | |
| `other_fees` | `float = 0` | |
| `total_fare` | `float` | |
| `quality_flag` | `Literal["ok","iqr_outlier","sold_out","sum_mismatch","duplicate"] = "ok"` | |
| `raw_ref` | `str` | |

A `model_validator(mode="after")` enforces **sum consistency**: components must equal
`total_fare` within **±₹5**, else `quality_flag = "sum_mismatch"`.

### Fee-label → canonical-component mapping (unbundler)
| Vendor label (regex, case-insensitive) | Canonical field |
|---|---|
| `base fare`, `fare`, `airfare` | `base_fare` |
| `user development fee`, `udf`, `adf` | `udf` |
| `psf`, `asf`, `aviation security`, `gst`, `k3`, `cute` | `taxes` |
| `convenience fee`, `service fee`, `platform fee` | `convenience_fee` |
| `fuel surcharge`, `yq`, `seat`, `meal`, `insurance` | `other_fees` |

---

## 7. Directory-by-Directory Deep Dive

### 7.1 `app/` — FastAPI API + Celery orchestration **(Owner: Yuvraj)**

| File | Contents |
|---|---|
| `main.py` | `create_app()` factory; `GET /health`; mounts v1 router at `/api/v1`. |
| `core/config.py` | `Settings(BaseSettings)` reading `.env`. Exported singleton `settings`. |
| `core/security.py` | `HTTPBearer` + `require_token` dependency. |
| `core/celery_app.py` | Celery `"apix"` app (Redis broker+backend, `Asia/Kolkata` tz); `beat_schedule` with `daily-sweep`; `autodiscover_tasks(["app.tasks"])`. |
| `core/logging.py` | loguru: colorized stdout + `logs/app.log`. |
| `api/deps.py` | Imports `SessionLocal` from `db.session` (single source of truth). `get_db()` async generator. |
| `api/v1/router.py` | Aggregates 6 routers: `/admin`, `/apix`, `/routes`, `/elasticity`, `/quotes`, `/backtest`. |
| `api/v1/admin.py` | **`POST /admin/trigger-sweep`** — dispatches `run_daily_sweep` Celery task. **`GET /admin/status`** — system health: scrape times, quote counts, index, coverage, quality distribution (MOCK_MODE toggle). |
| `api/v1/apix.py` | `GET /daily`, `/weekly`, `/monthly` — MOCK_MODE toggle (mock + DB). |
| `api/v1/routes.py` | `GET /` (basket+weights), `GET /heatmap` — MOCK_MODE toggle (mock + DB). |
| `api/v1/elasticity.py` | `GET /?route_id=&route_date=` — MOCK_MODE toggle (mock + DB). |
| `api/v1/quotes.py` | `GET /?route_id=&route_date=&lead_time=&carrier=&limit=` — MOCK_MODE toggle (mock + DB). |
| `api/v1/backtest.py` | `GET /` → `{monthly[], summary{mape,rmse,corr}}` — MOCK_MODE toggle (mock + DB). |
| `schemas/responses.py` | Pydantic response models. |
| `services/mock_service.py` | `_load_mock(filename)` reads `data/mock/*.json`. |
| `tasks/scrape_tasks.py` | **Implemented:** `run_daily_sweep()` (chord: group of `scrape_route` → callback clean→index), `scrape_route()` (with retries on 429/503/502). |
| `tasks/pipeline_tasks.py` | **Implemented:** `clean_and_load(scrape_date)` — calls `pipeline.run.run_pipeline()`. |
| `tasks/index_tasks.py` | **Implemented:** `compute_daily_index(compute_date)` — calls `engine.index_calculator.compute_daily()`. |

### 7.2 `scrapers/` — Stealth scraping engine **(Owners: Sourabh + Abhay)**

| File | Contents |
|---|---|
| `base_scraper.py` | Dataclasses: `ScrapeJob`, `ScrapeResult`, `RequestSpec`. `BaseScraper(ABC)` with full `fetch()` loop (tenacity retry, proxy rotation, Playwright fallback). |
| `indigo.py` | **Implemented:** `IndigoScraper` — `build_request()` + `parse_ok()` wired to IndiGo XHR endpoint. |
| `makemytrip.py` | **Implemented:** `MakeMyTripScraper` — `build_request()` + `parse_ok()` wired to MMT XHR endpoint. |
| `airindia.py` | Stub class, post-MVP. |
| `registry.py` | `SCRAPERS` dict; `get_scraper(name)`; **working** `build_jobs_for_date()`. |
| `proxy_manager.py` | **Working** `ProxyManager`: rotation, cooldown, backoff. |
| `session_manager.py` | **Working** `SessionManager`: JSON cookie/token persistence. |
| `fingerprints.py` | **Working** TLS profiles + UA rotation. |
| `playwright_fallback.py` | **Stub** `fetch_with_browser()`. |
| `storage.py` | **Working** `save_raw(result)` → `data/raw/`. DB insert commented TODO. |
| `recon/indigo_endpoint.md` | **Captured:** Full cURL command with headers, auth token, request body shape. |

### 7.3 `pipeline/` — Cleaning, validation & unbundling **(Owner: Vanshika)**

| File | Contents |
|---|---|
| `schemas.py` | **The frozen data contract** (see §6). |
| `parsers/indigo_parser.py` | **Implemented** `parse(payload, job_meta) -> list[RawQuote]`. |
| `parsers/makemytrip_parser.py` | **Stub**. |
| `validators.py` | **Working** `validate_raw(q)`. |
| `unbundler.py` | **Working** `unbundle(RawQuote) -> CleanQuote`. |
| `cleaner.py` | **Working** Polars: `dedupe()`, `iqr_filter()`, `flag_sold_out()`, `clean_batch()`. |
| `loader.py` | **Stub** `load(df) -> int` — PostgreSQL upsert commented TODO. |
| `run.py` | **Working CLI** `python -m pipeline.run --date YYYY-MM-DD`. |

### 7.4 `db/` — TimescaleDB models, migrations, seeds **(Owners: Sourabh + Abhay)**

| File | Contents |
|---|---|
| `session.py` | `Base(DeclarativeBase)`, engine, `SessionLocal`, `get_db()`. Single source of truth. |
| `models.py` | Six SQLAlchemy 2 models. |
| `queries.py` | **Implemented:** Centralised query layer — `get_active_routes`, `upsert_fare_quotes`, `get_median_fares_by_route`, `get_apix_daily/weekly/monthly`, `get_quotes`, `get_heatmap_data`, `get_elasticity_data`, `get_dgca_benchmarks`. |
| `init.sql` | `CREATE EXTENSION IF NOT EXISTS timescaledb;` |
| `seed.py` | **Working** `seed()` + `seed_routes()` + `seed_dgca_weights()` + `seed_dgca_benchmarks()`. |
| `migrations/versions/0001_initial_schema.py` | **Created:** All 6 tables + hypertable on `fare_quotes(scraped_at)` + composite PK + indexes. |

**Tables created:** `routes`, `raw_quotes`, `fare_quotes` (hypertable), `apix_daily`, `dgca_weights`, `dgca_benchmark`.

### 7.5 `engine/` — Index math, elasticity & backtest **(Owners: Sourabh + Abhay)**

| File | Contents |
|---|---|
| `index_calculator.py` | **Working** `laspeyres()`, `geometric_young()`. **Stub** `compute_daily()` (placeholder returns 100.0). |
| `weights.py` | **Working** `load_weights(csv)`. **Stub** `get_base_period_prices()`. |
| `aggregator.py` | **Working** `pct_change()`, `daily_with_pct()`. **Stubs** `weekly_rollup()`, `monthly_rollup()`. |
| `elasticity.py` | **Working** `compute_elasticity_coefficient()`. **Stub** `compute_elasticity()`. |
| `backtest.py` | **Working** metric helpers. **Stub** `run_backtest()`. |

### 7.6 `config/` — Static configuration **(Owner: Yuvraj)**

- **`routes.yaml`** — 6-route basket with airport lat/lon and `lead_times: [1,7,15,30,45]`.
- **`sources.yaml`** — per-source config. Enabled: **indigo**, **makemytrip**.
- **`dgca_weights.csv`** — real DGCA FY 2024–25 passenger traffic weights (6 routes, total 23,163,234 passengers). Source: DGCA "City Pair Wise Passenger Traffic."
- **`dgca_monthly_avg_fare.csv`** — real DGCA monthly average fares, Jan 2024 – Nov 2025 (32 data points across 6 routes). Source: Kaggle "India Aviation Traffic Data" by Vonter (compiled from DGCA published reports).

### 7.7 `frontend/` — APIx Dashboard **(Owner: Mehak)**

**Setup:** Vite dev server on :5173 proxying `/api` → `http://localhost:8000`.

**Components:** MetricCard, ApixTrend, Heatmap, ElasticityCurve, BacktestChart, UnbundlingInspector, TimeRangeFilter, ExportButton.

### 7.8 `data/` — Datasets

| Folder | Contents | Git? |
|---|---|---|
| `raw/` | Scrape payloads | **No** (gitignored) |
| `mock/` | Realistic fake API responses | Yes |
| `reference/` | `airports.csv`, `dgca_monthly_avg_fare.csv` | Yes |

### 7.9 `tests/` — pytest suite (26+ unit tests + 11 integration tests)

| File | Tests | What they cover |
|---|---|---|
| `test_app/test_health.py` | 4 | Health endpoint, auth |
| `test_db/test_models.py` | 2 | Model imports, table names |
| `test_engine/test_index_calculator.py` | 4 | Laspeyres, Geometric Young |
| `test_pipeline/test_unbundler.py` | 4 | Validation, unbundling |
| `test_pipeline/test_cleaner.py` | — | Dedup, IQR, sold-out flagging |
| `test_scrapers/test_base.py` | 4 | Job/result creation, registry |
| `test_scrapers/test_request_builders.py` | 8 | IndiGo + MMT build_request/parse_ok |
| `test_scrapers/test_fetch_engine.py` | — | Fetch loop, retry logic |
| `test_scrapers/test_session_manager.py` | — | Cookie/token persistence |
| `test_scrapers/test_proxy_manager.py` | — | Proxy rotation, cooldown |
| `test_integration/test_db_pipeline.py` | 11 | **@integration** — DB round-trip, unbundler→DB, real fixture pipeline |

### 7.10 `scripts/`

- `generate_mock_data.py` — deterministic mock data generator.
- `run_local_sweep.sh` — one-off scrape wrapper.
- `wait_for_db.sh` — pg_isready poller.

### 7.11 `docs/`, `slides/`, `demo/` **(Owner: Sneh)**

- `docs/` — content files still to be written.
- `slides/` — pitch deck not yet created.
- `demo/` — video not yet recorded.

### 7.12 `.github/` — CI/CD & templates

- `workflows/backend-ci.yml` — ruff + pytest on push/PR.
- `workflows/frontend-ci.yml` — eslint + build on `frontend/**` changes.
- `PULL_REQUEST_TEMPLATE.md` — structured PR template.
- `ISSUE_TEMPLATE/` — bug and task templates.

---

## 8. Index Methodology & Math

### DGCA-weighted Laspeyres (primary)
```
I_t = Σ_i (P_i,t × Q_i,0) / Σ_i (P_i,0 × Q_i,0) × 100
```
- `P_i,t` — median `total_fare` across carriers & lead times
- `Q_i,0` — DGCA passenger volume weight (normalised to sum 1)
- `P_i,0` — base-period price (first 7 days of data → index = 100)

### Real DGCA Weights (FY 2024–25)

| Route | Passengers | Weight (`Q_i,0`) |
|-------|----------:|---------:|
| DEL–BOM | 68,50,869 | 0.2958 |
| DEL–BLR | 46,81,042 | 0.2021 |
| BOM–BLR | 41,14,574 | 0.1776 |
| DEL–CCU | 27,70,386 | 0.1196 |
| MAA–DEL | 24,52,761 | 0.1059 |
| BLR–HYD | 22,93,602 | 0.0990 |

**Source:** DGCA "City Pair Wise Passenger Traffic" FY 2024–25 ([dgca.gov.in](https://dgca.gov.in)).

### Backtest Data

The backtest compares APIx output against **DGCA Monthly Average Fares** (Jan 2024 – Nov 2025, 32 data points across 6 routes).

**Source:** Kaggle dataset ["India Aviation Traffic Data"](https://github.com/Vonter/india-aviation-traffic) by Vonter — sourced from DGCA published reports. DGCA's own portal had not been updated with recent monthly figures, so this Kaggle aggregation (which compiles the same DGCA reports) was used.

### Backtest metrics
- **MAPE** — Mean Absolute Percentage Error
- **RMSE** — Root Mean Square Error
- **Pearson r** — correlation coefficient

---

## 9. API Reference

Base URL `http://localhost:8000`, all endpoints under `/api/v1` require
`Authorization: Bearer <token>` (except `/health` and `/docs`).

| Method | Endpoint | Description | Params |
|---|---|---|---|
| GET | `/health` | Health check | — |
| GET | `/api/v1/apix/daily` | Daily APIx | `from_date`, `to_date` |
| GET | `/api/v1/apix/weekly` | Weekly rollup | `from_date`, `to_date` |
| GET | `/api/v1/apix/monthly` | Monthly rollup | `from_date`, `to_date` |
| GET | `/api/v1/routes` | Sector basket + weights | — |
| GET | `/api/v1/routes/heatmap` | Per-route heatmap | `route_date` |
| GET | `/api/v1/elasticity` | Lead-time elasticity | `route_id`, `route_date` |
| GET | `/api/v1/quotes` | Clean quotes | `route_id`, `route_date`, `lead_time`, `carrier`, `limit` |
| GET | `/api/v1/backtest` | APIx vs DGCA | — |
| **POST** | **`/api/v1/admin/trigger-sweep`** | **Trigger scrape sweep** | — |

---

## 10. Celery Task Orchestration

- **Beat:** `daily-sweep` → `run_daily_sweep` at 02:00 IST.
- **Chord workflow:** `group(scrape_route × 60)` → callback: `clean_and_load | compute_daily_index`.
- **Queues:** worker starts with `-Q default,scrape`.
- **Monitoring:** Flower at `:5555`.

```
run_daily_sweep
  ├─ build_jobs_for_date() → 60 jobs
  ├─ chord(group([scrape_route, ...]), callback)
  │    └─ scrape_route × 60 (parallel, acks_late, retry on 429/503/502)
  └─ callback:
       ├─ clean_and_load(date) → parse → validate → unbundle → IQR → load
       └─ compute_daily_index(date) → Laspeyres → apix_daily
```

---

## 11. Docker Infrastructure

`docker-compose.yml` — 8 services:

| Service | Build | Notes |
|---|---|---|
| `db` | `timescale/timescaledb:latest-pg16` | Healthcheck: pg_isready |
| `redis` | `redis:7-alpine` | **Healthcheck: redis-cli ping** |
| `api` | `.` (INSTALL_PLAYWRIGHT=false) | Depends on db+redis healthy |
| `worker` | `. (INSTALL_PLAYWRIGHT=true)` | Depends on db+redis healthy |
| `beat` | `.` | Depends on redis healthy |
| `flower` | `.` | Port 5555 |
| `frontend` | `node:20-alpine` | Port 5173 |
| `minio` | `minio/minio` | Profile: audit |

**Dockerfile:** `INSTALL_PLAYWRIGHT` defaults to `false` (~600MB). Worker overrides to `true`.

---

## 12. Configuration & Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `MOCK_MODE` | `true` | Serve mock data (toggle: false = real DB via `db/queries.py`) |
| `API_TOKEN` | `change-me-dev-token` | Bearer auth |
| `DATABASE_URL` | `postgresql+psycopg://apix:apix@db:5432/apix` | PostgreSQL |
| `REDIS_URL` | `redis://redis:6379/0` | Celery broker |
| `PROXY_ENABLED` | `false` | Proxy rotation |
| `SCRAPE_HOUR_IST` | `2` | Nightly sweep hour |

---

## 13. Makefile & Developer Commands

| Target | Runs |
|---|---|
| `make setup` | Install deps, pre-commit, frontend |
| `make up` / `make down` | Docker compose up/down |
| `make migrate` | `alembic -c db/migrations/alembic.ini upgrade head` |
| `make seed` | `python -m db.seed` |
| `make test` | pytest (unit tests only, integration excluded) |
| `make test-integration` | pytest -m integration -v (DB round-trip tests) |
| `make lint` | ruff check + eslint |
| `make scrape ROUTE=… LEAD=… SOURCE=…` | Submit Celery scrape task |

---

## 14. Testing Landscape

- 26+ unit tests pass (verifiable with `make test`).
- 11 integration tests for DB round-trip (run with `make test-integration` inside Docker).
- Fixtures include real Indigo sample (77 flights, 756 KB).
- CI runs `pytest -m "not integration"` with coverage.

---

## 15. CI/CD Pipeline

```
GitHub Actions (push/PR to main)
├─ Backend CI            └─ Frontend CI (paths: frontend/**)
│  ├─ Lint: ruff check + │  ├─ Lint: eslint
│  │     ruff format     │  └─ Build: vite
│  └─ Test: pytest       │
└────────────────────────┘
```

---

## 16. Team, Ownership & Workflow

| Member | Role | Packages |
|---|---|---|
| **Yuvraj** | Team Lead, Backend/DevOps | `app/`, `config/`, Docker, CI |
| **Sourabh** | Scraping & DB | `scrapers/`, `db/`, `engine/` |
| **Abhay** | Scraping & DB | `scrapers/`, `db/`, `engine/` |
| **Vanshika** | Data Pipeline | `pipeline/` |
| **Mehak** | Frontend | `frontend/` |
| **Sneh** | Documentation | `docs/`, `slides/`, `demo/` |

---

## 17. Ethics & Compliance

- Rate limiting: ≤1 req/3s per source per IP
- robots.txt respected
- Off-peak scraping (02:00 IST)
- No login/booking — anonymous search only
- Audit trail: raw payloads retained
- No personal data collected

---

## 18. Implementation Status: Done vs. Stub (Critical)

### ✅ Fully implemented & working
- FastAPI app: health, CORS, Bearer auth, all v1 endpoints (**MOCK_MODE toggle** — mock + real DB branches)
- **POST /admin/trigger-sweep** endpoint registered
- **GET /admin/status** monitoring endpoint (scrape stats, coverage, quality distribution)
- Celery chord workflow: sweep → scrape group → clean → index
- **DB migration** with hypertable + composite indexes
- **deps.py single source of truth** (no duplication)
- **db/queries.py** — centralised query layer (15+ functions)
- **Redis healthcheck** + proper startup ordering
- **Dockerfile** — Playwright conditional (default off)
- **Real Indigo fixture** (77 flights, 756 KB)
- Mock service + deterministic data generator
- Loguru logging, full DB model layer, seed script
- `laspeyres()` / `geometric_young()` math + tests
- Pipeline: validators, unbundler, cleaner, `run.py` CLI
- Scrapers: registry, job builder, proxy/session managers, fingerprints, storage
- Entire frontend (7 components + hooks + client)
- GitHub Actions CI/CD, PR/issue templates
- **DGCA weights** — real FY 2024–25 passenger traffic (`config/dgca_weights.csv`, 6 routes, 23,163,234 total passengers)
- **DGCA monthly average fares** — real Jan 2024–Nov 2025 data (`config/dgca_monthly_avg_fare.csv`, 32 data points, sourced from Kaggle/Vonter DGCA compilation)

### ⚠️ Stubbed / not yet implemented
- `playwright_fallback.fetch_with_browser()` (**Sourabh/Abhay**)
- `raw_quotes` DB insert in `storage.py` (**Sourabh/Abhay**)
- `loader.load()` DB upsert (**Vanshika**)
- `compute_daily` real DB path (**Sourabh/Abhay**)
- `get_base_period_prices` real DB path (**Sourabh/Abhay**)
- `makemytrip_parser.py` (**Vanshika**)
- `docs/*` content, slides deck, demo video (**Sneh**)

---

## 19. Deliverables Checklist State

| Deliverable | Status |
|---|---|
| Working prototype: scrape → clean → index → dashboard | **Partial** — mock demo works; real scrape chain needs fetch() implementation |
| Cleaned, de-duplicated fare DB with unbundled fields | Models + cleaner **done**; loader **pending** |
| Laspeyres index module | Math **done**; DB-backed daily **pending** |
| Interactive dashboard | **Done** (mock-fed) |
| README + Docker + config docs | **Done** |
| Tests + CI/CD | **Done** (15 tests, both pipelines) |
| DB migration + hypertable | **Done** |
| Celery task chain | **Done** (chord workflow implemented) |
| Centralised query layer | **Done** (db/queries.py) |
| Admin endpoints | **Done** (POST /admin/trigger-sweep + GET /admin/status) |
| 30+ day backtest vs DGCA | **Data ready** — real DGCA FY 2024–25 weights + monthly avg fares (Jan 2024–Nov 2025, 32 data points) loaded in `config/`; backtest engine integration **pending** |
| Architecture doc, demo video, slides | **Started** |

---

## 20. Known Gaps, TODOs & Roadmap

**Remaining blockers:**
1. **loader.py** — DB upsert commented TODO; models exist, queries layer ready.
2. **compute_daily DB path** — placeholder returns 100.0; needs real `percentile_cont` queries.
3. **MakemyTrip parser** — stub; needs real fixture parsing once MMT scraping is live.
4. **Playwright fallback** — not yet wired for live anti-bot challenges.

**Known wrinkles:**
- `get_mock_apix_weekly/monthly` echo daily data; mock shapes don't fully match response schemas.
- Frontend `ApixTrend` granularity toggle doesn't fetch weekly/monthly yet.

**Roadmap beyond MVP:** Air India/Akasa/EaseMyTrip scrapers; MinIO audit archive; rate limiting + audit tags; continuous aggregates; full DGCA basket; public MoSPI/RBI-facing API.

---

*Document updated — commit `693f1bb`, branch `main`, Sept 6, 2026.*
