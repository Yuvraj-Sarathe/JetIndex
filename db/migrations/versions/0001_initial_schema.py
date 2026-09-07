"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-05

Creates all six tables from db/models.py, converts fare_quotes into a
TimescaleDB hypertable partitioned on scraped_at, and adds the composite
indexes the engine queries rely on.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- routes ---------------------------------------------------------
    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("route_code", sa.String(length=10), nullable=False),
        sa.Column("origin", sa.String(length=3), nullable=False),
        sa.Column("destination", sa.String(length=3), nullable=False),
        sa.Column("o_lat", sa.Float(), nullable=True),
        sa.Column("o_lon", sa.Float(), nullable=True),
        sa.Column("d_lat", sa.Float(), nullable=True),
        sa.Column("d_lon", sa.Float(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_routes_route_code", "route_code", unique=True),
    )

    # --- raw_quotes (audit / landing) -----------------------------------
    op.create_table(
        "raw_quotes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("scrape_date", sa.Date(), nullable=False),
        sa.Column("depart_date", sa.Date(), nullable=False),
        sa.Column("lead_time", sa.Integer(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("method", sa.String(length=20), nullable=True),
        sa.Column("proxy_used", sa.String(length=255), nullable=True),
        sa.Column("raw_path", sa.String(length=500), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- fare_quotes (clean quotes — becomes a hypertable) --------------
    # NOTE: TimescaleDB requires the partitioning column (scraped_at) to be
    # part of the primary key. We create the table without a PK first, then
    # add a composite PK after creating the hypertable.
    op.create_table(
        "fare_quotes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("carrier", sa.String(length=10), nullable=False),
        sa.Column("flight_no", sa.String(length=20), nullable=True),
        sa.Column("depart_date", sa.Date(), nullable=False),
        sa.Column("depart_time", sa.DateTime(), nullable=True),
        sa.Column("lead_time", sa.Integer(), nullable=False),
        sa.Column("fare_class", sa.String(length=30), nullable=True),
        sa.Column("base_fare", sa.Float(), nullable=False),
        sa.Column("udf", sa.Float(), nullable=True),
        sa.Column("taxes", sa.Float(), nullable=True),
        sa.Column("convenience_fee", sa.Float(), nullable=True),
        sa.Column("other_fees", sa.Float(), nullable=True),
        sa.Column("total_fare", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("is_refundable", sa.Boolean(), nullable=True),
        sa.Column("stops", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("raw_quote_id", sa.Integer(), nullable=True),
        sa.Column("quality_flag", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["raw_quote_id"], ["raw_quotes.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        # No PrimaryKeyConstraint here — added after hypertable creation
        sa.Index("ix_fare_quotes_carrier", "carrier"),
        sa.Index("ix_fare_quotes_lead_time", "lead_time"),
        sa.Index("ix_fare_quotes_route_id", "route_id"),
        sa.Index("ix_fare_quotes_scraped_at", "scraped_at"),
    )

    # Create sequence for auto-incrementing id (required for TimescaleDB hypertable)
    op.execute("CREATE SEQUENCE IF NOT EXISTS fare_quotes_id_seq OWNED BY fare_quotes.id")
    op.execute("ALTER TABLE fare_quotes ALTER COLUMN id SET DEFAULT nextval('fare_quotes_id_seq')")

    # --- apix_daily ------------------------------------------------------
    op.create_table(
        "apix_daily",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("apix", sa.Float(), nullable=False),
        sa.Column("apix_base_only", sa.Float(), nullable=True),
        sa.Column("n_quotes", sa.Integer(), nullable=True),
        sa.Column("n_routes", sa.Integer(), nullable=True),
        sa.Column("method", sa.String(length=20), nullable=True),
        sa.Column("base_period", sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint("date"),
    )

    # --- dgca_weights -----------------------------------------------------
    op.create_table(
        "dgca_weights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(length=10), nullable=False),
        sa.Column("passengers", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- dgca_benchmark (per-route monthly avg fares) ----------------------
    op.create_table(
        "dgca_benchmark",
        sa.Column("route_code", sa.String(length=10), nullable=False),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column("avg_fare", sa.Float(), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("route_code", "month"),
    )

    # --- Convert fare_quotes into a TimescaleDB hypertable ---------------
    # Must run AFTER create_table. Partitioned on scraped_at with 7-day chunks.
    op.execute(
        """
        SELECT create_hypertable(
            'fare_quotes',
            'scraped_at',
            chunk_time_interval => INTERVAL '7 days',
            if_not_exists => TRUE
        );
        """
    )

    # --- Add composite primary key including scraped_at -----------------
    # TimescaleDB requires the partitioning column in the primary key.
    op.create_primary_key(
        "pk_fare_quotes",
        "fare_quotes",
        ["id", "scraped_at"],
    )

    # --- Composite indexes the engine queries need -----------------------
    op.create_index(
        "ix_fare_quotes_route_lead_scrape",
        "fare_quotes",
        ["route_id", "lead_time", "scraped_at"],
    )
    op.create_index(
        "ix_fare_quotes_quality",
        "fare_quotes",
        ["quality_flag"],
    )


def downgrade() -> None:
    # Drop composite indexes (hypertable indexes are dropped with the table)
    op.drop_index("ix_fare_quotes_quality", table_name="fare_quotes")
    op.drop_index("ix_fare_quotes_route_lead_scrape", table_name="fare_quotes")

    # Drop tables in reverse dependency order
    op.drop_table("dgca_benchmark")
    op.drop_table("dgca_weights")
    op.drop_table("apix_daily")
    op.drop_table("fare_quotes")  # DROP TABLE works on hypertables
    op.drop_table("raw_quotes")
    op.drop_table("routes")
