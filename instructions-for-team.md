# Instructions for Team — JetIndex (APIx)

**SIH26056 · Real-time Airfare Price Index for India**

> Read this fully before touching any code. If something is unclear, ask Yuvraj.

---

## What's Already Done (Infrastructure Complete)

I have completed the infrastructure layer. Here's what's ready for you:

| Component | Status | What it means for you |
|---|---|---|
| DB migration + hypertable | ✅ Done | `make migrate && make seed` works. `fare_quotes` is a TimescaleDB hypertable. |
| deps.py single source of truth | ✅ Done | No duplicate engine/session. Import from `db.session`. |
| Docker (Redis healthcheck) | ✅ Done | `docker compose up -d` is stable. Redis waits for health. |
| db/queries.py | ✅ Done | Centralised queries. Use these instead of raw SQLAlchemy. |
| Celery chord workflow | ✅ Done | `run_daily_sweep → scrape_route × N → clean_and_load → compute_daily_index` |
| POST /admin/trigger-sweep | ✅ Done | Frontend demo button works (mock mode returns simulated response). |
| GET /admin/status | ✅ Done | System health endpoint: scrape times, quote counts, index, coverage, quality distribution. |
| MOCK_MODE toggle (all endpoints) | ✅ Done | All 9 endpoints check `settings.MOCK_MODE`; mock branch (demo) + real DB branch wired. |
| IndiGo recon | ✅ Done | Full endpoint captured in `scrapers/recon/indigo_endpoint.md` |
| IndiGo + MMT build_request/parse_ok | ✅ Done | Implemented by Abhay in `scrapers/indigo.py` and `scrapers/makemytrip.py` |
| IndiGo parser | ✅ Done | `pipeline/parsers/indigo_parser.py` — parses real fixture (77 flights) |
| Real Indigo fixture | ✅ Done | 77 flights in `tests/fixtures/indigo_sample.json` (756 KB) |
| Integration tests | ✅ Done | 11 DB round-trip tests in `tests/test_integration/` |

---

## Common to All

### 1. Clone & Start (takes ~2 minutes)

```bash
git clone https://github.com/Yuvraj-Sarathe/JetIndex.git && cd JetIndex
cp .env.local .env          # ← use this exact file, do NOT create your own .env
make setup                  # installs python dev deps + pre-commit + npm ci 
docker compose up -d        # starts db, redis, api, worker, beat, flower, frontend
```

### 2. Verify Everything Works

| Check | Command / URL | Expected Result |
|---|---|---|
| API health | `curl http://localhost:8000/health` | `{"status":"ok","mock_mode":true,...}` |
| API docs | http://localhost:8000/docs | Swagger UI with all endpoints |
| Dashboard | http://localhost:5173 | React dashboard with MetricCard |
| Flower (Celery) | http://localhost:5555 | Celery monitoring panel |
| DB tables | `make psql` then `\dt+` | 6 tables + hypertable |
| Test auth | `curl -H "Authorization: Bearer SJSSF01-zSIe6SqSVBaVHx1kh7_jBNKUPyVUWtnw6eA" http://localhost:8000/api/v1/apix/daily` | JSON array |

### 3. The API Token

```
SJSSF01-zSIe6SqSVBaVHx1kh7_jBNKUPyVUWtnw6eA
```

- This is already in `.env` (copied from `.env.local`).
- **Do NOT share this outside the team.**
- Every API request needs: `Authorization: Bearer <token>`
- `/health` and `/docs` do NOT need the token.

### 4. Mock Mode

`MOCK_MODE=true` is set by default:
- The API serves **realistic fake data** from `data/mock/`.
- **No database is required** to see the dashboard working.
- Every endpoint has a **MOCK_MODE toggle** — when `MOCK_MODE=false`, endpoints call `db/queries.py` for real data.
- The mock branch stays forever as a demo safety net.

### 5. Branch Naming

