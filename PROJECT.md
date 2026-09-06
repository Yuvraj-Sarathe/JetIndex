# JetIndex (APIx) — Complete Project Documentation (A–Z)

> **One file, every fact.** This document captures the *entire* state of the repository as of
> **September 5, 2026** (branch `main`, HEAD `5bcb2f7`): vision, architecture, tech stack,
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
│   Scrape    │───▶│   Clean     │───▶│   Store     │───▶│   Compute   │───▶│   Serve     │
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

### Git state (local checkout, Sept 5, 2026)
- **Branch:** `main` (single branch; remote `origin/main` exists).
- **Local HEAD:** `5bcb2f7` — *"fix(db): use class-based DeclarativeBase, fix test imports"*.
- **Remote ahead:** local is **behind `origin/main` by 3 commits** (README-only revisions by a
  teammate: `d487cf0`, `05b11bc`, `05b40f1` — README rewording / removal of branch-protection
  mention). No conflicts; a `git pull` fast-forwards.
- **Total commits:** 19, all dated 2026-09-04 (single-day scaffold blitz by the team).
- **1 human contributor detected in the local history** (commit author), though the team is 6 people.
- **Untracked:** `.freebuff/` (tooling dir, ignore it).
- No tags, no merged PRs detected locally.

### Commit history (local, newest → oldest)
```
5bcb2f7 fix(db): use class-based DeclarativeBase, fix test imports
2f2d278 fix(ci): exclude markdown/json from ruff, fix README code example
8c08c4a docs: rewrite README with architecture, API reference, and team info
a9c54e1 fix(ci): add PYTHONPATH and fix Node.js caching
7408ec8 docs: add documentation, slides, demo templates, and team guide
4d41c5a ci: add GitHub Actions workflows and PR/issue templates
14f7522 chore(scripts): add mock data generator and helper scripts
9edd203 test: add pytest suite with 15 tests
c0bf531 chore(data): add mock data and reference datasets
cb35c74 feat(frontend): add React + Vite + Tailwind dashboard scaffold
a47bd2f feat(engine): add index math, elasticity, and DGCA backtest
7c4bee8 feat(db): add TimescaleDB models, migrations, and seeds
9619d57 feat(pipeline): add data contract and cleaning pipeline
68d621c feat(scrapers): add stealth scraping engine scaffold
4b38576 feat(app): add FastAPI app with Celery orchestration
682b597 chore: add config files for routes, sources, and DGCA weights
23c9d0a chore: add Docker setup for all services
476b0c3 chore: add root config, env, and project metadata
d1cd8ea Initial commit
```

### Coding stage in one paragraph
This is a **Day-0/Day-1 scaffold**: the full skeleton, contracts, mock mode, and demo path are
complete and testable end-to-end, but the **real implementations are deliberately stubbed**.
What works today: the FastAPI app serving realistic mock data, the Celery/beat/flower wiring,
the complete DB model layer, the pure index-math functions, the unbundler + validators +
cleaner, the scraper framework (registry, dataclasses, proxy/session/fingerprint managers),
and the full frontend. What is **not** wired to reality yet: actual scraper endpoints (recon
pending), real parsers, DB-backed engine queries, the Alembic first migration, and the
`run_daily_sweep` → `scrape_route` → `clean_and_load` → `compute_daily_index` Celery chord.
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
| **curl_cffi** | TLS-fingerprint-impersonating HTTP client (e.g. `impersonate="chrome124"`) | `scrapers/` |
| **Playwright + playwright-stealth** | Stealth browser fallback (XHR interception) | `scrapers/playwright_fallback.py` |
| **fake-useragent** | UA generation (listed in requirements; fingerprints module has its own literal UA list) | `scrapers/fingerprints.py` |
| **Polars** | High-speed data cleaning (dedupe, IQR) | `pipeline/cleaner.py` |
| **NumPy / SciPy / Pandas** | Stats: linregress, MAPE/RMSE/correlation | `engine/` |
| **PyYAML** | Config files | `config/`, `db/seed.py`, `scrapers/registry.py` |
| **httpx** | HTTP client (declared; unused so far) | — |
| **python-dotenv** | `.env` loading | — |
| **loguru** | Structured logging (console + rotating file) | `app/core/logging.py` |
| **tenacity** | Retry/backoff for the scraper fetch loop (declared; to be used in `BaseScraper.fetch`) | `scrapers/base_scraper.py` |
| **minio** (compose) | Optional S3-compatible object storage for audit payloads (`audit` profile) | `docker-compose.yml` |

### Frontend (Node 20)
| Technology | Purpose |
|---|---|
| **React 18.3** (JSX) | SPA |
| **Vite 5** | Dev server (port 5173) + build, `/api` proxy → :8000 |
| **TailwindCSS 3.4** | Styling (`slate` base, `indigo` accent, `emerald`/`rose` up/down) |
| **Recharts 2.12** | Line/Scatter charts |
| **react-leaflet 4 + Leaflet 1.9** | Route heatmap map |
| **date-fns 3** | Date helpers (declared) |
| **papaparse 5** | CSV export |
| **ESLint 8 + Prettier 3** | Lint/format (`--max-warnings 0`) |

### Dev / QA
| Technology | Purpose |
|---|---|
| **pytest + pytest-asyncio + pytest-cov** | Test runner & coverage |
| **respx** | Mock httpx for scraper tests (declared) |
| **factory-boy** | Test factories (declared) |
| **ruff** (v0.4.4 pre-commit) | Python lint (`E,F,I,N,UP,B,SIM`, line-length 120, ignores `B008`) + format |
| **pre-commit** | Hooks: ruff, ruff-format, end-of-file, trailing-whitespace, large files > 5 MB, private-key detection |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker Compose** | 8-service dev stack |
| **TimescaleDB `latest-pg16`** | Time-series DB with hypertables |
| **Redis 7-alpine** | Celery broker/backend |
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
2. The sweep builds ~60 jobs (`6 routes × 5 lead times × 2 enabled sources`) and each
   `scrape_route` job fetches the fare-search XHR response of IndiGo / MakeMyTrip using
   `curl_cffi` with impersonated TLS, retrying with proxy rotation, then falling back to a
   stealth Playwright browser.
