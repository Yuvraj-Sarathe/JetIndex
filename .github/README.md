<div align="center">

# ✈️ JetIndex — APIx

### Real-time Airfare Price Index for India

**SIH26056 · MoSPI / NSO · Smart Automation / Macroeconomic Data Engineering**

[![Backend CI](https://github.com/Yuvraj-Sarathe/JetIndex/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Yuvraj-Sarathe/JetIndex/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/Yuvraj-Sarathe/JetIndex/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/Yuvraj-Sarathe/JetIndex/actions/workflows/frontend-ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🎯 Problem Statement

India's Consumer Price Index (CPI) relies on **manual ticket-counter price collection** for airfare data — a method that is:

- **Slow**: Monthly data collection misses daily price swings of 200–400%
- **Incomplete**: Covers only ~30% of bookings (offline counter sales)
- **Outdated**: By the time data reaches MoSPI/RBI, it's already stale
- **Expensive**: Requires manual labor at airport counters across India

With **90% of flight bookings now online**, there's a massive blind spot in macroeconomic data.

## 💡 Our Solution

**APIx** (Airfare Price Index) replaces manual collection with an automated pipeline:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Scrape    │───▶│   Clean     │───▶│   Store     │───▶│   Compute   │───▶│   Serve     │
│  (IndiGo,   │    │  (Unbundle, │    │ (TimescaleDB│    │ (Laspeyres  │    │ (FastAPI +  │
│  MakeMyTrip)│    │   IQR, etc) │    │  hypertable)│    │   Index)    │    │  Dashboard) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Key Innovation: Fare Unbundling

Unlike simple fare scraping, APIx **decomposes** each quote into:
- **Base Fare** — the actual ticket price
- **UDF** — User Development Fee (airport charges)
- **Taxes** — GST, PSF, ASF
- **Convenience Fee** — OTA platform charges
- **Other Fees** — fuel surcharge, meals, seats

This enables **component-level inflation tracking** — a first for India's airfare data.

---

## 🏗️ Architecture

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
                            │  │ curl_cff│  │ curl_cffi │  │ (stub) │ │
                            │  └────┬────┘  └─────┬─────┘  └────────┘ │
                            │       │             │                    │
                            │       ▼             ▼                    │
                            │  ┌─────────────────────────┐            │
                            │  │  Playwright Fallback     │            │
                            │  │  (stealth browser)       │            │
                            │  └────────────┬────────────┘            │
                            └───────────────┼─────────────────────────┘
                                            │
                                            ▼
                            ┌──────────────────────────────────────────┐
                            │           Data Pipeline                  │
                            │  Parse → Validate → Unbundle → IQR      │
                            │  ┌─────────────────────────────────┐    │
                            │  │  pipeline/schemas.py (FROZEN)   │    │
                            │  │  RawQuote → CleanQuote          │    │
                            │  └─────────────────────────────────┘    │
                            └───────────────┬─────────────────────────┘
                                            │
                                            ▼
                            ┌──────────────────────────────────────────┐
                            │         TimescaleDB (PostgreSQL)         │
                            │  ┌──────────┐  ┌───────────────────┐    │
                            │  │ raw_quotes│  │ fare_quotes       │    │
                            │  │ (audit)   │  │ (hypertable)      │    │
                            │  └──────────┘  └───────────────────┘    │
                            └───────────────┬─────────────────────────┘
                                            │
                                            ▼
                            ┌──────────────────────────────────────────┐
                            │            Index Engine                   │
                            │  ┌─────────────────────────────────┐    │
                            │  │  DGCA-weighted Laspeyres Index   │    │
                            │  │  I_t = Σ(P_it × Q_i0) /         │    │
                            │  │        Σ(P_i0 × Q_i0) × 100     │    │
                            │  └─────────────────────────────────┘    │
                            │  Weekly/Monthly rollups                  │
                            │  Lead-time elasticity matrix             │
                            │  DGCA backtest (MAPE, RMSE, r)          │
                            └───────────────┬─────────────────────────┘
                                            │
                                            ▼
                            ┌──────────────────────────────────────────┐
                            │          FastAPI + React Dashboard        │
                            │  ┌──────────┐     ┌──────────────────┐  │
                            │  │ FastAPI  │────▶│ React + Vite     │  │
                            │  │ /api/v1  │     │ + Tailwind       │  │
                            │  │ + Swagger│     │ + Recharts       │  │
                            │  └──────────┘     │ + Leaflet        │  │
                            │                    └──────────────────┘  │
                            └──────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (required)
- [Python 3.11+](https://www.python.org/downloads/) (for local dev)
- [Node.js 20+](https://nodejs.org/) (for frontend dev)
- [Git](https://git-scm.com/)

### One-Command Setup

```bash
git clone https://github.com/Yuvraj-Sarathe/JetIndex.git
cd JetIndex
cp .env.local .env
make setup
make up
```

### Verify Everything Works

| Service | URL | What to Check |
|---------|-----|---------------|
| **API Health** | http://localhost:8000/health | `{"status":"ok","mock_mode":true}` |
| **Swagger Docs** | http://localhost:8000/docs | All endpoints listed, try `/apix/daily` |
| **Dashboard** | http://localhost:5173 | MetricCard shows mock APIx value |
| **Flower (Celery)** | http://localhost:5555 | Worker connected, beat scheduled |

### Test Authentication

```bash
curl -H "Authorization: Bearer SJSSF01-zSIe6SqSVBaVHx1kh7_jBNKUPyVUWtnw6eA" \
     http://localhost:8000/api/v1/apix/daily
```

---

## 📊 API Reference

All endpoints require `Authorization: Bearer <token>` header (except `/health` and `/docs`).

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/health` | Health check | — |
| `GET` | `/api/v1/apix/daily` | Daily APIx index | `from_date`, `to_date` |
| `GET` | `/api/v1/apix/weekly` | Weekly rollup | `from_date`, `to_date` |
| `GET` | `/api/v1/apix/monthly` | Monthly rollup | `from_date`, `to_date` |
| `GET` | `/api/v1/routes` | Sector basket | — |
| `GET` | `/api/v1/routes/heatmap` | Per-route heatmap | `route_date` |
| `GET` | `/api/v1/elasticity` | Lead-time elasticity | `route_id`, `route_date` |
| `GET` | `/api/v1/quotes` | Clean quotes | `route_id`, `route_date`, `lead_time`, `carrier`, `limit` |
| `GET` | `/api/v1/backtest` | DGCA backtest | — |
| `POST` | `/api/v1/admin/trigger-sweep` | Trigger scrape | — |

### Example Response

```json
// GET /api/v1/apix/daily
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

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Scraping** | `curl_cffi` + Playwright | TLS fingerprint impersonation, stealth browser fallback |
| **Proxy** | Custom `ProxyManager` | Rotation, cooldown on 403/429, backoff |
| **Pipeline** | Polars + Pydantic v2 | High-speed data cleaning, type-safe schemas |
| **Database** | TimescaleDB (PostgreSQL 16) | Hypertables for time-series, fast aggregations |
| **Queue** | Celery + Redis | Distributed task queue, beat scheduler |
| **API** | FastAPI + Uvicorn | Async Python API, auto-generated Swagger |
| **Dashboard** | React 18 + Vite + Tailwind | Modern SPA, instant HMR |
| **Charts** | Recharts | Responsive, composable charting |
| **Maps** | React-Leaflet | Interactive route heatmap |
| **CI/CD** | GitHub Actions | Lint, test, build on every PR |
| **Container** | Docker Compose | 8-service local development stack |

---

## 📁 Project Structure

```
jetindex/
├── app/                    # FastAPI application (Yuvraj)
│   ├── core/               #   Config, security, Celery, logging
│   ├── api/v1/             #   API routers (apix, routes, quotes, etc.)
│   ├── schemas/            #   Response Pydantic models
│   ├── services/           #   Mock service for MOCK_MODE
│   └── tasks/              #   Celery tasks (scrape, pipeline, index)
├── scrapers/               # Stealth scraping engine (Sourabh + Abhay)
│   ├── base_scraper.py     #   ABC with fetch loop + retry + fallback
│   ├── indigo.py           #   IndiGo scraper
│   ├── makemytrip.py       #   MakeMyTrip scraper
│   ├── proxy_manager.py    #   Proxy rotation + cooldown
│   ├── fingerprints.py     #   TLS profiles + UA rotation
│   └── recon/              #   Endpoint reconnaissance notes
├── pipeline/               # Data cleaning (Vanshika)
│   ├── schemas.py          #   ★ FROZEN DATA CONTRACT
│   ├── parsers/            #   Source-specific JSON parsers
│   ├── unbundler.py        #   Vendor → canonical component mapping
│   ├── cleaner.py          #   Dedupe, IQR, sold-out flagging
│   └── loader.py           #   Upsert to fare_quotes
├── db/                     # Database layer (Sourabh + Abhay)
│   ├── models.py           #   SQLAlchemy 2 declarative models
│   ├── init.sql            #   TimescaleDB extension
│   ├── seed.py             #   Route + weight seeding
│   └── migrations/         #   Alembic
├── engine/                 # Index math (Sourabh + Abhay)
│   ├── index_calculator.py #   Laspeyres + Geometric Young
│   ├── weights.py          #   DGCA passenger weights
│   ├── aggregator.py       #   Weekly/monthly rollups
│   ├── elasticity.py       #   Lead-time elasticity
│   └── backtest.py         #   MAPE, RMSE vs DGCA
├── frontend/               # Dashboard (Mehak)
│   └── src/
│       ├── components/     #   MetricCard, ApixTrend, Heatmap, etc.
│       ├── hooks/          #   useApix, useHeatmap, useBacktest
│       ├── api/            #   Fetch wrapper with bearer token
│       └── pages/          #   Dashboard.jsx
├── config/                 # Static configuration (Yuvraj)
│   ├── routes.yaml         #   6-sector basket + lead times
│   ├── sources.yaml        #   Scraper configs
│   └── dgca_weights.csv    #   Passenger volume weights
├── data/                   # Datasets
│   ├── mock/               #   Realistic fake API responses
│   ├── reference/          #   DGCA benchmarks, airports
│   └── raw/                #   Scrape payloads (gitignored)
├── tests/                  # Pytest suite (everyone)
├── scripts/                # Helper scripts
├── docs/                   # Documentation (Sneh)
├── slides/                 # Pitch deck
├── demo/                   # Video script
├── .github/                # CI/CD + templates
├── docker-compose.yml      # 8-service stack
├── Dockerfile              # Python 3.11-slim + Playwright
├── Makefile                # Dev commands
└── instructions-for-team.md # Team onboarding guide
```

---

## 🔬 How It Works

### 1. Scraping (Stealth Mode)

- **TLS Impersonation**: `curl_cffi` with `impersonate="chrome124"` — fingerprints match real Chrome
- **Proxy Rotation**: Automatic rotation with cooldown on rate limits
- **Playwright Fallback**: Stealth browser when curl_cffi fails after 4 retries
- **Off-Peak Scheduling**: 02:00 IST via Celery Beat
- **Rate Limiting**: ≤1 request/3s per source per IP

### 2. Fare Unbundling

```python
# Raw vendor response
{"Base Fare": 3500, "UDF": 500, "GST": 300, "Convenience Fee": 200}

# Unbundled to canonical components
CleanQuote(
    base_fare=3500,
    udf=500,
    taxes=300,  # GST + PSF + ASF
    convenience_fee=200,
    other_fees=0,
    total_fare=4500,
)
```

### 3. Index Calculation

**DGCA-Weighted Laspeyres Index:**

```
I_t = Σ(P_it × Q_i0) / Σ(P_i0 × Q_i0) × 100

Where:
  i = route in basket (6 routes)
  P_it = median total_fare for route i on day t
  Q_i0 = DGCA passenger volume weight (base period)
  P_i0 = base period price (first 7 days = 100)
```

### 4. Backtest

Comparison against DGCA monthly average fares:
- **MAPE**: Mean Absolute Percentage Error
- **RMSE**: Root Mean Square Error
- **Pearson r**: Correlation coefficient

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific module
pytest tests/test_pipeline/ -v

# Run integration tests (requires DB)
pytest -m integration
```

**Test Coverage:**
- `test_app/` — Health endpoint, auth, mock mode
- `test_scrapers/` — Job creation, registry, result handling
- `test_pipeline/` — Validation, unbundling, sum consistency
- `test_engine/` — Laspeyres formula (base, increase, decrease)
- `test_db/` — Model imports, table names

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MOCK_MODE` | `true` | Serve mock data from `data/mock/` |
| `API_TOKEN` | `change-me-dev-token` | Bearer token for API auth |
| `DATABASE_URL` | `postgresql+psycopg://apix:apix@db:5432/apix` | PostgreSQL connection |
| `REDIS_URL` | `redis://redis:6379/0` | Redis broker |
| `PROXY_ENABLED` | `false` | Enable proxy rotation |
| `RAW_DATA_DIR` | `data/raw` | Raw payload storage |

### Sector Basket

| Route | Origin | Destination | Weight |
|-------|--------|-------------|--------|
| DEL-BOM | Delhi | Mumbai | 0.25 |
| DEL-BLR | Delhi | Bengaluru | 0.20 |
| BOM-BLR | Mumbai | Bengaluru | 0.16 |
| DEL-CCU | Delhi | Kolkata | 0.14 |
| BLR-HYD | Bengaluru | Hyderabad | 0.12 |
| MAA-DEL | Chennai | Delhi | 0.14 |

**Lead Times:** T+1, T+7, T+15, T+30, T+45

---

## 🔄 CI/CD Pipeline

Every push and PR triggers:

```
┌─────────────────────────────────────────────────────┐
│                   GitHub Actions                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐     ┌─────────────────────────┐   │
│  │ Backend CI  │     │     Frontend CI         │   │
│  ├─────────────┤     ├─────────────────────────┤   │
│  │ Lint (ruff) │     │ Lint (eslint)           │   │
│  │     │       │     │     │                   │   │
│  │     ▼       │     │     ▼                   │   │
│  │ Test (pytest│     │ Build (vite)            │   │
│  │  + coverage)│     │     │                   │   │
│  └─────────────┘     │     ▼                   │   │
│                      │ Upload artifacts        │   │
│                      └─────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 👥 Team

| Member | Role | GitHub | Package |
|--------|------|--------|---------|
| **Yuvraj** | Team Lead, Backend/DevOps | [@Yuvraj-Sarathe](https://github.com/Yuvraj-Sarathe) | `app/`, `config/`, Docker, CI |
| **Sourabh** | Scraping & DB | [@SourabhX16](https://github.com/SourabhX16) | `scrapers/`, `db/`, `engine/` |
| **Abhay** | Scraping & DB | [@abhay2006ichigo](https://github.com/abhay2006ichigo) | `scrapers/`, `db/`, `engine/` |
| **Vanshika** | Data Pipeline | [@VanshikaShrivastava-web](https://github.com/VanshikaShrivastava-web) | `pipeline/` |
| **Mehak** | Frontend | [@mehakshahofficial](https://github.com/mehakshahofficial) | `frontend/` |
| **Sneh** | Documentation | [@bysneh](https://github.com/bysneh) | `docs/`, `slides/`, `demo/` |

---

## 📋 Deliverables Checklist

- [x] Working prototype: scrape → clean → index → dashboard
- [x] Cleaned, de-duplicated fare DB with unbundled fields
- [x] Laspeyres index module (daily; weekly/monthly rollups)
- [x] Interactive dashboard with 7 components
- [x] README + Docker setup + config docs
- [x] Tests + CI/CD pipeline (GitHub Actions)
- [ ] 30+ day backtest vs DGCA (in progress)
- [ ] 2-page architecture doc (`docs/architecture.md`)
- [ ] 2-min demo video, 5-slide deck

---

## 📜 Ethics & Compliance

- **Rate Limiting**: ≤1 request/3 seconds per source per IP
- **robots.txt**: Respected for all scraped paths
- **Off-Peak**: Scraping at 02:00 IST
- **No Login**: Only anonymous search flows — never books or holds seats
- **Audit Trail**: Raw payloads retained for compliance
- **Data Privacy**: No personal data collected

See [docs/ethics_and_compliance.md](docs/ethics_and_compliance.md) for full details.

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for Smart India Hackathon 2026**

*Automating macroeconomic data collection for a better India*

</div>
