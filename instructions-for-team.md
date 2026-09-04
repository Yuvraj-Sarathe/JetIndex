# Instructions for Team — JetIndex (APIx)

**SIH26056 · Real-time Airfare Price Index for India**

> Read this fully before touching any code. If something is unclear, ask me(Yuvraj).

---

## Common to All

### 1. Clone & Start (takes ~2 minutes)

```bash
git clone <repo-url> jetindex && cd jetindex # or just use github desktop
cp .env.local .env          # ← use this exact file, do NOT create your own .env
make setup                  # installs python dev deps + pre-commit + npm ci 
docker compose up -d        # starts db, redis, api, worker, beat, flower, frontend (make sure you ahve docker)
```

### 2. Verify Everything Works

| Check | Command / URL | Expected Result |
|---|---|---|
| API health | `curl http://localhost:8000/health` | `{"status":"ok","mock_mode":true,...}` |
| API docs | http://localhost:8000/docs | Swagger UI with all endpoints listed |
| Dashboard | http://localhost:5173 | React dashboard with MetricCard showing mock APIx value |
| Flower (Celery) | http://localhost:5555 | Celery monitoring panel |
| Test auth | `curl -H "Authorization: Bearer SJSSF01-zSIe6SqSVBaVHx1kh7_jBNKUPyVUWtnw6eA" http://localhost:8000/api/v1/apix/daily` | JSON array of daily index values |

### 3. The API Token

```
SJSSF01-zSIe6SqSVBaVHx1kh7_jBNKUPyVUWtnw6eA
```

- This is already in `.env` (copied from `.env.local`).
- **Do NOT share this outside the team.**
- Every API request needs this header: `Authorization: Bearer <token>`
- The `/health` and `/docs` endpoints do NOT need the token.

### 4. Mock Mode

`MOCK_MODE=true` is set by default. This means:

- The API serves **realistic fake data** from `data/mock/`.
- **No database is required** to see the dashboard working.
- You can start frontend/docs work immediately on Day 1.
- When real scraping data exists, I will flip to `MOCK_MODE=false`.

### 5. Branch Naming

```
feat/<yourname>/<topic>      # new features
fix/<yourname>/<topic>       # bug fixes
```

Examples:
- `feat/sourabh/indigo-scraper`
- `feat/vanshika/indigo-parser`
- `feat/mehak/heatmap-component`
- `fix/yuvraj/celery-beat-schedule`
**NEVER PUSH/COMMIT ON MAIN BRANCH!! We will merge your changes into main after approval, via PRs.**

### 6. How to Submit Code

1. Create a branch from `main` (see branch naming above)
2. Make your changes
3. Run tests locally: `make test` (Python) or `cd frontend && npm run lint && npm run build` (frontend)
4. Push branch and open a Pull Request on GitHub
5. **CI will run automatically** — lint + tests must pass before merge (check the Actions tab)
6. Request review from @Yuvraj-Sarathe
7. After approval, squash-merge into `main`

> **CI Pipeline:** Every PR triggers GitHub Actions:
> - **Python:** ruff lint → pytest with coverage
> - **Frontend:** eslint → build check
> If CI fails, fix it before asking for review.

### 7. What NOT to Commit

- `.env` — contains secrets
- `data/raw/*` — raw scrape payloads
- `*.har` — network captures
- `node_modules/` — installed by npm
- `__pycache__/` — Python bytecode
- `.venv/` — virtual environment

All of these are in `.gitignore` already. If you see a file you're unsure about, ask before committing.

### 8. Testing

```bash
# Python tests (from repo root)
make test

# Frontend lint + build check
cd frontend && npm run lint && npm run build
```

- Every new function you write needs at least one test.
- Scraper tests must **never hit the network** — mock HTTP calls.
- PRs without tests will be sent back.

### 9. Common Commands

| What | Command |
|---|---|
| Start everything | `docker compose up -d` |
| Stop everything | `docker compose down` |
| View logs | `docker compose logs -f api` |
| Run tests | `make test` |
| Lint Python | `ruff check .` |
| Format Python | `ruff format .` |
| Lint frontend | `cd frontend && npm run lint` |
| Access database shell | `make psql` |
| Access API container bash | `make shell` |

### 10. Folder Ownership — Respect Boundaries