3. Raw payloads are saved to `data/raw/{source}/{scrape_date}/{ORIGIN}-{DEST}_T{lead}.json`
   **and** mirrored into the `raw_quotes` audit table (never parsed at this layer).
4. `clean_and_load` runs the pipeline: source parsers → `RawQuote` → validators → unbundler →
   dedupe + IQR + sold-out flags → upsert into the `fare_quotes` hypertable.
5. `compute_daily_index` computes the DGCA-weighted Laspeyres index and writes `apix_daily`;
   `aggregator` produces weekly/monthly rollups; `elasticity` builds the lead-time matrix;
   `backtest` compares against DGCA benchmarks.
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

`INDIGO_FEE_MAP` and `MMT_FEE_MAP` are identical today; `airindia`/`akasa` default to the
IndiGo map, `easemytrip` to the MMT map. Unknown labels fall through a keyword heuristic
("base/fare/ticket" → base; "tax/gst/surcharge/fee" → taxes; else `other_fees` + warning log).

---

## 7. Directory-by-Directory Deep Dive

### 7.1 `app/` — FastAPI API + Celery orchestration **(Owner: Yuvraj)**

| File | Contents |
|---|---|
| `main.py` | `create_app()` factory: title *"APIx – Airfare Price Index API"* v0.1.0; CORS for `http://localhost:5173`; `GET /health` → `{status, mock_mode, version}`; mounts v1 router at `/api/v1`. Module-level `app = create_app()` for uvicorn. |
| `core/config.py` | `Settings(BaseSettings)` reading `.env` — all env vars (see §12). Exported singleton `settings` used by **every** package. |
| `core/security.py` | `HTTPBearer` + `require_token` dependency: rejects anything ≠ `settings.API_TOKEN` with 401. |
| `core/celery_app.py` | Celery `"apix"` app (Redis broker+backend, `Asia/Kolkata` tz, JSON serializers); `beat_schedule` with `daily-sweep` at `crontab(hour=SCRAPE_HOUR_IST, minute=0)`; `autodiscover_tasks(["app.tasks"])`. |
| `core/logging.py` | loguru: colorized stdout + `logs/app.log` (rotation 10 MB, retention 7 days); runs on import. |
| `api/deps.py` | Lazy SQLAlchemy engine (`pool_pre_ping=True`) + `SessionLocal` + `get_db()` async generator. Note: `app/api/deps.py` duplicates `db/session.py` — a known redundancy. |
| `api/v1/router.py` | Aggregates 5 routers: `/apix`, `/routes`, `/elasticity`, `/quotes`, `/backtest`. |
| `api/v1/apix.py` | `GET /daily`, `/weekly`, `/monthly` — `from_date`/`to_date` filters; **mock branch only** (TODO: real DB). |
| `api/v1/routes.py` | `GET /` (basket+weights), `GET /heatmap?route_date=` — mock. |
| `api/v1/elasticity.py` | `GET /?route_id=&route_date=` — mock. |
| `api/v1/quotes.py` | `GET /?route_id=&route_date=&lead_time=&carrier=&limit=` (limit 1–500, default 50) — mock. |
| `api/v1/backtest.py` | `GET /` → `{monthly[], summary{mape,rmse,corr}}` — mock. |
| `schemas/responses.py` | Pydantic response models: `ApixDailyResponse`, `RouteResponse`, `HeatmapResponse`, `ElasticityResponse`, `QuoteResponse`, `BacktestSummary`, `BacktestResponse` (kept in sync with `docs/api_reference.md`). |
| `services/mock_service.py` | `_load_mock(filename)` reads `data/mock/*.json`; getters per endpoint with light filtering (`get_mock_apix_daily` filters by date; `get_mock_quotes` truncates to limit; weekly/monthly currently just return daily; routes/heatmap share `heatmap.json`; backtest returns dict or empty defaults). |
| `tasks/scrape_tasks.py` | `run_daily_sweep()` (beat entry; currently `raise NotImplementedError("Owner: Sourabh/Abhay")`), `scrape_route(source, route_code, lead_time)` (stub). |
| `tasks/pipeline_tasks.py` | `clean_and_load(scrape_date)` (stub, Owner: Vanshika). |
| `tasks/index_tasks.py` | `compute_daily_index(compute_date)` (stub, Owner: Sourabh/Abhay). |

Conventions (from `app/README.md`): never query DB directly in routers; ISO-8601 dates; INR
floats rounded to 2 dp; FastAPI-style `{"detail": ...}` errors; keep `MOCK_MODE` working
forever as the demo safety net.

### 7.2 `scrapers/` — Stealth scraping engine **(Owners: Sourabh + Abhay, Yuvraj supports)**

