-- TimescaleDB initialization
-- Runs on first container start via docker-compose volume mount

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Note: Tables are created via Alembic migrations.
-- The hypertable conversion is done in the first Alembic migration:
-- SELECT create_hypertable('fare_quotes', 'scraped_at', if_not_exists => TRUE);
