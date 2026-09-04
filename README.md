# JetIndex — APIx: Real-time Airfare Price Index for India

**SIH26056 · MoSPI / NSO · Smart Automation / Macroeconomic Data Engineering**

APIx replaces manual ticket-counter price collection with an automated pipeline:
**scrape → clean & unbundle → TimescaleDB → weighted Laspeyres index → FastAPI + React dashboard**, benchmarked against DGCA monthly average fares.

> Root README is owned by **Sneh**. This is v0 written at scaffold time — Sneh, rewrite freely once the system works.

## Quickstart (everyone, Day 1)

```bash
git clone <repo-url> jetindex && cd jetindex
make setup            # copies .env, installs python dev deps, pre-commit, npm ci
make up               # db + redis + api + worker + beat + frontend
```
- API docs: http://localhost:8000/docs  (Bearer token = `API_TOKEN` in `.env`, default `change-me-dev-token`)
- Dashboard: http://localhost:5173
- Flower (celery): http://localhost:5555

`MOCK_MODE=true` by default → the API serves realistic fake data from `data/mock/` so frontend/docs work starts immediately. Flip to `false` once the DB has real quotes.

```bash
make test             # pytest
make lint             # ruff + eslint
make scrape ROUTE=DEL-BOM LEAD=7 SOURCE=indigo   # single scrape, no proxy
make pipeline DATE=2025-01-15                     # clean + load one day
make index DATE=2025-01-15                        # compute APIx for one day
make backtest
```

## Repo map & owners

| Path | Owner | What lives here |
|---|---|---|
| `app/` | Yuvraj | FastAPI app, Celery app/tasks, auth, settings |
| `scrapers/` | Sourabh + Abhay (+Yuvraj) | curl_cffi/Playwright scrapers, proxy & session mgmt |
| `pipeline/` | Vanshika | Data contract (`schemas.py`), parsers, unbundling, IQR cleaning, loader |
| `db/` | Sourabh + Abhay (+Yuvraj) | SQLAlchemy models, Timescale hypertables, Alembic, seeds |
| `engine/` | Sourabh + Abhay (+Yuvraj) | Laspeyres index, rollups, elasticity, DGCA backtest |
| `frontend/` | Mehak | React + Vite + Tailwind + Recharts + Leaflet dashboard |
| `docs/`, `slides/`, `demo/` | Sneh | Architecture doc, pitch deck, demo video script |
| `config/` | Yuvraj | Route basket, sources, DGCA weights |
| `data/` | shared | mock data, reference datasets, raw payloads (gitignored) |
| `tests/` | everyone | mirror of packages; write tests for your own module |

Each folder has its own `README.md` with your step-by-step brief. **Read yours first.**

## Pipeline & dependency chain

```
Celery Beat 02:00 IST ─▶ scrapers/ ─▶ data/raw + raw_quotes
                                 └▶ pipeline/ (parse → validate → unbundle → IQR) ─▶ fare_quotes (Timescale)
                                                                                   └▶ engine/ (Laspeyres) ─▶ apix_daily
                                                                                                         └▶ app/ FastAPI ─▶ frontend/ + MoSPI/RBI JSON
```
Yuvraj (infra) → Sourabh/Abhay (scrape) → Vanshika (clean) → Sourabh/Abhay (db+index) → Yuvraj (API) → Mehak (UI) → Sneh (docs/video).
**Don't block on upstream:** every stage has fixtures/mock data so you can start today.

## Team workflow

- Branch: `feat/<yourname>/<topic>` from `main`. PR → 1 approval → squash merge. `main` is protected.
- Never commit `.env`, raw scrape payloads, HAR files, or proxy credentials.
- Keep `pipeline/schemas.py` frozen after Day-1 review; changes need a PR tagged `data-contract` and a ping in the group.
- Daily 10-min sync: what's done, what's blocked, what you need from whom.
- Tests: add at least one test per new function in `tests/test_<yourpkg>/`.

## Sector basket & lead times
`DEL-BOM, DEL-BLR, BOM-BLR, DEL-CCU, BLR-HYD, MAA-DEL` × `T+1, T+7, T+15, T+30, T+45` — defined once in `config/routes.yaml`.

## Deliverables checklist (SIH)
- [ ] Working prototype: scrape → clean → index → dashboard
- [ ] Cleaned, de-duplicated fare DB with unbundled fields
- [ ] Laspeyres index module (daily; weekly/monthly optional)
- [ ] Interactive dashboard
- [ ] README + Docker setup + config docs
- [ ] Tests + reproducible run command (CI included)
- [ ] 30+ day backtest vs DGCA
- [ ] 2-page architecture doc (`docs/architecture.md`)
- [ ] 2-min demo video, 5-slide deck

## Ethics
Rate-limited, robots.txt-aware, off-peak scheduling, no login/booking flows, raw payloads retained only for audit. See `docs/ethics_and_compliance.md`.