| File | Contents |
|---|---|
| `base_scraper.py` | Dataclasses: `ScrapeJob(source, origin, destination, depart_date, lead_time, scrape_date)`, `ScrapeResult(job, ok, status_code, payload, error, fetched_at, method="curl_cffi"\|"playwright", proxy_used, raw_path)`, `RequestSpec(url, method, headers, json_body, params)`. `BaseScraper(ABC)` with `rate_limit_rps = 0.33` (1 req/3 s), abstract `build_request()` / `parse_ok()`, **stub** `fetch()` (planned loop: build → curl_cffi → tenacity retries max 4 on 403/429/5xx with new proxy → Playwright fallback → `storage.save_raw`), and working `run_jobs()` (sequential execution with per-job exception capture). |
| `indigo.py` | `IndigoScraper` — endpoint/headers/body **TODO after recon**; `build_request`/`parse_ok` raise `NotImplementedError`. Module docstring is a recon how-to (DevTools → XHR → Copy as cURL). |
| `makemytrip.py` | `MakeMyTripScraper` — same state; notes heavier Akamai anti-bot; strategy: Playwright token bootstrap then reuse cookies with curl_cffi. |
| `airindia.py` | Stub class, post-MVP. |
| `registry.py` | `SCRAPERS` dict (`indigo`, `makemytrip`, `airindia`; Akasa/EaseMyTrip commented out); `get_scraper(name)`; **working** `build_jobs_for_date()` — reads `config/routes.yaml` + `config/sources.yaml`, yields 6×5×enabled-sources jobs. |
| `proxy_manager.py` | **Working** `ProxyManager`: parses comma-separated `PROXY_URL`; `get()` round-robin skipping proxies in cooldown (falls back to direct); `mark_bad(proxy, cooldown=60s)`; `backoff(status)` → 429: 30 s, 403/401: 60 s, 5xx: 10 s. |
| `session_manager.py` | **Working** `SessionManager`: JSON cookie/token persistence per source at `data/raw/.sessions/{source}.json`; `load`/`save`/`clear` with error tolerance. |
| `fingerprints.py` | **Working** `IMPERSONATE_PROFILES = [chrome120, chrome124, safari17_0, edge101]`, literal UA list, `STANDARD_HEADERS` (Accept, Sec-Fetch-*, etc.); `get_random_profile()`, `get_headers_for_profile()`. |
| `playwright_fallback.py` | **Stub** `async fetch_with_browser(job, scraper_instance)` — plan: headless Chromium + `stealth_async`, intercept XHR responses via `page.on("response")` (never DOM-scrape). |
| `storage.py` | **Working** `save_raw(result)` → `data/raw/{source}/{scrape_date}/{ORIGIN}-{DEST}_T{lead}.json`; sets `result.raw_path`; DB insert into `raw_quotes` is commented-out TODO (must never crash scrape if DB is down). |
| `recon/` | Endpoint reconnaissance notes (`.gitkeep` + `README.md` template for `indigo_endpoint.md`, `makemytrip_endpoint.md`; `*.har`/`*.json` gitignored). |

Priority order: **IndiGo → MakeMyTrip → Air India → Akasa → EaseMyTrip**; two working sources
is MVP. Rate-limit rule: ≤ 1 req/3 s per source per IP with 1–4 s jitter.

### 7.3 `pipeline/` — Cleaning, validation & unbundling **(Owner: Vanshika)**

| File | Contents |
|---|---|
| `schemas.py` | **The frozen data contract** (see §6). |
| `parsers/indigo_parser.py` | **Stub** `parse(payload, job_meta) -> list[RawQuote]`; documented expected response shape; returns `[]` with warning. Has a helper `_parse_depart_time`. |
| `parsers/makemytrip_parser.py` | **Stub**; same pattern, documented `searchResult.flightOffers` shape. |
| `validators.py` | **Working** `validate_raw(q)`: rejects non-positive fare, `depart_date <= scrape_date`, lead-time mismatch vs `(depart - scrape).days`, carrier not in `ALLOWED_CARRIERS = {"6E","AI","QP","SG","UK","G8","I5"}`, non-INR currency. Returns `None` + warning log. |
| `unbundler.py` | **Working** `unbundle(RawQuote) -> CleanQuote` (mapping tables + regex fallback + sum check, see §6). |
| `cleaner.py` | **Working** Polars functions: `dedupe()` on `(source, route_code, carrier, flight_no, depart_date, scrape_date, fare_class)` keep-first; `iqr_filter()` grouped by `(route_code, lead_time, scrape_date)`, k=1.5 on `total_fare`, groups < 4 rows never flagged, sets `quality_flag="iqr_outlier"`; `flag_sold_out()`; `clean_batch()` orchestrates all three with a quality-flag distribution log. |
| `loader.py` | **Stub** `load(df) -> int` — PostgreSQL upsert into `fare_quotes` (SQLAlchemy `insert ... on_conflict_do_update`) is commented TODO; currently logs "would insert N" and returns N. |
| `run.py` | **Working CLI** `python -m pipeline.run --date YYYY-MM-DD [--source X] [--dry-run]`: walks `data/raw/{source}/{date}/*.json`, applies parser → validate → unbundle → clean_batch → load; prints counts for parsed / valid / unbundled / outliers / loaded. |

Definition of done: ≥ 90 % of valid quotes load with `quality_flag="ok"`.

### 7.4 `db/` — TimescaleDB models, migrations, seeds **(Owners: Sourabh + Abhay)**

| File | Contents |
|---|---|
| `session.py` | `Base(DeclarativeBase)` (**class-based** — the latest fix commit), engine from `settings.DATABASE_URL` (`pool_pre_ping=True`), `SessionLocal`, `get_db()`. |
| `models.py` | Six SQLAlchemy 2 models (details below). |
| `init.sql` | `CREATE EXTENSION IF NOT EXISTS timescaledb;` mounted into the db container's init dir. Hypertable conversion deferred to the first Alembic migration. |
| `migrations/env.py` | Alembic env wired to `settings.DATABASE_URL`, imports all models into `target_metadata`. |
| `migrations/script.py.mako` | Alembic template. |
| `migrations/versions/` | **Empty** (only `.gitkeep`) — the first migration (create tables + `create_hypertable('fare_quotes','scraped_at')`) has **not** been generated yet. |
| `seed.py` | **Working** `seed()`: `Base.metadata.create_all` (also used by scripts) + `seed_routes()` from `config/routes.yaml` (idempotent) + `seed_dgca_weights()` from `config/dgca_weights.csv`. |

