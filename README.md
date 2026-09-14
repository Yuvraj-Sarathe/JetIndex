<!-- generated-by: gsd-doc-writer -->

<div align="center">

# JetIndex — APIx

### Real-time Airfare Price Index for India's CPI

**SIH26056 · MoSPI / NSO · Smart India Hackathon 2026**

[![Backend CI](https://github.com/Yuvraj-Sarathe/JetIndex/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Yuvraj-Sarathe/JetIndex/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/Yuvraj-Sarathe/JetIndex/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/Yuvraj-Sarathe/JetIndex/actions/workflows/frontend-ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

India's CPI airfare data is collected manually at airport counters — covering only ~30% of bookings and missing daily price swings of 200–400%. **APIx** replaces this with an automated pipeline that scrapes online fares, unbundles fare components, and computes a DGCA-weighted Laspeyres price index across 20 domestic routes.

```
Scrape → Clean → Store → Compute → Serve
```

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (required)
- [Python 3.11+](https://www.python.org/downloads/) (for local dev)
- [Node.js 20+](https://nodejs.org/) (for frontend dev)

### One-Command Setup

```bash
git clone https://github.com/Yuvraj-Sarathe/JetIndex.git
cd JetIndex
cp .env.example .env
make setup
make up
```

### Verify It Works

| Service | URL | Check |
|---------|-----|-------|
| **API Health** | http://localhost:8000/health | `{"status":"ok","mock_mode":true,"version":"0.1.0"}` |
| **Swagger Docs** | http://localhost:8000/docs | All endpoints listed |
| **Dashboard** | http://localhost:5173 | MetricCard shows mock APIx value |
| **Flower (Celery)** | http://localhost:5555 | Worker connected |

### Test Authentication

```bash
curl -H "Authorization: Bearer SJSSF01-zSIe6SqSVBaVHx1kh7_jBNKUPyVUWtnw6eA" \
     http://localhost:8000/api/v1/apix/daily
```

---

## Key Features

- **Fare Unbundling** — Decomposes each quote into base fare, UDF, taxes, convenience fee, and other fees for component-level inflation tracking
- **8 Index Formulas** — Laspeyres (primary), Fisher, Paasche, Jevons, Geometric Young, Törnqvist, Walsh, and base-only
- **DGCA-Weighted** — Route weights from official FY 2024–25 passenger traffic data
- **20 Routes × 5 Lead Times** — 200 nightly scrape jobs across IndiGo and MakeMyTrip
- **Stealth Scraping** — TLS fingerprint impersonation via `curl_cffi` with Playwright fallback
- **30+ Day Backtest** — Validated against DGCA monthly average fares (MAPE, RMSE, Pearson r)
- **50+ API Endpoints** — Index, forecast, anomalies, scenario simulation, data quality, and more
- **Interactive Dashboard** — React SPA with trend charts, route heatmap, elasticity curves, and export

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Scraping** | `curl_cffi` (TLS impersonation), Playwright (stealth fallback), proxy rotation |
| **Pipeline** | Polars + Pydantic v2 (schemas, validation, unbundling) |
| **Database** | TimescaleDB (PostgreSQL 16) — hypertables for time-series |
| **Queue** | Celery + Redis (Beat scheduler at 02:00 IST) |
| **API** | FastAPI + Uvicorn (async, auto-generated Swagger) |
| **Dashboard** | React 18 + Vite + Tailwind CSS + Recharts + React-Leaflet |
| **Auth** | PBKDF2-HMAC-SHA256, HMAC-signed tokens, 8 RBAC roles |
| **ML** | NumPy, SciPy, scikit-learn (Ridge + Gradient Boosting ensemble) |
| **Infrastructure** | Docker Compose (8 services), GitHub Actions CI/CD |

---

## Project Structure

```
jetindex/
├── app/                    # FastAPI application
│   ├── core/               #   Config, security, Celery, logging
│   ├── api/v1/             #   25 API routers
│   ├── schemas/            #   Response Pydantic models
│   ├── services/           #   Mock service for MOCK_MODE
│   └── tasks/              #   Celery tasks (scrape, pipeline, index)
├── scrapers/               # Stealth scraping engine
│   ├── base_scraper.py     #   ABC with fetch loop + retry + fallback
│   ├── indigo.py           #   IndiGo scraper
│   ├── makemytrip.py       #   MakeMyTrip scraper
│   └── proxy_manager.py    #   Proxy rotation + cooldown
├── pipeline/               # Data cleaning & unbundling
│   ├── schemas.py          #   ★ FROZEN DATA CONTRACT
│   ├── parsers/            #   Source-specific JSON parsers
│   ├── unbundler.py        #   Vendor → canonical component mapping
│   ├── cleaner.py          #   Dedupe, IQR, sold-out flagging
│   └── loader.py           #   Upsert to fare_quotes
├── db/                     # Database layer
│   ├── models.py           #   SQLAlchemy 2 declarative models
│   ├── queries.py          #   Centralised query functions
│   └── migrations/         #   Alembic
├── engine/                 # Index math & analytics
│   ├── index_calculator.py #   Laspeyres + 7 other formulas
│   ├── weights.py          #   DGCA passenger weights
│   ├── aggregator.py       #   Weekly/monthly rollups
│   ├── elasticity.py       #   Lead-time elasticity
│   └── backtest.py         #   MAPE, RMSE vs DGCA
├── frontend/               # Dashboard SPA
│   └── src/                #   React components, hooks, API client
├── config/                 # Static configuration
│   ├── routes.yaml         #   20-route basket + lead times
│   ├── sources.yaml        #   Scraper configs
│   └── dgca_weights.csv    #   Passenger volume weights
├── data/                   # Datasets
│   ├── mock/               #   Realistic fake API responses
│   └── reference/          #   DGCA benchmarks, airports
├── tests/                  # Pytest suite
├── docs/                   # Documentation
├── docker-compose.yml      # 8-service stack
├── Makefile                # Dev commands
└── requirements-dev.txt    # Python dev dependencies
```

---

## Configuration

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

20 DGCA routes weighted by FY 2024–25 passenger traffic:

| Route | Weight | Route | Weight |
|-------|--------|-------|--------|
| DEL-BOM | 10.92% | BOM-BLR | 5.84% |
| BOM-DEL | 10.73% | BLR-BOM | 5.75% |
| DEL-BLR | 8.05% | DEL-CCU | 4.98% |
| BLR-DEL | 7.85% | CCU-DEL | 4.89% |

**Lead Times:** T+1, T+7, T+15, T+30, T+45

---

## Testing

```bash
make test              # Run all tests
make test-cov          # Run with coverage
make test-integration  # Integration tests (requires DB)
```

---

## CI/CD

Every push and PR triggers GitHub Actions:

- **Backend CI** — Ruff lint + Pytest with coverage
- **Frontend CI** — ESLint + Vite build + artifact upload

---

## Ethics & Compliance

- Rate limiting: ≤1 request/3 seconds per source per IP
- robots.txt respected for all scraped paths
- Off-peak scheduling at 02:00 IST
- No login/booking — only anonymous search flows
- Raw payloads retained for audit trail
- No personal data collected

See [docs/ethics_and_compliance.md](docs/ethics_and_compliance.md) for full details.

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/architecture.md](docs/architecture.md) | System architecture and pipeline design |
| [docs/api_reference.md](docs/api_reference.md) | All API endpoints with examples |
| [docs/data_contract.md](docs/data_contract.md) | CleanQuote schema and fee mapping |
| [docs/index_methodology.md](docs/index_methodology.md) | Laspeyres formula, weights, and limitations |
| [docs/ethics_and_compliance.md](docs/ethics_and_compliance.md) | Scraping policy and legal posture |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

---

## Team

| Member | Role | GitHub |
|--------|------|--------|
| **Yuvraj** | Team Lead, Backend/DevOps | [@Yuvraj-Sarathe](https://github.com/Yuvraj-Sarathe) |
| **Sourabh** | Scraping & DB | [@SourabhX16](https://github.com/SourabhX16) |
| **Abhay** | Scraping & DB | [@abhay2006ichigo](https://github.com/abhay2006ichigo) |
| **Vanshika** | Data Pipeline | [@VanshikaShrivastava-web](https://github.com/VanshikaShrivastava-web) |
| **Mehak** | Frontend | [@mehakshahofficial](https://github.com/mehakshahofficial) |
| **Sneh** | Documentation | [@bysneh](https://github.com/bysneh) |

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built for Smart India Hackathon 2026**

*Automating macroeconomic data collection for a better India*

</div>
