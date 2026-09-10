"""Local daily sweep runner — no Docker/Celery required.

Runs the full pipeline: scrape → clean → index.
Can be scheduled via Windows Task Scheduler or cron.

Usage:
    python -m scrapers.local_sweep                      # Scrape all routes
    python -m scrapers.local_sweep --route DEL-BOM      # Scrape one route
    python -m scrapers.local_sweep --source indigo      # One source only
    python -m scrapers.local_sweep --dry-run            # Show what would be scraped
    python -m scrapers.local_sweep --schedule           # Run in loop (every 6 hours)
"""

import argparse
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def run_sweep(
    source_filter: str | None = None,
    route_filter: str | None = None,
    lead_times: list[int] | None = None,
    dry_run: bool = False,
) -> dict:
    """Run the daily scrape sweep synchronously."""
    from scrapers.base_scraper import ScrapeJob
    from scrapers.registry import build_jobs_for_date, get_scraper

    today = date.today()
    jobs = build_jobs_for_date(today)

    # Apply filters
    if source_filter:
        jobs = [j for j in jobs if j.source == source_filter]
    if route_filter:
        origin, dest = route_filter.split("-")
        jobs = [j for j in jobs if j.origin == origin and j.destination == dest]
    if lead_times:
        jobs = [j for j in jobs if j.lead_time in lead_times]

    print(f"\nDaily sweep for {today}: {len(jobs)} jobs")
    print(f"Sources: {sorted(set(j.source for j in jobs))}")
    print(f"Routes: {sorted(set(f'{j.origin}-{j.destination}' for j in jobs))}")
    print(f"Lead times: {sorted(set(j.lead_time for j in jobs))}")

    if dry_run:
        print("\n[DRY RUN] Would scrape:")
        for j in jobs:
            print(f"  {j.source} | {j.origin}-{j.destination} | T+{j.lead_time} | departs {j.depart_date}")
        return {"status": "dry_run", "n_jobs": len(jobs)}

    # Group by source to respect rate limits
    results = {"scraped": 0, "failed": 0, "errors": []}

    # Group jobs by source
    jobs_by_source: dict[str, list[ScrapeJob]] = {}
    for j in jobs:
        jobs_by_source.setdefault(j.source, []).append(j)

    for source, source_jobs in jobs_by_source.items():
        print(f"\nScraping {source}: {len(source_jobs)} jobs")
        try:
            scraper = get_scraper(source)
            scrape_results = scraper.run_jobs(source_jobs)

            for r in scrape_results:
                route = f"{r.job.origin}-{r.job.destination}"
                if r.ok:
                    results["scraped"] += 1
                    print(f"  OK  {route} T+{r.job.lead_time} -> {r.raw_path}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"{source}/{route}: {r.error}")
                    print(f"  FAIL {route} T+{r.job.lead_time}: {r.error}")

        except Exception as e:
            results["failed"] += len(source_jobs)
            results["errors"].append(f"{source}: {e}")
            print(f"  ERROR {source}: {e}")

    print(f"\nSweep complete: {results['scraped']} scraped, {results['failed']} failed")
    return results


def run_pipeline(scrape_date_str: str) -> dict:
    """Run the cleaning pipeline for a given date."""
    try:
        from pipeline.run import run_pipeline as _run_pipeline

        stats = _run_pipeline(scrape_date_str)
        print(f"Pipeline complete: {stats}")
        return stats
    except ImportError:
        print("Warning: pipeline module not available, skipping clean step")
        return {"status": "skipped"}
    except Exception as e:
        print(f"Pipeline error: {e}")
        return {"status": "error", "error": str(e)}


def run_index(compute_date_str: str) -> dict:
    """Compute the daily index."""
    try:
        from engine.index_calculator import compute_daily
        from db.session import SessionLocal

        compute_date = date.fromisoformat(compute_date_str)
        session = SessionLocal()
        try:
            result = compute_daily(compute_date, session)
            print(f"Index computed: APIx={result.get('apix', 'N/A')}")
            return result
        finally:
            session.close()
    except ImportError:
        print("Warning: index calculator not available, skipping index step")
        return {"status": "skipped"}
    except Exception as e:
        print(f"Index error: {e}")
        return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Local daily sweep runner")
    parser.add_argument("--source", help="Source filter (indigo, makemytrip)")
    parser.add_argument("--route", help="Route filter (e.g. DEL-BOM)")
    parser.add_argument("--leads", help="Lead times (e.g. 1,7,15)")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without scraping")
    parser.add_argument("--scrape-only", action="store_true", help="Skip pipeline and index")
    parser.add_argument("--schedule", action="store_true", help="Run in loop every 6 hours")
    parser.add_argument("--interval", type=int, default=6, help="Hours between runs (with --schedule)")
    args = parser.parse_args()

    lead_times = [int(x) for x in args.leads.split(",")] if args.leads else None

    if args.schedule:
        print(f"Starting scheduled sweep (every {args.interval} hours)")
        print("Press Ctrl+C to stop")
        while True:
            try:
                today = date.today().isoformat()
                print(f"\n--- Sweep at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
                results = run_sweep(
                    source_filter=args.source,
                    route_filter=args.route,
                    lead_times=lead_times,
                )
                if not args.scrape_only and results.get("scraped", 0) > 0:
                    print("\nRunning pipeline...")
                    run_pipeline(today)
                    print("\nComputing index...")
                    run_index(today)
                print(f"\nNext sweep in {args.interval} hours")
                time.sleep(args.interval * 3600)
            except KeyboardInterrupt:
                print("\nStopped.")
                break
    else:
        results = run_sweep(
            source_filter=args.source,
            route_filter=args.route,
            lead_times=lead_times,
            dry_run=args.dry_run,
        )
        if not args.dry_run and not args.scrape_only and results.get("scraped", 0) > 0:
            today = date.today().isoformat()
            print("\nRunning pipeline...")
            run_pipeline(today)
            print("\nComputing index...")
            run_index(today)


if __name__ == "__main__":
    main()