**Table schemas:**

- **`routes`** — `id PK, route_code (unique, indexed), origin, destination, o_lat, o_lon, d_lat, d_lon, active`; relationships to raw_quotes/fare_quotes/dgca_weights.
- **`raw_quotes`** (audit/landing) — `id PK, source, route_id FK, scrape_date, depart_date, lead_time, fetched_at, status_code, method ("curl_cffi"/"playwright"), proxy_used, raw_path, payload JSONB`.
- **`fare_quotes`** — **hypertable on `scraped_at`** — `id PK, route_id FK (idx), carrier (idx), flight_no, depart_date, depart_time, lead_time (idx), fare_class, base_fare, udf, taxes, convenience_fee, other_fees, total_fare, currency="INR", is_refundable, stops, source, scraped_at (idx), raw_quote_id FK, quality_flag="ok"`.
- **`apix_daily`** — `date PK, apix, apix_base_only, n_quotes, n_routes, method="laspeyres", base_period`.
- **`dgca_weights`** — `id PK, route_id FK, period ("2025-01"), passengers, weight`.
- **`dgca_benchmark`** — `month PK ("2025-01"), avg_fare, source_url`.

Rules: schema changes go through Alembic migrations (never hand-edit); **UTC everywhere** —
convert to IST only in the frontend.

### 7.5 `engine/` — Index math, elasticity & backtest **(Owners: Sourabh + Abhay)**

| File | Contents |
|---|---|
| `index_calculator.py` | **Working** `laspeyres(p_t, p_0, q_0)` (guards zero denominator → 100), **working** `geometric_young(...)` (log-form), **stub** `compute_daily(date, session, lead_times=(1,7,15,30,45), price_agg="median")` — placeholder returns `apix=100.0, n_quotes=0, n_routes=6, base_period="placeholder"`; real DB path (median via `percentile_cont(0.5)`, weights, base prices, `session.merge` into `apix_daily`) is commented out. |
| `weights.py` | **Working** `load_weights(csv)` — reads `config/dgca_weights.csv`, normalises to sum 1, logs; **stub** `get_base_period_prices(session, n_days=7)` — placeholder equal prices per route. |
| `aggregator.py` | **Working** `pct_change()`, `daily_with_pct()` (day-over-day series); **stubs** `weekly_rollup()`, `monthly_rollup()` (SQL with `date_trunc` commented out; return `[]`). |
| `elasticity.py` | **Working** `compute_elasticity_coefficient(fares, lead_times)` — log-log `scipy.stats.linregress` slope; **stub** `compute_elasticity(session, route_id, route_date)` — placeholder linear values (fares rise as lead time shrinks). |
| `backtest.py` | **Working** metric helpers `compute_mape`, `compute_rmse`, `compute_correlation` (numpy); **stub** `run_backtest(session)` — placeholder 3-month series (MAPE 0.5, RMSE 25, r 0.98) written to `data/backtest_results.json`. |
| `run.py` | **Working CLI**: `--date` → `compute_daily`; `--backtest` → `run_backtest`; `--rebuild` flag accepted (unused). |

### 7.6 `config/` — Static configuration **(Owner: Yuvraj)**

- **`routes.yaml`** — 6-route basket with airport lat/lon and `lead_times: [1,7,15,30,45]`:

  | Route | Origin → Destination | DGCA weight (csv) |
  |---|---|---|
  | DEL-BOM | Delhi → Mumbai | 0.25 |
  | DEL-BLR | Delhi → Bengaluru | 0.20 |
  | BOM-BLR | Mumbai → Bengaluru | 0.16 |
  | DEL-CCU | Delhi → Kolkata | 0.14 |
  | BLR-HYD | Bengaluru → Hyderabad | 0.12 |
  | MAA-DEL | Chennai → Delhi | 0.14 |

- **`sources.yaml`** — per-source `enabled / rate_limit_rps=0.33 / max_retries=4 / use_playwright_fallback / robots_paths_checked`. Currently enabled: **indigo**, **makemytrip**; disabled: airindia, akasa, easemytrip.
- **`dgca_weights.csv`** — `route_code, period=2025-01, passengers (1.2M…550K), weight` — **placeholder values**; replace with real DGCA monthly traffic.
- Principle: *everything that is "a list of things we track" lives here, never hard-coded.*

### 7.7 `frontend/` — APIx Dashboard **(Owner: Mehak)**

**Setup:** Vite dev server on :5173 proxying `/api` → `http://localhost:8000`; env via
`frontend/.env.example` → `VITE_API_BASE=/api/v1`, `VITE_API_TOKEN=...` (default fallback
`change-me-dev-token` in code).

