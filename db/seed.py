"""Seed the database with route basket and DGCA weights from config files."""

import csv
from pathlib import Path

import yaml
from loguru import logger
from sqlalchemy import select

from db.models import DgcaBenchmark, DgcaWeight, Route
from db.session import Base, SessionLocal, engine


def seed_routes(session) -> int:
    """Load routes from config/routes.yaml into the routes table."""
    with open("config/routes.yaml") as f:
        config = yaml.safe_load(f)

    routes = config["routes"]

    count = 0

    for route_data in routes:
        route_code = f"{route_data['origin']}-{route_data['destination']}"

        existing = session.execute(select(Route).where(Route.route_code == route_code)).scalar_one_or_none()

        if existing:
            continue

        route = Route(
            route_code=route_code,
            origin=route_data["origin"],
            destination=route_data["destination"],
            o_lat=route_data.get("o_lat"),
            o_lon=route_data.get("o_lon"),
            d_lat=route_data.get("d_lat"),
            d_lon=route_data.get("d_lon"),
            active=True,
        )

        session.add(route)
        count += 1

    session.commit()
    logger.info(f"Seeded {count} routes")
    return count


def seed_dgca_weights(session) -> int:
    """Load weights from config/dgca_weights.csv into dgca_weights table."""
    csv_path = Path("config/dgca_weights.csv")
    if not csv_path.exists():
        logger.warning("dgca_weights.csv not found, skipping")
        return 0

    count = 0
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Get route_id
            route = session.execute(select(Route).where(Route.route_code == row["route_code"])).scalar_one_or_none()

            if not route:
                logger.warning(f"Route {row['route_code']} not found, skipping weight")
                continue

            # Handle both old format (period, passengers) and new format (total_passengers)
            period = row.get("period", "2024-25")
            passengers = int(row.get("passengers", row.get("total_passengers", 0)))

            weight = DgcaWeight(
                route_id=route.id,
                period=period,
                passengers=passengers,
                weight=float(row["weight"]),
            )
            session.add(weight)
            count += 1

    session.commit()
    logger.info(f"Seeded {count} DGCA weights")
    return count


def seed_dgca_benchmarks(session) -> int:
    """Load monthly average fares from config/dgca_monthly_avg_fare.csv into dgca_benchmark table.

    Inserts one row per (route_code, month) combination from the CSV.
    """
    csv_path = Path("config/dgca_monthly_avg_fare.csv")
    if not csv_path.exists():
        logger.warning("dgca_monthly_avg_fare.csv not found, skipping")
        return 0

    count = 0
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            route_code = row["route_code"]
            month = row["month"]
            avg_fare = float(row["avg_fare_inr"])
            source = row.get("source", "")

            # Upsert: update if (route_code, month) already exists
            existing = (
                session.execute(
                    select(DgcaBenchmark).where(
                        DgcaBenchmark.route_code == route_code,
                        DgcaBenchmark.month == month,
                    )
                )
                .scalar_one_or_none()
            )

            if existing:
                existing.avg_fare = avg_fare
                existing.source_url = source
            else:
                benchmark = DgcaBenchmark(
                    route_code=route_code,
                    month=month,
                    avg_fare=avg_fare,
                    source_url=source,
                )
                session.add(benchmark)
            count += 1

    session.commit()
    logger.info(f"Seeded {count} DGCA benchmarks (per route)")
    return count


def seed():
    """Run all seed functions."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        n_routes = seed_routes(session)
        n_weights = seed_dgca_weights(session)
        n_benchmarks = seed_dgca_benchmarks(session)
        logger.info(f"Seeding complete: {n_routes} routes, {n_weights} weights, {n_benchmarks} benchmarks")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
