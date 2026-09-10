"""Standalone scraper test runner.

Tests individual scrapers against real airline/OTA endpoints.
Does NOT require Celery, PostgreSQL, or Redis.

Usage:
    python -m scrapers.test_run --source indigo --route DEL-BOM --lead 7
    python -m scrapers.test_run --source makemytrip --route DEL-BOM --lead 7
    python -m scrapers.test_run --all --route DEL-BOM --lead 7
    python -m scrapers.test_run --source indigo --routes DEL-BOM,DEL-BLR,BOM-BLR --lead 7
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_scraper(source: str, route_code: str, lead_time: int, verbose: bool = False) -> dict:
    """Test a single scraper with one route."""
    from scrapers.base_scraper import ScrapeJob
    from scrapers.registry import get_scraper

    today = date.today()
    origin, destination = route_code.split("-")
    depart_date = today + timedelta(days=lead_time)

    job = ScrapeJob(
        source=source,
        origin=origin,
        destination=destination,
        depart_date=depart_date,
        lead_time=lead_time,
        scrape_date=today,
    )

    try:
        scraper = get_scraper(source)
    except ValueError as e:
        return {"source": source, "route": route_code, "ok": False, "error": str(e)}

    results = scraper.run_jobs([job])
    result = results[0]

    output = {
        "source": source,
        "route": route_code,
        "lead_time": lead_time,
        "depart_date": str(depart_date),
        "ok": result.ok,
        "status_code": result.status_code,
        "method": result.method,
        "error": result.error,
        "raw_path": str(result.raw_path) if result.raw_path else None,
    }

    if verbose and result.raw_path and Path(result.raw_path).exists():
        with open(result.raw_path) as f:
            data = json.load(f)
        if isinstance(data, list):
            output["n_flights"] = len(data)
            if data:
                output["sample_fare"] = data[0].get("total_fare") or data[0].get("fare", {}).get("totalAmount")
        elif isinstance(data, dict):
            output["response_keys"] = list(data.keys())[:10]

    return output


def main():
    parser = argparse.ArgumentParser(description="Test scrapers against real endpoints")
    parser.add_argument("--source", help="Source name (indigo, makemytrip, airindia)")
    parser.add_argument("--route", default="DEL-BOM", help="Route code (e.g. DEL-BOM)")
    parser.add_argument("--routes", help="Comma-separated route codes")
    parser.add_argument("--lead", type=int, default=7, help="Lead time in days")
    parser.add_argument("--all", action="store_true", help="Test all enabled sources")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show response details")
    args = parser.parse_args()

    sources = []
    if args.all:
        sources = ["indigo", "makemytrip"]
    elif args.source:
        sources = [args.source]
    else:
        parser.error("Must specify --source or --all")

    routes = [args.route]
    if args.routes:
        routes = [r.strip() for r in args.routes.split(",")]

    results = []
    for source in sources:
        for route in routes:
            print(f"\n{'='*50}")
            print(f"Testing {source} | {route} | T+{args.lead}")
            print(f"{'='*50}")

            result = test_scraper(source, route, args.lead, verbose=args.verbose)
            results.append(result)

            status = "OK" if result["ok"] else "FAILED"
            print(f"  Status: {status}")
            if result.get("status_code"):
                print(f"  HTTP: {result['status_code']}")
            if result.get("error"):
                print(f"  Error: {result['error']}")
            if result.get("raw_path"):
                print(f"  Raw: {result['raw_path']}")
            if args.verbose:
                for key in ("n_flights", "sample_fare", "response_keys", "method"):
                    if key in result and result[key] is not None:
                        print(f"  {key}: {result[key]}")

    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: {sum(1 for r in results if r['ok'])}/{len(results)} passed")
    print(f"{'='*50}")

    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"  [{status}] {r['source']}/{r['route']} T+{r['lead_time']}")
        if r.get("error"):
            print(f"         {r['error'][:80]}")

    sys.exit(0 if all(r["ok"] for r in results) else 1)


if __name__ == "__main__":
    main()