**File map:**
| File | Role |
|---|---|
| `index.html` | Shell; loads Leaflet CSS from unpkg; title "APIx — Airfare Price Index Dashboard". |
| `src/main.jsx` | React 18 StrictMode root. |
| `src/App.jsx` | Header (APIx + SIH26056 + MoSPI/NSO) + `<Dashboard/>`. |
| `src/pages/Dashboard.jsx` | State `timeRange`; `useApixDaily`; 4 `MetricCard`s (APIx Today, Routes Tracked, Quotes Processed, Last Updated); chart grid (ApixTrend, Heatmap, ElasticityCurve, BacktestChart); UnbundlingInspector; loading/error states. |
| `src/api/client.js` | `apiFetch` wrapper adding `Authorization: Bearer`; 9 functions: `getApixDaily/Weekly/Monthly`, `getRoutes`, `getHeatmap`, `getElasticity`, `getQuotes`, `getBacktest`, `triggerSweep`. |
| `src/hooks/useApix.js` | 4 hooks (`useApixDaily`, `useHeatmap`, `useElasticity`, `useBacktest`) — fetch + loading + error with cancellation guards. |
| `src/components/MetricCard.jsx` | Headline metric + ↑/↓ % change (emerald/rose). |
| `src/components/ApixTrend.jsx` | Recharts LineChart; daily/weekly/monthly granularity toggle (state-local; only daily data is fed today); overlays `apix_base_only` dashed line when present. |
| `src/components/Heatmap.jsx` | react-leaflet map of India (zoom 5); `CircleMarker` airports + `Polyline` colored by volatility (green/amber/red), width ∝ `index_contrib`; popups with avg fare + volatility. |
| `src/components/ElasticityCurve.jsx` | Recharts ScatterChart fare vs lead time (total + base). |
| `src/components/BacktestChart.jsx` | LineChart APIx(rebased) vs DGCA avg fare; MAPE badge; RMSE + correlation footer. |
| `src/components/UnbundlingInspector.jsx` | Fetches 50 quotes, aggregates averages by carrier, renders a table of base/udf/taxes/convenience/other/total. |
| `src/components/TimeRangeFilter.jsx` | Presets 7d/30d/90d + custom date inputs. |
| `src/components/ExportButton.jsx` | CSV (papaparse) + JSON downloads of current data. |
| `src/utils/format.js` | `formatINR` (en-IN currency), `formatDateIST` (Asia/Kolkata tz), `formatPercent`, `formatNumber`. |
| `src/index.css` | Tailwind base/components/utilities + Inter font stack. |
| `src/mock/README.md` | Rule: **no JSON in the frontend** — mock data only from backend `data/mock/`. |

Conventions: never hard-code data; components stay dumb (hooks fetch); `npm run lint` and
`npm run build` must pass (CI).

### 7.8 `data/` — Datasets

| Folder | Contents | Git? |
|---|---|---|
| `raw/` | Scrape payloads `{source}/{date}/{ROUTE}_T{lead}.json` + `.sessions/` | **No** (gitignored, `.gitkeep` only) |
| `mock/` | Realistic fake API responses (**committed**): `apix_daily.json` (45 days, 361 lines), `fare_quotes.json` (90 quotes, 1711 lines, generated 2026-09-04), `heatmap.json` (6 routes), `elasticity.json` (5 lead times), `backtest.json` (3 months: MAPE 1.61 %, RMSE 36.46, r 0.9502) | Yes |
| `reference/` | `airports.csv` (6 IATA coords), `dgca_monthly_avg_fare.csv` (placeholder weights) | Yes (small only) |

Mock shapes must match `pipeline/schemas.py` + `app/schemas/responses.py`; regenerated
deterministically (seed 42) by `make mock-data`.

### 7.9 `tests/` — pytest suite (15 tests)

| File | Tests | What they cover |
|---|---|---|
| `test_app/test_health.py` | 4 | `/health` 200 + fields; no-auth required for health; API 401 without token; 200 with token |
| `test_db/test_models.py` | 2 | All 6 models importable; correct `__tablename__`s |
| `test_engine/test_index_calculator.py` | 4 | Laspeyres = 100 at base; >100 on +10 % prices (≈110); <100 on −10 % (≈90); Geometric Young = 100 at base |
| `test_pipeline/test_unbundler.py` | 4 | `validate_raw` accepts valid; rejects negative fare; `unbundle` maps labels correctly |
| `test_scrapers/test_base.py` | 4 | ScrapeJob/ScrapeResult creation; registry has indigo + makemytrip |
| `tests/conftest.py` | — | Fixtures: `sample_raw_quote`, `sample_clean_quote`, `sample_indigo_fixture`, `sample_makemytrip_fixture` |
| `tests/fixtures/` | — | `indigo_sample.json` / `makemytrip_sample.json` — **placeholders** (docstring only), awaiting real recon captures |

Marker: `integration` (excluded in CI). Rules: mirror package layout; scraper tests never hit
the network (respx/monkeypatch); ≥1 test per public function; PRs without tests bounce.

### 7.10 `scripts/`

- `generate_mock_data.py` — deterministic (seed 42) generator for the 5 mock JSON files;
  models lead-time fare decay (T+1 ≈ 1.8× T+45) and daily index drift.
- `run_local_sweep.sh` — one-off scrape wrapper: `bash scripts/run_local_sweep.sh DEL-BOM 7 indigo`.
- `wait_for_db.sh` — pg_isready poller (used by compose flows).

### 7.11 `docs/`, `slides/`, `demo/` **(Owner: Sneh)**

- `docs/README.md` — plan for `architecture.md` (≤ 2 pages), `api_reference.md`,
  `data_contract.md`, `index_methodology.md`, `ethics_and_compliance.md`, `img/`.
  **All content files are still to be written.**
- `slides/README.md` — 5-slide pitch deck plan (`pitch_deck.pptx` + PDF): Problem → Scraping
  & Stealth → Unbundling & Index Math → APIx vs DGCA → Impact & Roadmap. Not yet created.
- `demo/README.md` — 2-minute video shot list (`apix_demo.mp4`): hero → trigger sweep →
  pipeline → index → dashboard → Swagger/backtest → close. Not yet recorded.

### 7.12 `.github/` — CI/CD & templates

- `workflows/backend-ci.yml` — on push/PR to `main`: **Lint** job (Python 3.11, `ruff check`
  + `ruff format --check`) → **Test** job (`pytest -m "not integration"` with coverage,
  `PYTHONPATH=.`, artifacts `coverage.xml` + `report.xml`, 7-day retention).
- `workflows/frontend-ci.yml` — path-filtered to `frontend/**`: **Lint** (`npm ci` + `npm run
  lint`) → **Build** (`npm run build`, artifact `frontend-dist`, 1-day retention).
