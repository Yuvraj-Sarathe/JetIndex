"""Celery application instance and beat schedule."""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery = Celery(
    "apix",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    beat_schedule={
        "daily-sweep": {
            "task": "app.tasks.scrape_tasks.run_daily_sweep",
            "schedule": crontab(hour=settings.SCRAPE_HOUR_IST, minute=0),
        },
    },
)

# Auto-discover tasks in app.tasks
celery.autodiscover_tasks(["app.tasks"])