```
feat/<yourname>/<topic>      # new features
fix/<yourname>/<topic>       # bug fixes
```

**NEVER PUSH/COMMIT ON MAIN BRANCH!!** We will merge your changes into main after approval, via PRs.

### 6. How to Submit Code

1. Create a branch from `main`
2. Make your changes
3. Run tests: `make test` (Python) or `cd frontend && npm run lint && npm run build` (frontend)
4. Push branch and open a Pull Request
5. **CI runs automatically** — lint + tests must pass
6. Request review from @Yuvraj-Sarathe
7. After approval, squash-merge into `main`

### 7. What NOT to Commit

- `.env` — contains secrets
- `data/raw/*` — raw scrape payloads
- `*.har` — network captures
- `node_modules/`, `__pycache__/`, `.venv/`

### 8. Common Commands

| What | Command |
|---|---|
| Start everything | `docker compose up -d` |
| Stop everything | `docker compose down` |
| View logs | `docker compose logs -f api` |
| Run unit tests | `make test` |
| Run integration tests | `make test-integration` |
| Lint Python | `ruff check .` |
| Format Python | `ruff format .` |
| Access database | `make psql` |
| Run migration | `make migrate` |
| Seed database | `make seed` |

### 9. Folder Ownership — Respect Boundaries

| Folder | Owner | You can edit? |
|---|---|---|
| `app/` | Yuvraj | ❌ Ask first |
| `config/` | Yuvraj | ❌ Ask first |
| `Dockerfile`, `docker-compose.yml`, `Makefile` | Yuvraj | ❌ Ask first |
| `scrapers/` | Sourabh + Abhay | ✅ If you're Sourabh or Abhay |
| `pipeline/` | Vanshika | ✅ If you're Vanshika |
| `db/`, `engine/` | Sourabh + Abhay | ✅ If you're Sourabh or Abhay |
| `frontend/` | Mehak | ✅ If you're Mehak |
| `docs/`, `slides/`, `demo/` | Sneh | ✅ If you're Sneh |

### 10. The Data Contract

`pipeline/schemas.py` is the **single source of truth** for all data structures. It is FROZEN.

- If you need to change it, open a PR tagged `data-contract` and ping Yuvraj + Vanshika.
- All API responses, database models, and frontend types must match this file.

### 11. Data Sources (Real DGCA Data)

The project uses **real DGCA data** for route weighting and backtesting. Do NOT use placeholder values.