- `PULL_REQUEST_TEMPLATE.md` — What/Why/Module-Owner/How-Tested/Screenshots/Type-of-Change/
  Checklist (incl. "does NOT modify `pipeline/schemas.py`"; data-contract ping rule).
- `ISSUE_TEMPLATE/bug.md`, `ISSUE_TEMPLATE/task.md` — structured issue templates (module,
  assignee, priority P0–P3, acceptance criteria, blocked-by).
- `README.md` — notes; branch protection on `main`: PR required, 1 approval, CI green
  (recent remote commits removed this claim from the root README).

---

## 8. Index Methodology & Math

### DGCA-weighted Laspeyres (primary)
```
I_t = Σ_i (P_i,t × Q_i,0) / Σ_i (P_i,0 × Q_i,0) × 100
```
- `i` — route in the 6-route basket
- `P_i,t` — representative price of route i on day t = **median `total_fare`** across
  carriers & non-stop flights per lead time, then aggregated across lead times (default:
  simple mean of the 5 lead-time medians; optional lead-time weights from config)
- `Q_i,0` — **DGCA passenger volume weight** (base period), normalised to sum 1
- `P_i,0` — base-period price = mean over the **first 7 days** of collected data → index = 100
- `apix_base_only` — same index computed on `base_fare` only (isolates tax/fee inflation)

### Geometric Young (comparison/optional)
```
I_t = Π_i (P_i,t / P_i,0)^(Q_i,0) × 100
```

### Elasticity
`elasticity = d ln(P) / d ln(lead_time)` via `scipy.stats.linregress` on the
(lead_time, median fare) points — negative slope ⇒ advance-purchase discount (T+1 ≈ 1.8× T+45).

### Backtest metrics
- **MAPE** — Mean Absolute Percentage Error (`|actual−predicted|/actual × 100`)
- **RMSE** — Root Mean Square Error
- **Pearson r** — correlation between APIx-implied monthly fares and DGCA monthly average fares

Backtest strategy (from `engine/README.md`): since the past can't be scraped, combine 30+
days of live collection with synthetic back-fill from public historical fare datasets, and be
explicit about which in `docs/index_methodology.md`.

---

## 9. API Reference

Base URL `http://localhost:8000`, all endpoints under `/api/v1` require
`Authorization: Bearer <token>` (except `/health` and `/docs`).

| Method | Endpoint | Description | Params |
|---|---|---|---|
| GET | `/health` | Health check → `{status:"ok", mock_mode:true, version:"0.1.0"}` | — |
| GET | `/api/v1/apix/daily` | Daily APIx | `from_date`, `to_date` |
| GET | `/api/v1/apix/weekly` | Weekly rollup | `from_date`, `to_date` |
| GET | `/api/v1/apix/monthly` | Monthly rollup | `from_date`, `to_date` |
| GET | `/api/v1/routes` | Sector basket + weights | — |
| GET | `/api/v1/routes/heatmap` | Per-route heatmap (avg fare, volatility, lat/lon) | `route_date` |
| GET | `/api/v1/elasticity` | Lead-time elasticity matrix | `route_id`, `route_date` |
| GET | `/api/v1/quotes` | Clean quotes (paginated) | `route_id`, `route_date`, `lead_time`, `carrier`, `limit` (1–500, default 50) |
| GET | `/api/v1/backtest` | APIx vs DGCA + MAPE/RMSE/r | — |
| POST | `/api/v1/admin/trigger-sweep` | Enqueue `run_daily_sweep` (planned demo button) | — |

*Note: `trigger-sweep` exists in the frontend client (`triggerSweep()`) and README but is
**not yet registered** in `router.py`.*

Example daily response:
```json
[
  {
    "date": "2025-01-15",
    "apix": 102.3456,
    "apix_base_only": 101.8923,
    "pct_change_dod": 0.23,
    "n_quotes": 24,
    "n_routes": 6
  }
]
```
Swagger UI: `http://localhost:8000/docs`. Frontend dev proxy: `localhost:5173/api/*` → `:8000`.

---

## 10. Celery Task Orchestration

- **App:** `app.core.celery_app.celery` — name `"apix"`, Redis broker + backend, JSON
  serialization, timezone `Asia/Kolkata`.
- **Beat:** single entry `daily-sweep` → `app.tasks.scrape_tasks.run_daily_sweep` at
  `crontab(hour=settings.SCRAPE_HOUR_IST=2, minute=0)` (02:00 IST nightly).
- **Planned chord:** `build_jobs_for_date()` → group of `scrape_route` tasks → callback
  `clean_and_load` → `compute_daily_index`. All three tasks are currently stubs.
- **Queues:** worker starts with `-Q default,scrape`.
- **Monitoring:** Flower at `:5555`.

---

## 11. Docker Infrastructure

`docker-compose.yml` — 8 services (7 default + MinIO behind the `audit` profile):

| Service | Image / build | Command | Ports | Notes |
|---|---|---|---|---|
| `db` | `timescale/timescaledb:latest-pg16` | — | 5432 | mounts `db/init.sql`; volume `pgdata`; pg_isready healthcheck; creds `apix/apix` |
| `redis` | `redis:7-alpine` | — | 6379 | |
| `api` | `build: .` | `uvicorn app.main:app --reload` | 8000 | `env_file: .env`; mounts repo + `data/`; depends on healthy db; `/health` curl healthcheck |
| `worker` | `build: .` | `celery -A app.core.celery_app worker -l info -Q default,scrape` | — | |
| `beat` | `build: .` | `celery -A app.core.celery_app beat -l info` | — | |
| `flower` | `build: .` | `celery -A app.core.celery_app flower --port=5555` | 5555 | |
| `frontend` | `node:20-alpine` | `npm install && npm run dev -- --host` | 5173 | |
| `minio` | `minio/minio` | `server /data --console-address ":9001"` | 9000/9001 | **profile `audit`** — optional object storage for raw payloads; creds `minio/minio123` |

