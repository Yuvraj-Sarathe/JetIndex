# `app/` — FastAPI API + Celery orchestration

**Owner: Yuvraj** (Team Lead, Backend/DevOps)

## What this package does
- Exposes the **consumption API** for MoSPI/RBI and the dashboard (`/api/v1/...`) with Bearer-token auth.
- Hosts the **Celery app** (broker Redis) and the **Beat schedule** that fires the nightly sweep at **02:00 IST**.
- Owns global **settings** (`core/config.py`) — every other package imports `settings` from here.
- Provides **mock mode** so the frontend/docs can work before real data exists.

## Files
| File | Purpose |
|---|---|
| `main.py` | `create_app()`, CORS, router mount, `/health` |
| `core/config.py` | `Settings` (pydantic-settings, reads `.env`) |
| `core/security.py` | `require_token` dependency |
| `core/celery_app.py` | Celery instance, queues (`default`, `scrape`), beat schedule |
| `core/logging.py` | loguru setup |
| `api/v1/router.py` | includes `apix`, `routes`, `elasticity`, `quotes`, `backtest` routers |
| `api/v1/*.py` | one file per resource; mock branch vs DB branch |
| `schemas/responses.py` | response models (keep in sync with `docs/api_reference.md`) |
| `services/mock_service.py` | reads `data/mock/*.json` |
| `tasks/scrape_tasks.py` | `run_daily_sweep`, `scrape_route(source, route_code, lead)` |
| `tasks/pipeline_tasks.py` | `clean_and_load(date)` |
| `tasks/index_tasks.py` | `compute_daily_index(date)` |

## Endpoints to deliver
| Method & path | Notes |
|---|---|
| `GET /health` | no auth |
| `GET /api/v1/apix/daily?from&to` | `[{date, apix, pct_change_dod, n_quotes}]` |
| `GET /api/v1/apix/weekly`, `/monthly` | rollups from `engine/aggregator.py` |
| `GET /api/v1/routes` | basket + weights |
| `GET /api/v1/routes/heatmap?date` | per-route avg fare, volatility, lat/lon |
| `GET /api/v1/elasticity?route_id&date` | fare by lead time |
| `GET /api/v1/quotes?...` | clean quote inspector (paginated) |
| `GET /api/v1/backtest` | APIx vs DGCA + MAPE/RMSE |
| `POST /api/v1/admin/trigger-sweep` | enqueue `run_daily_sweep` (demo button) |

## Step-by-step
1. **Day 1:** `make up` works, `/health` green, `/docs` shows all endpoints returning mock data. Share the API token with Mehak.
2. Wire `core/celery_app.py`; verify `worker` and `beat` containers stay up and Flower shows the scheduled task.
3. Implement `tasks/*` as thin wrappers: `scrapers.registry.build_jobs_for_date` → group of `scrape_route` → chord callback `clean_and_load` → `compute_daily_index`.
4. Replace mock branches with real queries once `db/models.py` + `engine/` land (Sourabh/Abhay). Keep `MOCK_MODE` working forever — it's the demo safety net.
5. Add rate limiting (simple in-memory or `slowapi`), request logging, and `X-Request-ID`.
6. Tag responses with `generated_at` and `method: "laspeyres"` for auditability.

## Conventions
- Never query the DB directly in routers — go through `engine/` or `db/` helper functions.
- All dates ISO-8601, all money INR floats rounded to 2 dp.
- Errors: `{"detail": "..."}`, standard FastAPI style.

## Run locally without Docker
```bash
uvicorn app.main:app --reload
celery -A app.core.celery_app worker -l info
celery -A app.core.celery_app beat -l info
```
