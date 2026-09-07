"""Raw payload storage — writes files + raw_quotes DB row."""

import json
from pathlib import Path

from loguru import logger

from app.core.config import settings
from scrapers.base_scraper import ScrapeResult


def save_raw(result: ScrapeResult) -> Path:
    """
    Save raw scrape payload to disk.

    Path format: data/raw/{source}/{scrape_date}/{ORIGIN}-{DEST}_T{lead}.json

    Also attempts to insert a row into raw_quotes table.
    If DB is unreachable, logs a warning but does not crash the scrape.
    """
    raw_dir = Path(settings.RAW_DATA_DIR)
    date_dir = raw_dir / result.job.source / result.job.scrape_date.isoformat()
    date_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{result.job.origin}-{result.job.destination}_T{result.job.lead_time}.json"
    filepath = date_dir / filename

    # Write raw payload to disk
    with open(filepath, "w") as f:
        json.dump(result.payload, f, indent=2, default=str)

    result.raw_path = str(filepath)
    logger.info(f"Saved raw payload to {filepath}")

    # Try to insert into raw_quotes table (non-critical)
    try:
        from db.queries import get_route_by_code, insert_raw_quote
        from db.session import SessionLocal

        route_code = f"{result.job.origin}-{result.job.destination}"
        with SessionLocal() as db:
            route = get_route_by_code(db, route_code)
            if route:
                raw_record = {
                    "source": result.job.source,
                    "route_id": route.id,
                    "scrape_date": result.job.scrape_date,
                    "depart_date": result.job.depart_date,
                    "lead_time": result.job.lead_time,
                    "fetched_at": result.fetched_at,
                    "status_code": result.status_code,
                    "method": result.method,
                    "proxy_used": result.proxy_used,
                    "raw_path": str(filepath),
                    "payload": result.payload,
                }
                insert_raw_quote(db, raw_record)
            else:
                logger.warning(f"Cannot insert raw_quote: route {route_code} not found in DB")
    except Exception as e:
        logger.warning(f"Failed to insert raw_quotes row (DB may be down): {e}")

    return filepath
