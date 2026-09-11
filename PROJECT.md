# JetIndex (APIx) — Airfare Price Index

> Real-time airfare price index for India's CPI, built for Smart India Hackathon 2026 (SIH26056 — MoSPI/NSO)

---

## Problem Statement

India's Consumer Price Index (CPI) relies on manual ticket-counter price collection covering only ~30% of air bookings. This misses daily price swings of 200–400%, producing stale and inaccurate inflation data. MoSPI/NSO needs an automated, real-time system that captures the full market.

## Solution

JetIndex scrapes online airfare data (covering ~90% of bookings), unbundles fare components, and computes a DGCA-weighted Laspeyres price index — replacing manual collection with an automated **Scrape → Clean → Store → Compute → Serve** pipeline.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | Python 3.11, FastAPI, SQLAlchemy 2, Pydantic v2 |
| **Database** | PostgreSQL 16 + TimescaleDB (Neon in prod) |
| **Task Queue** | Celery + Redis (Beat scheduler at 02:00 IST) |
| **Scraping** | curl_cffi (TLS impersonation), Playwright (stealth browser), proxy rotation |
| **Data Pipeline** | Polars (DataFrames), Pydantic schemas |
| **ML / Analytics** | NumPy, SciPy, scikit-learn (Ridge + Gradient Boosting ensemble) |
| **Frontend** | React 18, Vite, Tailwind CSS, Recharts, React-Leaflet |
| **Infrastructure** | Docker Compose (8 services), GitHub Actions CI/CD |
| **Object Storage** | MinIO (audit payloads) |
| **Auth** | PBKDF2-HMAC-SHA256, HMAC-signed JWT-like tokens, RBAC (8 roles) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Celery Beat (02:00 IST)                     │
│                        run_daily_sweep                          │
└──────────────┬──────────────────────────────────┬───────────────┘
               │  fan-out (200 scrape jobs)       │
               ▼                                  ▼
┌──────────────────────┐            ┌──────────────────────────┐
│   Scrape Route       │            │   Scrape Route           │
│   (curl_cffi /       │  ... x200  │   (Playwright fallback)  │
│    Playwright)       │            │                          │
└──────────┬───────────┘            └──────────┬───────────────┘
           │  raw JSON to disk + DB            │
           ▼                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Pipeline (clean_and_load)                     │
│  Parse → Validate → Unbundle → Dedupe → MAD/IQR Filter → Load  │
└──────────────────────────┬──────────────────────────────────────┘
                           │  clean fare_quotes
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               Index Computation (compute_daily_index)            │
│  Median fares → Laspeyres → APIx daily → Route/Window indices   │
└──────────────────────────┬──────────────────────────────────────┘
                           │  apix_daily, route_indices
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Server (port 8000)                    │
│  26 sub-routers · Bearer token auth · CORS · Mock mode          │
└──────────────────────────┬──────────────────────────────────────┘
                           │  JSON API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               React Dashboard (Vercel)                          │
│  8 pages · 32 components · Recharts · Leaflet maps              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Pipeline

### 1. Scraping Layer
- **20 DGCA sector-bucket routes** × **5 lead times** (T+1, T+7, T+15, T+30, T+45) × **2 active sources** (IndiGo, MakeMyTrip) = **200 nightly jobs**
- `curl_cffi` with TLS fingerprint impersonation (Chrome 120/124, Safari 17, Edge 101)
- Playwright stealth browser fallback on failure
- Token-bucket rate limiting (0.33 req/s), proxy rotation with cooldown
- Raw payloads saved to `data/raw/` + `raw_quotes` DB table

