#!/bin/bash
# Wait for PostgreSQL to be ready
# Used by docker-compose to ensure DB is healthy before migrations

set -euo pipefail

DB_HOST="${1:-db}"
DB_PORT="${2:-5432}"
DB_USER="${3:-apix}"

echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -q 2>/dev/null; do
    echo -n "."
    sleep 2
done

echo " PostgreSQL is ready!"
