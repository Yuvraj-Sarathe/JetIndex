<!-- generated-by: gsd-doc-writer -->

# Architecture

## Problem

India's Consumer Price Index (CPI) relies on manual ticket-counter price collection for airfare data. This method covers only ~30% of bookings (offline counter sales), misses daily price swings of 200–400%, and produces stale data by the time it reaches MoSPI/RBI. With 90% of flight bookings now online, there is a massive blind spot in macroeconomic data.

## Solution

APIx (Airfare Price Index) replaces manual collection with an automated pipeline that scrapes online airfare data, unbundles fare components, and computes a DGCA-weighted Laspeyres price index across 20 domestic routes.

## Architecture Overview

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
│  25 sub-routers · Bearer token auth · CORS · Mock mode          │
└──────────────────────────┬──────────────────────────────────────┘
                           │  JSON API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               React Dashboard (Vercel)                          │
│  8 pages · 32 components · Recharts · Leaflet maps              │
└─────────────────────────────────────────────────────────────────┘
```

## Pipeline Detail

### 1. Scraping Layer

- **20 DGCA sector-bucket routes** × **5 lead times** (T+1, T+7, T+15, T+30, T+45) × **2 active sources** (IndiGo, MakeMyTrip) = **200 nightly jobs**
- `curl_cffi` with TLS fingerprint impersonation (Chrome 120/124, Safari 17, Edge 101)
- Playwright stealth browser fallback on failure after 4 retries
- Token-bucket rate limiting (0.33 req/s), proxy rotation with cooldown
- Raw payloads saved to `data/raw/` + `raw_quotes` DB table

### 2. Cleaning Pipeline

| Step | Module | Description |
|------|--------|-------------|
| Parse | `parsers/indigo_parser.py`, `makemytrip_parser.py` | Vendor JSON → `RawQuote` schema |
| Validate | `validators.py` | Positive fares, date ordering, carrier allowlist |
| Unbundle | `unbundler.py` | Regex label → canonical components (base_fare, UDF, taxes, convenience_fee, other_fees) |
| Dedupe | `cleaner.py` | Key-based dedup, cross-OTA dedup (prefers direct airline) |
| Filter | `cleaner.py` | MAD Z-score with IQR fallback, sold-out flagging |
| Load | `loader.py` | Bulk upsert to `fare_quotes` via raw SQL |

### 3. Index Computation

8 index formulas are implemented, with Laspeyres as the primary:

| Formula | Description |
|---------|-------------|
| **Laspeyres** | Σ(p₁·q₀) / Σ(p₀·q₀) — primary index |
| Fisher Ideal | √(Laspeyres × Paasche) |
| Paasche | Current-weighted (demand elasticity = -0.85) |
| Jevons | Unweighted geometric mean |
| Geometric Young | Weighted geometric mean |
| Törnqvist | Symmetric log-change index |
| Walsh | Quantity-weighted |
| Base-only | Without substitution bias |

**Key Constants:**
- Airfare share in transport CPI: 3.85%
- Transport CPI weight in headline: 8.59%
- Effective headline CPI weight: 0.003307

## Database Schema

10 tables in TimescaleDB (PostgreSQL 16):

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

## Stealth Strategy

The scraping layer uses multiple techniques to avoid detection:

1. **TLS Fingerprint Impersonation** — `curl_cffi` with `impersonate="chrome124"` matches real Chrome TLS fingerprints
2. **Proxy Rotation** — Automatic rotation with cooldown on 403/429 responses
3. **Playwright Fallback** — Full stealth browser when curl_cffi fails after 4 retries
4. **Off-Peak Scheduling** — All scraping runs at 02:00 IST via Celery Beat
5. **Rate Limiting** — ≤1 request/3 seconds per source per IP with jitter

## Backtest

Comparison against DGCA monthly average fares (Jan 2024 – Nov 2025):

- **MAPE**: Mean Absolute Percentage Error
- **RMSE**: Root Mean Square Error
- **Pearson r**: Correlation coefficient

DGCA data sourced from "City Pair Wise Passenger Traffic" FY 2024–25 and Kaggle aggregation of DGCA published reports.

## Infrastructure

Docker Compose runs 8 services:

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

**Deployment:**

| Component | Platform | URL |
|-----------|----------|-----|
| Frontend | Vercel | https://jetindex.vercel.app |
| Backend API | Render | https://jetindex-api.onrender.com |
| Database | Neon (PostgreSQL) | — |