**DGCA Passenger Traffic (FY 2024–25):**
- File: `config/dgca_weights.csv`
- 6 routes, total 23,163,234 passengers
- Weights: DEL-BOM 0.2958, DEL-BLR 0.2021, BOM-BLR 0.1776, DEL-CCU 0.1196, MAA-DEL 0.1059, BLR-HYD 0.0990
- Source: DGCA "City Pair Wise Passenger Traffic" ([dgca.gov.in](https://dgca.gov.in))

**DGCA Monthly Average Fares (Jan 2024 – Nov 2025):**
- File: `config/dgca_monthly_avg_fare.csv`
- 32 data points across 6 routes
- Source: Kaggle dataset ["India Aviation Traffic Data"](https://github.com/Vonter/india-aviation-traffic) by Vonter — compiled from DGCA published reports
- Note: DGCA's own portal hasn't been updated in recent years; this Kaggle aggregation compiles the same DGCA reports

### 12. Database Queries

**Use `db/queries.py`** for all database access. Do NOT write raw SQLAlchemy in your modules.

```python
# ✅ Correct
from db.queries import get_active_routes, get_median_fares_by_route
routes = get_active_routes(session)

# ❌ Wrong
from sqlalchemy import select
from db.models import Route
routes = session.scalars(select(Route).where(Route.active == True)).all()
```

---

## Person-Specific Instructions

---

### Sourabh + Abhay — Scrapers, DB & Engine

**Your packages:** `scrapers/`, `db/`, `engine/`

**What I already did for you:**
- IndiGo endpoint recon captured in `scrapers/recon/indigo_endpoint.md`
- Real Indigo fixture saved in `tests/fixtures/indigo_sample.json` (77 flights, 756 KB)
- DB migration + hypertable ready (`make migrate && make seed`)
- `db/queries.py` ready for engine queries
- IndiGo + MakeMyTrip `build_request()`/`parse_ok()` implemented (by Abhay)
- IndiGo parser implemented in `pipeline/parsers/indigo_parser.py`

#### Your Tasks (Priority Order)

**1. ~~Implement `indigo.py`~~ ✅ DONE** (by Abhay)

**2. ~~Do MakeMyTrip recon~~ ✅ DONE** (in `scrapers/recon/makemytrip_endpoint.md`)

**3. ~~Implement `makemytrip.py`~~ ✅ DONE** (by Abhay)

**4. Implement engine queries**
   - Replace `compute_daily()` placeholder with real DB queries
   - Use `db/queries.get_median_fares_by_route()` for prices
   - Use `db/queries.get_weights()` for DGCA weights
   - Use `db/queries.get_base_period_prices()` for base prices
   - Use `db/queries.upsert_apix_daily()` to write results

**5. Add tests**
   - `tests/test_scrapers/test_indigo.py` — test build_request, parse_ok
   - `tests/test_engine/test_compute_daily.py` — test with mock DB

#### IndiGo Reconstruct Reference

The endpoint is:
```
POST https://api-prod-flight-skyplus6e.goindigo.in/v2/flight/search
```

Key headers:
- `authorization: <JWT token>` (expires ~15 min)
- `user_key: 31e90be8fff2f5e2eea242c225f21b1a`
- `content-type: application/json`

Request body shape:
```json
{
  "codes": {"currency": "INR", "promotionCode": ""},
  "criteria": [{"dates": {"beginDate": "2026-10-13"}, "stations": {"originStationCodes": ["DEL"], "destinationStationCodes": ["BOM"]}}],
  "passengers": {"residentCountry": "IN", "types": [{"count": 1, "type": "ADT"}]},
  "tripCriteria": "oneWay"
}
```

Response path: `data.trips[0].journeysAvailable[]` — each has `designator` (times) and `passengerFares` (pricing).

#### Your Definition of Done

- `python -m app.tasks.scrape_tasks --route DEL-BOM --lead 7 --source indigo` returns OK
- `python -m app.tasks.scrape_tasks --route DEL-BOM --lead 7 --source makemytrip` returns OK
- `make index DATE=...` writes real data to `apix_daily`
- Tests in `tests/test_scrapers/`, `tests/test_engine/`

---

### Vanshika — Pipeline (Data Cleaning & Unbundling)

**Your package:** `pipeline/`

**What I already did for you:**
- Real Indigo fixture in `tests/fixtures/indigo_sample.json` (77 flights)
- Fixture is a flat array matching `RawQuote` schema — ready to parse
- `db/queries.py` has `upsert_fare_quotes()` for loading data

#### Your Tasks

**1. Review the real fixture**
   - Open `tests/fixtures/indigo_sample.json`
   - See how IndiGo data is structured (carrier, flight_no, fare_breakdown, etc.)
   - Compare with `pipeline/schemas.py` — the fixture already maps to `RawQuote`

**2. Implement `indigo_parser.py`**
   - Parse the flat array from the fixture
   - Map each item to `RawQuote`:
     - `source` → `"indigo"`
     - `route_code` → from fixture
     - `carrier` → `"6E"` (IndiGo)
     - `flight_no` → extract from `flight_no` field
     - `fare_breakdown` → use `fare_breakdown` from fixture
   - Test: `python -c "from pipeline.parsers.indigo_parser import parse; ..."`

**3. Implement `loader.py`**
   - Use `db.queries.upsert_fare_quotes()` to load data
   - Convert Polars DataFrame rows to dicts for upsert

**4. Test the full pipeline**
   ```bash
   python -m pipeline.run --date 2026-10-13
   ```
   - Should parse → validate → unbundle → clean → load
   - Verify data in DB: `make psql` then `SELECT COUNT(*) FROM fare_quotes;`

#### Your Definition of Done

- `python -m pipeline.run --date 2026-10-13` loads ≥ 90% of valid quotes
- Unit tests in `tests/test_pipeline/`
- `docs/data_contract.md` matches `schemas.py`

---

### Mehak — Frontend Dashboard

**Your package:** `frontend/`

**What's ready for you:**
- All endpoints return realistic mock data from Day 1
- POST /admin/trigger-sweep is registered (demo button works)

#### Setup

```bash
cd frontend
cp .env.example .env        # VITE_API_BASE=/api/v1
npm install
npm run dev                  # http://localhost:5173
```

#### Tasks

1. **Verify dashboard loads** — MetricCard shows mock APIx value
2. **Build in order:**
   - `MetricCard.jsx`
   - `ApixTrend.jsx` + `TimeRangeFilter.jsx`
   - `Heatmap.jsx` (Leaflet Polyline + CircleMarker)
   - `ElasticityCurve.jsx`
   - `UnbundlingInspector.jsx`
   - `BacktestChart.jsx`
   - `ExportButton.jsx`

#### Rules

- **Never hard-code data** — always fetch from API via `src/api/client.js`
- Colors: Tailwind `slate` base, `indigo` accent, `emerald`/`rose` for up/down
- Format money with `utils/format.js` (`₹4,250`)
- `npm run lint` and `npm run build` must pass (CI checks this)

#### Your Definition of Done

- Dashboard renders all 7 components with mock data
- Time range filter works (7d/30d/90d/custom)
- CSV + JSON export works
- `npm run lint && npm run build` pass
- Screenshots for Sneh's slides

---

### Sneh — Documentation, Pitch & Demo

**Your packages:** `docs/`, `slides/`, `demo/`, root `README.md`

**What's ready for you:**
- Root `README.md` is comprehensive (architecture, API, team)
- `PROJECT.md` has full project state
- Architecture diagram in README

#### Tasks

1. **Read everything**
   - This file
   - `README.md` (root) — already has architecture diagram
   - `PROJECT.md` — full project state

2. **Draft `docs/architecture.md`** (max 2 pages)
   - Problem → Architecture → Pipeline → Schema → Index math → Backtest
   - Use the ASCII diagram from README as starting point

3. **Collect from owners:**
   - API examples & screenshots (Yuvraj)
   - Schema documentation (Vanshika)
   - Formula + backtest numbers (Sourabh/Abhay)
   - Dashboard screenshots (Mehak)

4. **Build `slides/pitch_deck.pptx`** (5 slides)
   1. Problem — manual counters vs 90% online
   2. Scraping & Stealth — curl_cffi, XHR interception, ethics
   3. Unbundling & Index Math — base/UDF/tax/fee split, Laspeyres
   4. APIx vs DGCA — backtest chart, MAPE
   5. Impact & Roadmap — MoSPI/RBI API, dashboard screenshot

5. **Record the demo** (2 min, OBS/Loom, captions on)

#### Your Definition of Done

- `docs/architecture.md` ≤ 2 pages, exported to PDF
- `slides/pitch_deck.pptx` (5 slides) + PDF
- `demo/apix_demo.mp4` ≤ 2 min, 1080p

---

## Quick Reference

| Service | URL | Auth |
|---|---|---|
| API | http://localhost:8000 | Bearer token |
| API Docs | http://localhost:8000/docs | Paste token in authorize box |
| Dashboard | http://localhost:5173 | None (uses env token) |
| Flower | http://localhost:5555 | None |
| Database | `localhost:5432` | `apix` / `apix` |

---

*Last updated: Sept 6, 2026. Infrastructure complete, scrapers implemented, integration tests added.*
