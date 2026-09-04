#!/bin/bash
# Run a single scrape for one route, one lead time, no proxy
# Usage: bash scripts/run_local_sweep.sh DEL-BOM 7 indigo

set -euo pipefail

ROUTE="${1:-DEL-BOM}"
LEAD="${2:-7}"
SOURCE="${3:-indigo}"

echo "Running local sweep: ${SOURCE} ${ROUTE} T+${LEAD}"
python -m app.tasks.scrape_tasks --route "${ROUTE}" --lead "${LEAD}" --source "${SOURCE}"
