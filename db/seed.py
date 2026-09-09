"""Seed the database with route basket, DGCA weights, and config data.

Updated to support 20-route DGCA basket from VayuSutra-V4.
"""

import csv
from pathlib import Path

import yaml
from loguru import logger
from sqlalchemy import select

from db.models import DgcaBenchmark, DgcaWeight, Route
from db.session import Base, SessionLocal, engine


def seed_routes(session) -> int:
    """Load routes from config/routes.yaml into the routes table.

    Supports both old format (6 routes, no metadata) and new format (20 routes
    with weight, distance_km, is_metro, base_fare_benchmark, city_name).
    """
    with open("config/routes.yaml") as f:
        config = yaml.safe_load(f)

    routes = config["routes"]

    count = 0

    for route_data in routes:
        route_code = route_data.get("route_code", f"{route_data['origin']}-{route_data['destination']}")

        existing = session.execute(select(Route).where(Route.route_code == route_code)).scalar_one_or_none()

        if existing:
            # Update metadata fields if they exist on the model
            if hasattr(existing, "weight") and route_data.get("weight"):
                existing.weight = route_data["weight"]
            if hasattr(existing, "distance_km") and route_data.get("distance_km"):
                existing.distance_km = route_data["distance_km"]
            if hasattr(existing, "is_metro") and route_data.get("is_metro") is not None:
                existing.is_metro = route_data["is_metro"]
            if hasattr(existing, "base_fare_benchmark") and route_data.get("base_fare_benchmark"):
                existing.base_fare_benchmark = route_data["base_fare_benchmark"]
            continue

        route_kwargs = dict(
            route_code=route_code,
            origin=route_data["origin"],
            destination=route_data["destination"],
            o_lat=route_data.get("o_lat"),
            o_lon=route_data.get("o_lon"),
            d_lat=route_data.get("d_lat"),
            d_lon=route_data.get("d_lon"),
            active=True,
        )

        # New fields from expanded 20-route config
        if "weight" in route_data:
            route_kwargs["weight"] = route_data["weight"]
        if "distance_km" in route_data:
            route_kwargs["distance_km"] = route_data["distance_km"]
        if "is_metro" in route_data:
            route_kwargs["is_metro"] = route_data["is_metro"]
        if "base_fare_benchmark" in route_data:
            route_kwargs["base_fare_benchmark"] = route_data["base_fare_benchmark"]

        route = Route(**route_kwargs)

        session.add(route)
        count += 1

    session.commit()
    logger.info("Seeded {} routes (20-route DGCA basket)", count)
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
                logger.warning("Route {} not found, skipping weight", row["route_code"])
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
    logger.info("Seeded {} DGCA weights", count)
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
            existing = session.execute(
                select(DgcaBenchmark).where(
                    DgcaBenchmark.route_code == route_code,
                    DgcaBenchmark.month == month,
                )
            ).scalar_one_or_none()

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
    logger.info("Seeded {} DGCA benchmarks (per route)", count)
    return count


def seed_airlines(session) -> int:
    """Validate airlines config exists and is loadable (stored in YAML, read at runtime)."""
    config_path = Path("config/airlines.yaml")
    if not config_path.exists():
        logger.warning("airlines.yaml not found, skipping")
        return 0

    with open(config_path) as f:
        config = yaml.safe_load(f)

    airlines = config.get("airlines", [])
    total_share = sum(a["market_share"] for a in airlines)
    logger.info("Loaded {} airlines (total market share: {:.4f})", len(airlines), total_share)
    return len(airlines)


def seed_tax_rules(session) -> int:
    """Validate tax_rules config exists and is loadable (stored in YAML, read at runtime)."""
    config_path = Path("config/tax_rules.yaml")
    if not config_path.exists():
        logger.warning("tax_rules.yaml not found, skipping")
        return 0

    with open(config_path) as f:
        config = yaml.safe_load(f)

    gst = config.get("gst", {})
    fees = config.get("fees", {})
    logger.info(
        "Loaded tax rules: GST economy={}%, ASF=₹{}, PSF=₹{}",
        gst.get("rate_economy", 0) * 100,
        fees.get("aviation_security_fee", 0),
        fees.get("passenger_service_fee", 0),
    )
    return 1


def seed_cpi_weights(session) -> int:
    """Validate CPI weights config exists and is loadable."""
    config_path = Path("config/cpi_weights.yaml")
    if not config_path.exists():
        logger.warning("cpi_weights.yaml not found, skipping")
        return 0

    with open(config_path) as f:
        config = yaml.safe_load(f)

    logger.info(
        "Loaded CPI weights: transport={}%, airfare={}%, headline={:.4f}%",
        config.get("transport_and_communication_cpi_weight", 0) * 100,
        config.get("airfare_share_within_transport", 0) * 100,
        config.get("effective_headline_cpi_weight", 0) * 100,
    )
    return 1


def seed_windows(session) -> int:
    """Validate advance purchase windows config exists and is loadable."""
    config_path = Path("config/windows.yaml")
    if not config_path.exists():
        logger.warning("windows.yaml not found, skipping")
        return 0

    with open(config_path) as f:
        config = yaml.safe_load(f)

    windows = config.get("windows", [])
    total_weight = sum(w["weight"] for w in windows)
    logger.info("Loaded {} advance purchase windows (total weight: {:.4f})", len(windows), total_weight)
    return len(windows)


def seed():
    """Run all seed functions."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        n_routes = seed_routes(session)
        n_weights = seed_dgca_weights(session)
        n_benchmarks = seed_dgca_benchmarks(session)
        n_airlines = seed_airlines(session)
        n_tax = seed_tax_rules(session)
        n_cpi = seed_cpi_weights(session)
        n_windows = seed_windows(session)
        logger.info(
            "Seeding complete: {} routes, {} weights, {} benchmarks, "
            "{} airlines, {} tax rules, {} CPI weights, {} windows",
            n_routes,
            n_weights,
            n_benchmarks,
            n_airlines,
            n_tax,
            n_cpi,
            n_windows,
        )
    finally:
        session.close()


if __name__ == "__main__":
    seed()