### 2. Cleaning Pipeline
| Step | Module | Description |
|------|--------|-------------|
| Parse | `parsers/indigo_parser.py`, `makemytrip_parser.py` | Vendor JSON → `RawQuote` schema |
| Validate | `validators.py` | Positive fares, date ordering, carrier allowlist `{6E, AI, QP, SG, UK, G8, I5}` |
| Unbundle | `unbundler.py` | Regex label → canonical components (base_fare, UDF, taxes, convenience_fee, other_fees). Reverse decomposition using statutory constants (ASF=₹200, PSF=₹91, UDF=₹420, GST=5%) |
| Dedupe | `cleaner.py` | Key-based dedup, cross-OTA dedup (prefers direct airline) |
| Filter | `cleaner.py` | MAD Z-score with IQR fallback, sold-out flagging |
| Load | `loader.py` | Bulk upsert to `fare_quotes` via raw SQL |

### 3. Index Computation
**8 Index Formulas:**
| Formula | Description |
|---------|-------------|
| **Laspeyres** | Σ(p₁·q₀) / Σ(p₀·q₀) — primary index |
| Geometric Young | Weighted geometric mean |
| Jevons | Unweighted geometric mean |
| Paasche | Current-weighted (demand elasticity = -0.85) |
| Fisher Ideal | √(Laspeyres × Paasche) |
| Tornqvist | Symmetric log-change index |
| Walsh | Quantity-weighted |
| Base-only | Without substitution bias |

**Key Constants:**
- Airfare share in transport CPI: 3.85%
- Transport CPI weight in headline: 8.59%
- Effective headline CPI weight: 0.003307 (0.0385 × 0.0859)

---

## Database Schema (10 Tables)

| Table | Purpose |
|-------|---------|
| `routes` | 20 DGCA sector-bucket routes with coordinates |
| `raw_quotes` | Audit/landing table for raw scraper payloads (JSONB) |
| `fare_quotes` | Clean unbundled quotes (TimescaleDB hypertable on `scraped_at`) |
| `apix_daily` | Daily APIx index values |
| `dgca_weights` | DGCA passenger volume weights per route |
| `dgca_benchmark` | DGCA monthly average fares for backtesting |
| `national_indices` | Daily national indices (Laspeyres, Fisher, Paasche) |
| `route_indices` | Route-level indices per advance window |
| `cleaned_quotes` | Cleaned/validated quotes with outlier flags |
| `alert_rules` / `alerts` | Configurable alert rules and triggered alerts |

---

## Frontend Dashboard (8 Pages)

| Page | Features |
|------|----------|
| **Publishing Overview** | APIx trend chart, heatmap, route comparator, export |
| **Spike Anomalies** | Z-score anomaly feed, EWMA detection |
| **T+14 Forecast** | Ridge+GBD ensemble, 14-day nowcast with 95% CI |
| **Scenario Simulator** | What-if: airfare shock, ATF fuel, demand, capacity |
| **Model Validation** | MAPE, RMSE, Pearson r, residual distributions |
| **Trust & Quality** | 7-dimension composite score (freshness, completeness, coverage, health, dedup, outlier, consensus) |
| **Alerts** | Threshold-based alert rules with severity |
| **Methodology & API** | Full docs, formula reference, API explorer |

---

## API Endpoints (26 Sub-routers)

| Prefix | Endpoints |
|--------|-----------|
| `/api/v1/apix` | Daily, weekly, monthly index; scraped vs DGCA |
| `/api/v1/routes` | Route list, heatmap data |
| `/api/v1/elasticity` | Lead-time elasticity matrix |
| `/api/v1/quotes` | Clean fare quotes |
| `/api/v1/backtest` | APIx vs DGCA benchmark comparison |
| `/api/v1/forecast` | National + route-level forecasts |
| `/api/v1/anomalies` | Spike detection results |
| `/api/v1/analytics` | Pressure score, CPI decomposition, CPI impact |
| `/api/v1/scenario` | What-if simulation |
| `/api/v1/alerts` | Alert rules + live alerts |
| `/api/v1/data-quality` | Trust score breakdown |
| `/api/v1/telemetry` | System health metrics |
| `/api/v1/provenance` | SHA-256 audit trail |
| `/api/v1/validation` | Model performance metrics |
| `/api/v1/reports` | Daily executive reports |
| `/api/v1/route-intelligence` | Route-specific insights |
| `/api/v1/source-analytics` | Per-source performance |
| `/api/v1/source-consensus` | Cross-source agreement |
| `/api/v1/ai-analyst` | Natural language policy queries |
| `/api/v1/admin` | System status, trigger sweep |
| `/api/v1/auth` | Login, role switch |
| `/api/v1/ml` | ML model management |