`Dockerfile` (python:3.11-slim): `PYTHONDONTWRITEBYTECODE`/`PYTHONUNBUFFERED`/`PYTHONPATH=/app`;
curl/wget/gnupg for Playwright; `pip install -r requirements.txt`; optional
`playwright install --with-deps chromium` behind build-arg `INSTALL_PLAYWRIGHT=true` (default
on — heavy image); CMD uvicorn on 8000.

---

## 12. Configuration & Environment Variables

Loaded by pydantic-settings from `.env` (template in `.env.example`; team workflow copies
`.env.local` → `.env`). `frontend/.env` holds `VITE_API_BASE` / `VITE_API_TOKEN`.

| Variable | Default | Purpose |
|---|---|---|
| `APP_ENV` | `dev` | Environment label |
| `MOCK_MODE` | `true` | Serve `data/mock/*` instead of DB |
| `API_TOKEN` | `change-me-dev-token` | Bearer auth (real token in `.env.local`) |
| `POSTGRES_USER/PASSWORD/DB` | `apix` | DB credentials |
| `DATABASE_URL` | `postgresql+psycopg://apix:apix@db:5432/apix` | SQLAlchemy URL |
| `REDIS_URL` | `redis://redis:6379/0` | Celery broker/backend |
| `PROXY_ENABLED` | `false` | Toggle proxy rotation |
| `PROXY_URL` | *(empty)* | Comma-separated proxy list |
| `RAW_DATA_DIR` | `data/raw` | Raw payload storage root |
| `SCRAPE_HOUR_IST` | `2` | Nightly sweep hour |
| `LOG_LEVEL` | `INFO` | loguru level |
| `MINIO_ENDPOINT` / `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` | `minio:9000` / `minio` / `minio123` | Audit object storage |

---

## 13. Makefile & Developer Commands

| Target | Runs |
|---|---|
| `make setup` | `cp -n .env.example .env`; pip install dev deps; pre-commit install; `cd frontend && npm install` |
| `make up` / `make down` / `make logs` | docker compose up -d / down / logs -f |
| `make migrate` | `alembic -c db/migrations/env.py upgrade head` (inside api container) |
| `make seed` | `python -m db.seed` |
| `make mock-data` | `python scripts/generate_mock_data.py` |
| `make test` / `make test-cov` | pytest / pytest --cov |
| `make lint` | ruff check + frontend eslint |
| `make fmt` | ruff format + prettier |
| `make scrape ROUTE=… LEAD=… SOURCE=…` | `python -m app.tasks.scrape_tasks` |
| `make pipeline DATE=…` | `python -m pipeline.run --date …` |
| `make index DATE=…` / `make backtest` | `python -m engine.run` |
| `make shell` / `make psql` | api container bash / psql into db |

Local run without Docker: `uvicorn app.main:app --reload` + `celery -A app.core.celery_app
worker` + `celery ... beat`.

---

## 14. Testing Landscape

- `pytest` with `testpaths=["tests"]`; markers: `integration` (excluded by CI).
- 15 unit tests pass (verifiable with `make test`); CI additionally reports coverage with
  `--cov-report=term-missing`.
- Fixtures in `conftest.py`; placeholder vendor fixtures awaiting real recon captures.
- Planned additions per module READMEs: scraper retry/storage tests (mocked HTTP), parser
  tests, IQR outlier-injection test (₹99,999 fare), in-memory SQLite model tests, and the
  3-route hand-computed Laspeyres example (already partially covered).

---

## 15. CI/CD Pipeline

```
GitHub Actions (push/PR to main)
├─ Backend CI            └─ Frontend CI (paths: frontend/**)
│  ├─ Lint: ruff check + │  ├─ Lint: npm ci + eslint (max-warnings 0)
│  │     ruff format     │  └─ Build: npm run build → artifact frontend-dist
│  └─ Test: pytest -m    │
│       "not integration"│
│       + coverage →     │
│       coverage.xml,    │
│       report.xml       │
└────────────────────────┘
```
Branch protection on `main`: PR required, 1 approval, CI green (per `.github/README.md`;
recent remote README commits removed that claim from the root README).

---

## 16. Team, Ownership & Workflow

| Member | Role | Packages (per `CODEOWNERS`) |
|---|---|---|
| **Yuvraj** | Team Lead, Backend/DevOps | `app/`, `config/`, Docker/compose/Makefile, `.github/` |
| **Sourabh** | Scraping & DB | `scrapers/`, `db/`, `engine/` (+Yuvraj) |
| **Abhay** | Scraping & DB | `scrapers/`, `db/`, `engine/` (+Yuvraj) |
| **Vanshika** | Data Pipeline | `pipeline/` |
| **Mehak** | Frontend | `frontend/` |
| **Sneh** | Documentation | `docs/`, `slides/`, `demo/`, `README.md` |

