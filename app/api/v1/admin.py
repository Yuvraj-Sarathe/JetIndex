"""Admin endpoints — trigger sweeps, manage tasks."""

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_token

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/trigger-sweep", dependencies=[Depends(require_token)])
def trigger_sweep():
    """Trigger the daily scrape sweep manually (demo button in frontend)."""
    if settings.MOCK_MODE:
        return {"status": "mock_mode", "detail": "Sweep simulated (mock mode)"}

    from app.tasks.scrape_tasks import run_daily_sweep

    task = run_daily_sweep.delay()
    return {"status": "queued", "task_id": task.id}