---

## Sector Basket (20 Routes)

Weighted by DGCA passenger volumes:

| Route | Weight | Metro |
|-------|--------|-------|
| DEL-BOM | 18.2% | Yes |
| DEL-BLR | 12.5% | Yes |
| BOM-BLR | 8.7% | Yes |
| DEL-CCU | 6.3% | Yes |
| MAA-DEL | 5.8% | Yes |
| BLR-HYD | 4.2% | Yes |
| DEL-GOI | 3.5% | No |
| DEL-HYD | 3.4% | Yes |
| BOM-CCU | 2.9% | Yes |
| DEL-JAI | 2.6% | No |
| ... (15 more) | ... | ... |

**Advance Purchase Windows:**
| Window | Weight | Price Multiplier |
|--------|--------|-----------------|
| T+1 | 22% | 2.45x |
| T+7 | 34% | 1.60x |
| T+15 | 24% | 1.18x |
| T+30 | 14% | 1.00x |
| T+45 | 6% | 0.92x |

---

## Infrastructure (Docker Compose — 8 Services)

| Service | Image | Port | Role |
|---------|-------|------|------|
| `db` | TimescaleDB (PG16) | 5432 | Time-series database |
| `redis` | Redis 7 Alpine | 6379 | Celery broker |
| `api` | Custom (Python 3.11) | 8000 | FastAPI server |
| `worker` | Custom + Playwright | — | Celery worker |
| `beat` | Custom | — | Celery Beat scheduler |
| `flower` | Custom | 5555 | Celery monitoring |
| `frontend` | Node 20 Alpine | 5173 | Vite dev server |
| `minio` | MinIO | 9000/9001 | Object storage |

---

## Deployment

| Component | Platform | URL |
|-----------|----------|-----|
| **Frontend** | Vercel | https://jetindex.vercel.app |
| **Backend API** | Render | https://jetindex-api.onrender.com |
| **Database** | Neon (PostgreSQL) | — |
| **CI/CD** | GitHub Actions | Auto-deploy on push to `main` |

---

## Auth & RBAC (8 Roles)

| Role | Description |
|------|-------------|
| MOSPI_ADMIN | Full system access |
| MOSPI_ANALYST | Read + analysis |
| RBI_MPC | Monetary Policy Committee read access |
| RBI_ECONOMIST | Economist read access |
| DGCA_REGULATOR | Regulator read access |
| DGCA_INSPECTOR | Inspector limited access |
| SYSTEM_ADMIN | Infrastructure management |
| PUBLIC_AUDITOR | Read-only public data |

Demo password: `JetIndex2026!` (all roles)

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Routes tracked | 20 |
| Lead times | 5 (T+1 to T+45) |
| Active scrapers | 2 (IndiGo, MakeMyTrip) |
| Index formulas | 8 |
| Nightly scrape jobs | 200 |
| API endpoints | 50+ |
| Frontend pages | 8 |
| Frontend components | 32 |
| DB tables | 10 |
| Trust score dimensions | 7 |
| Auth roles | 8 |

---

## Team

| Name | Role |
|------|------|
| Yuvraj Sarathe | Backend / ML / Infrastructure |
| Sourabh | Backend / Pipeline |
| Abhay | Scraping / Backend |
| Vanshika | Frontend / Design |
| Mehak | Frontend / Analytics |
| Sneh | Data / Documentation |