Workflow rules (from `instructions-for-team.md`):
- Branch naming `feat/<name>/<topic>` / `fix/<name>/<topic>`; **never push/commit to main**.
- PR → CI green → review by Yuvraj → squash-merge.
- Folder ownership is strict (ask before touching another member's package).
- Daily 10-minute sync: done / doing / blocked.
- The API token in `.env.local` must not be shared outside the team.

---

## 17. Ethics & Compliance

- **Rate limiting:** ≤ 1 request / 3 s per source per IP (`rate_limit_rps = 0.33`), 1–4 s jitter.
- **robots.txt:** respected for all scraped paths; `robots_paths_checked` flag per source.
- **Off-peak:** scraping scheduled at 02:00 IST only.
- **No login / no booking:** anonymous search flows only — never books or holds seats.
- **Audit trail:** raw payloads retained (`data/raw/` + `raw_quotes` table + optional MinIO).
- **Privacy:** no personal data collected.
- Details destined for `docs/ethics_and_compliance.md` (not yet written).

---

## 18. Implementation Status: Done vs. Stub (Critical)

### ✅ Fully implemented & working
- FastAPI app: health, CORS, router mount, Bearer auth, all v1 endpoints serving mock data
- Mock service + deterministic mock data generator (seed 42)
- Celery app config + beat schedule (02:00 IST) + Flower
- Loguru logging setup
- Full DB model layer (6 tables) + session + seed script
- `laspeyres()` / `geometric_young()` math + their unit tests
- `load_weights()` / `pct_change()` / `daily_with_pct()` / `compute_elasticity_coefficient()` /
  `compute_mape` / `compute_rmse` / `compute_correlation`
- Pipeline: validators, unbundler (fee maps + regex fallback + sum check), cleaner
  (dedupe/IQR/sold-out), `run.py` CLI, `schemas.py` contract
- Scrapers: registry, job builder (6×5×enabled), proxy manager (rotation/cooldown/backoff),
  session manager, fingerprints, storage `save_raw`, `run_jobs`
- Entire frontend (7 components + hooks + client + utils)
- GitHub Actions (backend + frontend), PR/issue templates, pre-commit, Makefile, Docker stack

### ⚠️ Stubbed / not yet implemented (owner)
- `BaseScraper.fetch()` retry loop, `build_request()`/`parse_ok()` for IndiGo & MakeMyTrip
  (**Sourabh/Abhay**) — blocked on **endpoint recon** (DevTools capture → `scrapers/recon/*.md`
  → real fixtures)
- `playwright_fallback.fetch_with_browser()` (**Sourabh/Abhay**)
- `raw_quotes` DB insert in `storage.py` (**Sourabh/Abhay**)
- Source parsers `indigo_parser` / `makemytrip_parser` (**Vanshika**) — blocked on real fixtures
- `loader.load()` DB upsert (**Vanshika**) — blocked on models (models exist now)
- `compute_daily` / `get_base_period_prices` / weekly & monthly rollups / elasticity matrix /
  `run_backtest` real DB queries (**Sourabh/Abhay**)
- Celery tasks `run_daily_sweep`, `scrape_route`, `clean_and_load`, `compute_daily_index`
  (**Yuvraj wires with owners**)
- First Alembic migration incl. hypertable creation (**Sourabh/Abhay**)
- `POST /api/v1/admin/trigger-sweep` endpoint registration (client-side exists only)
- `db/queries.py` helper module (planned)
- `docs/*` content, slides deck, demo video (**Sneh**)
- 30+ day DGCA backtest with real data (in progress by design)

---

## 19. Deliverables Checklist State

| Deliverable | Status |
|---|---|
| Working prototype: scrape → clean → index → dashboard | **Partial** — demo path works via mock; real scrape chain stubbed |
| Cleaned, de-duplicated fare DB with unbundled fields | Models + cleaner done; loader/upsert pending |
| Laspeyres index module (daily; weekly/monthly rollups) | Math done; DB-backed daily/rollups pending |
| Interactive dashboard with 7 components | **Done** (mock-fed) |
| README + Docker setup + config docs | **Done** |
| Tests + CI/CD (GitHub Actions) | **Done** (15 tests, both pipelines) |
| 30+ day backtest vs DGCA | In progress |
| 2-page `docs/architecture.md` | Not started |
| 2-min demo video, 5-slide deck | Not started |

---

## 20. Known Gaps, TODOs & Roadmap

**Immediate next steps (Day-1 plan):**
1. Endpoint recon for IndiGo → MakeMyTrip (DevTools XHR capture, document in `recon/`,
   produce real `tests/fixtures/*.json`) — unblocks scrapers **and** parsers.
2. Generate the first Alembic migration + hypertable; `make migrate && make seed`; add
   `db/queries.py`.
3. Wire the Celery chord (sweep → scrape group → clean_and_load → compute_daily_index) and
   register `POST /admin/trigger-sweep`.
4. Implement `loader.py` against `FareQuote` and DB-backed `compute_daily`.

**Known wrinkles worth flagging:**
- `app/api/deps.py` duplicates `db/session.py` (engine/session) — consolidate later.
- `get_mock_apix_weekly/monthly` just echo daily data; `get_mock_quotes` ignores filters;
  `get_mock_routes` reuses `heatmap.json` (which lacks `weight`/`active` fields) — acceptable
  for demo, but the response schemas (`RouteResponse` requires `weight`, `active`) don't
  fully match mock shapes.
- `scripts/run_local_sweep.sh` invokes `python -m app.tasks.scrape_tasks` with CLI args, but
  `scrape_tasks.py` has **no argparse main** — the script will fail until tasks are built.
- The Docker image installs Playwright + Chromium by default (heavy); `INSTALL_PLAYWRIGHT=false`
  build-arg can slim it while it's unused.
- Frontend `ApixTrend` granularity toggle doesn't fetch weekly/monthly endpoints yet; the
  Heatmap falls back to hard-coded `AIRPORT_COORDS` (permitted fallback, API is source of truth).
- `engine/index_calculator.compute_daily` returns `n_routes=6` hard-coded in placeholder.

**Roadmap beyond MVP:** Air India/Akasa/EaseMyTrip scrapers; MinIO audit archive (compose
`audit` profile already exists); rate limiting + `X-Request-ID` + `generated_at` audit tags
on responses; continuous aggregates on the hypertable; scaling to the full DGCA basket;
public MoSPI/RBI-facing API.

---

*Document generated from a full repository audit — commit `5bcb2f7`, branch `main`, Sept 5, 2026.*