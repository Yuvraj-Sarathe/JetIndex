"""Admin endpoints — trigger sweeps, manage tasks, system health."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token
from db.models import ApixDaily, FareQuote, RawQuote, Route

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/status", dependencies=[Depends(require_token)])
def admin_status(db: Session = Depends(get_db)):
    """Return operational health: scrape times, quote counts, index, coverage, quality."""

    if settings.MOCK_MODE:
        return {
            "mode": "mock",
            "scraping": {"status": "simulated"},
            "database": {"status": "mock_data"},
        }

    # --- scraping stats ---
    last_scrape_at = db.scalar(select(func.max(RawQuote.fetched_at)))
    today_quotes = db.scalar(
        select(func.count(FareQuote.id)).where(func.cast(FareQuote.scraped_at, date) == date.today())
    )
    total_quotes = db.scalar(select(func.count(FareQuote.id)))

    # --- latest APIx index ---
    latest_apix = db.scalar(select(ApixDaily.apix).order_by(ApixDaily.date.desc()).limit(1))
    latest_index_date = db.scalar(select(ApixDaily.date).order_by(ApixDaily.date.desc()).limit(1))

    # --- route coverage today ---
    total_routes = db.scalar(select(func.count(Route.id)))
    routes_covered_today = db.scalar(
        select(func.count(func.distinct(FareQuote.route_id)))
        .where(func.cast(FareQuote.scraped_at, date) == date.today())
        .where(FareQuote.quality_flag == "ok")
    )
    pct = round(routes_covered_today / total_routes * 100, 1) if total_routes else 0.0

    # --- quality distribution (all-time) ---
    quality_dist = dict(db.execute(select(FareQuote.quality_flag, func.count()).group_by(FareQuote.quality_flag)).all())

    return {
        "mode": "live",
        "scraping": {
            "last_scrape_at": str(last_scrape_at) if last_scrape_at else None,
            "quotes_today": today_quotes or 0,
            "total_quotes": total_quotes or 0,
        },
        "index": {
            "latest_apix": latest_apix,
            "latest_date": str(latest_index_date) if latest_index_date else None,
        },
        "coverage": {
            "routes_today": routes_covered_today or 0,
            "routes_total": total_routes or 0,
            "pct": pct,
        },
        "quality": quality_dist,
    }


@router.post("/trigger-sweep", dependencies=[Depends(require_token)])
def trigger_sweep():
    """Trigger the daily scrape sweep manually (demo button in frontend)."""
    if settings.MOCK_MODE:
        return {"status": "mock_mode", "detail": "Sweep simulated (mock mode)"}

    from app.tasks.scrape_tasks import run_daily_sweep

    task = run_daily_sweep.delay()
    return {"status": "queued", "task_id": task.id}