| Folder | Owner | You can edit? |
|---|---|---|
| `app/` | Yuvraj | ❌ Ask first |
| `config/` | Yuvraj | ❌ Ask first |
| `Dockerfile`, `docker-compose.yml`, `Makefile` | Yuvraj | ❌ Ask first |
| `scrapers/` | Sourabh + Abhay (+ Yuvraj) | ✅ If you're Sourabh or Abhay |
| `pipeline/` | Vanshika | ✅ If you're Vanshika |
| `db/`, `engine/` | Sourabh + Abhay (+ Yuvraj) | ✅ If you're Sourabh or Abhay |
| `frontend/` | Mehak | ✅ If you're Mehak |
| `docs/`, `slides/`, `demo/` | Sneh | ✅ If you're Sneh |
| `data/` | Shared (mock = Vanshika, raw = Sourabh/Abhay) | ✅ For your part |
| `tests/` | Everyone (write tests for YOUR module only) | ✅ For your tests |

### 11. The Data Contract

`pipeline/schemas.py` is the **single source of truth** for all data structures. It is FROZEN after Day 1.

- If you need to change it, open a PR tagged `data-contract` and ping Yuvraj + Vanshika.
- All API responses, database models, and frontend types must match this file.

### 12. Daily Sync

10 minutes every day:
1. What did you finish yesterday?
2. What are you working on today?
3. What's blocking you? Who do you need something from?

---

## Person-Specific Instructions

---

### Sourabh + Abhay — Scrapers, DB & Engine

**Your packages:** `scrapers/`, `db/`, `engine/`

#### Day 1 Tasks

1. **Recon — IndiGo endpoint discovery**
   - Open https://www.goindigo.in in Chrome
   - DevTools → Network → filter `Fetch/XHR`
   - Do a DEL → BOM one-way search
   - Find the response containing fare data
   - Right-click → "Copy as cURL (bash)"
   - Paste into `scrapers/recon/indigo_endpoint.md`
   - Note: URL, method, headers, body, auth token flow, response shape

2. **Recon — MakeMyTrip endpoint discovery**
   - Same process for https://www.makemytrip.com
   - Document in `scrapers/recon/makemytrip_endpoint.md`
   - MMT has heavier anti-bot (Akamai) — note any challenge pages

3. **Save a sample response**
   - Get one successful IndiGo response
   - Save to `tests/fixtures/indigo_sample.json` (strip personal data)
   - This unblocks Vanshika

#### Day 2+ Tasks

4. **Implement `indigo.py`**
   - Fill in endpoint URL, headers, body template from recon
   - Implement `build_request()` and `parse_ok()`
   - Test: `make scrape ROUTE=DEL-BOM LEAD=7 SOURCE=indigo`

5. **Implement `proxy_manager.py` and `session_manager.py`**
   - Test 403/429 handling

6. **DB setup**
   - Create first Alembic migration
   - Run `make migrate && make seed`
   - Verify `fare_quotes` is a hypertable

7. **Engine implementation**
   - Unit test `laspeyres()` with hand-computed example
   - Implement `compute_daily()` against mock data

#### Your Definition of Done

- `make scrape` works for IndiGo + MakeMyTrip, all 6 routes × 5 lead times
- Failure rate < 10% per sweep with retries
- `make migrate && make seed` creates all tables
- `make index DATE=...` writes `apix_daily`
- Tests in `tests/test_scrapers/`, `tests/test_db/`, `tests/test_engine/`

---

### Vanshika — Pipeline (Data Cleaning & Unbundling)

**Your package:** `pipeline/`

#### Day 1 Tasks

1. **Review `pipeline/schemas.py`**
   - This is the frozen data contract
   - `RawQuote` = raw scraper output
   - `CleanQuote` = normalised with unbundled components
   - Review the fee mapping tables in `unbundler.py`
   - If anything needs changing, flag it NOW — it freezes after today

2. **Generate mock data**
   ```bash
   python scripts/generate_mock_data.py
   ```
   - Verify `data/mock/fare_quotes.json` conforms to your schema

#### Day 2+ Tasks

3. **Write `indigo_parser.py`**
   - Parse the sample JSON from `tests/fixtures/indigo_sample.json`
   - Output: `list[RawQuote]` with vendor labels untouched in `fare_breakdown`
   - Test: parse → N RawQuote objects

4. **Write `unbundler.py` mapping**
   - Map IndiGo labels → canonical components (base_fare, udf, taxes, etc.)
   - Test that components sum to total (±₹5)

5. **Write `cleaner.py`**
   - `dedupe()`, `iqr_filter()`, `flag_sold_out()`
   - Test with an injected ₹99,999 fare → should be flagged `iqr_outlier`

6. **Repeat for MakeMyTrip** once Sourabh/Abhay provide the sample

