"""Pipeline CLI — run the cleaning pipeline for a given date."""

import argparse
import json
from datetime import date
from pathlib import Path

from loguru import logger

from app.core.config import settings


def run_pipeline(target_date: str, source: str | None = None, dry_run: bool = False) -> dict:
    """
    Run the full pipeline: parse → validate → unbundle → clean → load.

    Args:
        target_date: ISO date string (YYYY-MM-DD)
        source: Optional source filter (e.g., "indigo")
        dry_run: If True, don't write to DB

    Returns:
        Summary dict with counts at each stage.
    """
    from pipeline.cleaner import clean_batch
    from pipeline.parsers.indigo_parser import parse as parse_indigo
    from pipeline.parsers.makemytrip_parser import parse as parse_makemytrip
    from pipeline.unbundler import unbundle
    from pipeline.validators import validate_raw

    scrape_date = date.fromisoformat(target_date)
    raw_dir = Path(settings.RAW_DATA_DIR)

    # Find raw files for this date
    all_raw_quotes = []
    parsers = {
        "indigo": parse_indigo,
        "makemytrip": parse_makemytrip,
    }

    for source_dir in raw_dir.iterdir():
        if not source_dir.is_dir():
            continue
        if source and source_dir.name != source:
            continue
        if source_dir.name not in parsers:
            continue

        date_dir = source_dir / target_date
        if not date_dir.exists():
            continue

        parser = parsers[source_dir.name]
        for json_file in date_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    payload = json.load(f)
                job_meta = {
                    "source": source_dir.name,
                    "raw_ref": str(json_file),
                    "scrape_date": scrape_date,
                }
                raw_quotes = parser(payload, job_meta)
                all_raw_quotes.extend(raw_quotes)
            except Exception as e:
                logger.error(f"Failed to parse {json_file}: {e}")

    # Count stages
    stats = {
        "parsed": len(all_raw_quotes),
        "valid": 0,
        "unbundled": 0,
        "outliers": 0,
        "loaded": 0,
    }

    # Validate
    valid_quotes = []
    for rq in all_raw_quotes:
        validated = validate_raw(rq)
        if validated:
            valid_quotes.append(validated)
    stats["valid"] = len(valid_quotes)

    # Unbundle
    clean_quotes = [unbundle(rq) for rq in valid_quotes]
    stats["unbundled"] = len(clean_quotes)

    # Clean batch
    df = clean_batch(clean_quotes)
    if "is_outlier" in df.columns:
     n_outliers = len(df.filter(df["is_outlier"] == True))
    else:
     n_outliers = 0
    stats["outliers"] = n_outliers

    # Load
    if not dry_run:
        from pipeline.loader import load

        stats["loaded"] = load(df)
    else:
        stats["loaded"] = len(df)

    logger.info(f"Pipeline complete for {target_date}: {stats}")
    return stats


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run the APIx cleaning pipeline")
    parser.add_argument("--date", required=True, help="Scrape date (YYYY-MM-DD)")
    parser.add_argument("--source", help="Filter by source (e.g., indigo)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to DB")
    args = parser.parse_args()

    stats = run_pipeline(args.date, args.source, args.dry_run)
    print("\nPipeline Summary:")
    print(f"  Parsed:     {stats['parsed']}")
    print(f"  Valid:      {stats['valid']}")
    print(f"  Unbundled:  {stats['unbundled']}")
    print(f"  Outliers:   {stats['outliers']}")
    print(f"  Loaded:     {stats['loaded']}")


if __name__ == "__main__":
    main()