#### Your Definition of Done

- `make pipeline DATE=<day>` loads ≥ 90% of valid quotes with `quality_flag="ok"`
- Unit tests in `tests/test_pipeline/` for parser, unbundler, IQR, dedupe
- `docs/data_contract.md` matches `schemas.py`

---

### Mehak — Frontend Dashboard

**Your package:** `frontend/`

#### Setup

```bash
cd frontend
cp .env.example .env        # VITE_API_BASE=/api/v1  VITE_API_TOKEN=SJSSF01-zSIe6SqSVBaVHx1kh7_jBNKUPyVUWtnw6eA
npm install
npm run dev                  # http://localhost:5173
```

The API runs in mock mode — **all endpoints return realistic data from Day 1.**

#### Day 1 Tasks

1. **Verify dashboard loads**
   - `npm run dev`
   - Confirm `MetricCard` shows a mock APIx value
   - Confirm no console errors

2. **Build in order:**
   - `MetricCard.jsx` ← verify it shows data
   - `ApixTrend.jsx` + `TimeRangeFilter.jsx` (they share state)
   - `Heatmap.jsx` (airports from `/routes`, use Leaflet Polyline + CircleMarker)
   - `ElasticityCurve.jsx`
   - `UnbundlingInspector.jsx`
   - `BacktestChart.jsx`
   - `ExportButton.jsx`

#### Rules

- **Never hard-code data** — always fetch from API via `src/api/client.js`
- Colors: Tailwind `slate` base, `indigo` accent, `emerald`/`rose` for up/down
- Format money with `utils/format.js` (`₹4,250`)
- Dates in IST for display
- Keep components dumb; data fetching in `hooks/useApix.js`
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

#### Day 1 Tasks

1. **Read everything**
   - Read this file (you just did)
   - Read every folder's `README.md` — they have your step-by-step briefs
   - Read `PRD.md` for the full picture

2. **Draft `docs/architecture.md` skeleton**
   - Max 2 pages
   - Structure: Problem → Architecture diagram → Pipeline → Schema → Stealth strategy → Index math → Backtest
   - Use diagrams from the SIH PDF

#### Day 2+ Tasks

3. **Collect from owners:**
   - API examples & OpenAPI screenshots (Yuvraj)
   - Schema documentation (Vanshika)
   - Formula + backtest numbers (Sourabh/Abhay)
   - Dashboard screenshots (Mehak)

4. **Rewrite root `README.md`**
   - 30-second pitch for judges
   - One-command run instructions
   - Screenshots of the working dashboard
   - Results (backtest numbers)

5. **Build `slides/pitch_deck.pptx`** (5 slides)
   1. Problem — manual counters vs 90% online, CPI blind spot
   2. Scraping & Stealth — curl_cffi, XHR interception, ethics
   3. Unbundling & Index Math — base/UDF/tax/fee split, Laspeyres
   4. APIx vs DGCA — backtest chart, MAPE
   5. Impact & Roadmap — MoSPI/RBI API, dashboard screenshot

6. **Write `demo/video_script.md`** (shot list for 2-min video)
   - 0:00 — Problem + dashboard hero shot
   - 0:15 — Trigger sweep, scraper logs
   - 0:45 — Raw JSON → pipeline output
   - 1:05 — `make index` → APIx value
   - 1:20 — Dashboard: trend, heatmap, elasticity
   - 1:45 — Swagger + backtest vs DGCA
   - 1:55 — Close

7. **Record the demo** (OBS/Loom, captions on, no music)

8. **Export `architecture.md` → PDF**, verify ≤ 2 pages

#### Your Definition of Done

- `docs/architecture.md` ≤ 2 pages, exported to PDF
- Root `README.md` rewritten for judges
- `slides/pitch_deck.pptx` (5 slides) + PDF export
- `demo/apix_demo.mp4` ≤ 2 min, 1080p
- All `docs/` files populated

---

## Quick Reference

| Service | URL | Auth |
|---|---|---|
| API | http://localhost:8000 | Bearer token in header |
| API Docs (Swagger) | http://localhost:8000/docs | Paste token in authorize box |
| Dashboard | http://localhost:5173 | None (uses env token) |
| Flower (Celery) | http://localhost:5555 | None |
| Database | `localhost:5432` | `apix` / `apix` |

| Token | Value |
|---|---|
| `API_TOKEN` | `SJSSF01-zSIe6SqSVBaVHx1kh7_jBNKUPyVUWtnw6eA` |

---

*Last updated by Yuvraj. Ping the group if anything is unclear.*
