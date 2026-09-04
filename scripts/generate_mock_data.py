"""Generate deterministic mock data for APIx demo mode.

Produces 5 JSON files in data/mock/ matching API response shapes:
- fare_quotes.json
- apix_daily.json
- heatmap.json
- elasticity.json
- backtest.json

Run: python scripts/generate_mock_data.py
"""

import json
import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np

# Seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

MOCK_DIR = Path("data/mock")
MOCK_DIR.mkdir(parents=True, exist_ok=True)

ROUTES = [
    {
        "code": "DEL-BOM",
        "origin": "DEL",
        "dest": "BOM",
        "o_lat": 28.5562,
        "o_lon": 77.1000,
        "d_lat": 19.0896,
        "d_lon": 72.8656,
    },
    {
        "code": "DEL-BLR",
        "origin": "DEL",
        "dest": "BLR",
        "o_lat": 28.5562,
        "o_lon": 77.1000,
        "d_lat": 13.1986,
        "d_lon": 77.7066,
    },
    {
        "code": "BOM-BLR",
        "origin": "BOM",
        "dest": "BLR",
        "o_lat": 19.0896,
        "o_lon": 72.8656,
        "d_lat": 13.1986,
        "d_lon": 77.7066,
    },
    {
        "code": "DEL-CCU",
        "origin": "DEL",
        "dest": "CCU",
        "o_lat": 28.5562,
        "o_lon": 77.1000,
        "d_lat": 22.6520,
        "d_lon": 88.4463,
    },
    {
        "code": "BLR-HYD",
        "origin": "BLR",
        "dest": "HYD",
        "o_lat": 13.1986,
        "o_lon": 77.7066,
        "d_lat": 17.2403,
        "d_lon": 78.4294,
    },
    {
        "code": "MAA-DEL",
        "origin": "MAA",
        "dest": "DEL",
        "o_lat": 12.9941,
        "o_lon": 80.1709,
        "d_lat": 28.5562,
        "d_lon": 77.1000,
    },
]

LEAD_TIMES = [1, 7, 15, 30, 45]
CARRIERS = [
    {"code": "6E", "name": "IndiGo"},
    {"code": "AI", "name": "Air India"},
    {"code": "QP", "name": "Akasa Air"},
]

# Base fares by route (INR)
BASE_FARES = {
    "DEL-BOM": 5000,
    "DEL-BLR": 5500,
    "BOM-BLR": 4500,
    "DEL-CCU": 6000,
    "BLR-HYD": 3500,
    "MAA-DEL": 5000,
}

# Lead-time decay factor: T+1 ≈ 1.8x T+45
LEAD_DECAY = {
    1: 1.8,
    7: 1.4,
    15: 1.15,
    30: 1.05,
    45: 1.0,
}


def generate_fare_quotes():
    """Generate ~300 realistic clean quotes."""
    quotes = []
    base_date = date.today() - timedelta(days=45)
    flight_counter = 100

    for route in ROUTES:
        for lead in LEAD_TIMES:
            for carrier in CARRIERS:
                depart_date = base_date + timedelta(days=45 + lead)
                scrape_date = base_date + timedelta(days=45)

                base_fare = BASE_FARES[route["code"]]
                fare_with_lead = base_fare * LEAD_DECAY[lead]

                # Add some randomness
                base_fare_actual = fare_with_lead * random.uniform(0.9, 1.1)
                udf = random.uniform(100, 800)
                taxes = base_fare_actual * random.uniform(0.05, 0.12)
                conv_fee = random.uniform(300, 400)
                other_fees = random.uniform(0, 200)
                total = base_fare_actual + udf + taxes + conv_fee + other_fees

                flight_counter += 1
                quotes.append(
                    {
                        "route_code": route["code"],
                        "origin": route["origin"],
                        "destination": route["dest"],
                        "carrier": carrier["code"],
                        "flight_no": f"{carrier['code']}-{flight_counter}",
                        "depart_date": depart_date.isoformat(),
                        "scrape_date": scrape_date.isoformat(),
                        "lead_time": lead,
                        "fare_class": random.choice(["Saver", "Flexi", "Economy"]),
                        "base_fare": round(base_fare_actual, 2),
                        "udf": round(udf, 2),
                        "taxes": round(taxes, 2),
                        "convenience_fee": round(conv_fee, 2),
                        "other_fees": round(other_fees, 2),
                        "total_fare": round(total, 2),
                        "source": "indigo" if carrier["code"] == "6E" else "makemytrip",
                        "quality_flag": "ok",
                    }
                )

    return quotes


def generate_apix_daily():
    """Generate 45 days of index values."""
    base_date = date.today() - timedelta(days=45)
    daily = []
    apix = 100.0

    for i in range(45):
        d = base_date + timedelta(days=i)
        # Small daily fluctuation
        change = np.random.normal(0, 0.3)
        apix = max(90, min(110, apix + change))
        base_only = apix * random.uniform(0.98, 1.02)

        daily.append(
            {
                "date": d.isoformat(),
                "apix": round(apix, 4),
                "apix_base_only": round(base_only, 4),
                "pct_change_dod": round(change, 4),
                "n_quotes": random.randint(15, 30),
                "n_routes": 6,
            }
        )

    return daily


def generate_heatmap():
    """Generate heatmap data for each route."""
    heatmap = []
    for route in ROUTES:
        base_fare = BASE_FARES[route["code"]]
        heatmap.append(
            {
                "route_id": ROUTES.index(route) + 1,
                "origin": route["origin"],
                "dest": route["dest"],
                "o_lat": route["o_lat"],
                "o_lon": route["o_lon"],
                "d_lat": route["d_lat"],
                "d_lon": route["d_lon"],
                "avg_fare": round(base_fare * random.uniform(0.95, 1.05), 2),
                "volatility": round(random.uniform(0.02, 0.12), 4),
                "index_contrib": round(random.uniform(0.1, 0.3), 4),
            }
        )

    return heatmap


def generate_elasticity():
    """Generate elasticity data: fare vs lead time."""
    elasticity = []
    for lead in LEAD_TIMES:
        base_fare = 5000 * LEAD_DECAY[lead]
        elasticity.append(
            {
                "lead_time": lead,
                "avg_total_fare": round(base_fare * random.uniform(1.1, 1.3), 2),
                "avg_base_fare": round(base_fare * random.uniform(0.8, 1.0), 2),
                "n": random.randint(8, 25),
            }
        )

    return elasticity


def generate_backtest():
    """Generate backtest results."""
    monthly = []
    for i in range(3):
        month = (date.today().replace(day=1) - timedelta(days=30 * (2 - i))).strftime("%Y-%m")
        apix = 100 + np.random.normal(0, 2)
        dgca = 5000 + np.random.normal(0, 200)
        apix_implied = (apix / 100) * 5000
        error = abs(apix_implied - dgca) / dgca * 100

        monthly.append(
            {
                "month": month,
                "apix_avg": round(apix, 4),
                "dgca_avg_fare": round(dgca, 2),
                "apix_rebased": round(apix, 4),
                "error_pct": round(error, 2),
            }
        )

    return {
        "monthly": monthly,
        "summary": {
            "mape": round(abs(np.random.normal(2, 1)), 2),
            "rmse": round(abs(np.random.normal(50, 20)), 2),
            "corr": round(0.95 + np.random.uniform(0, 0.04), 4),
        },
    }


def main():
    """Generate all mock data files."""
    print("Generating mock data...")

    fare_quotes = generate_fare_quotes()
    with open(MOCK_DIR / "fare_quotes.json", "w") as f:
        json.dump(fare_quotes, f, indent=2)
    print(f"  fare_quotes.json: {len(fare_quotes)} quotes")

    apix_daily = generate_apix_daily()
    with open(MOCK_DIR / "apix_daily.json", "w") as f:
        json.dump(apix_daily, f, indent=2)
    print(f"  apix_daily.json: {len(apix_daily)} days")

    heatmap = generate_heatmap()
    with open(MOCK_DIR / "heatmap.json", "w") as f:
        json.dump(heatmap, f, indent=2)
    print(f"  heatmap.json: {len(heatmap)} routes")

    elasticity = generate_elasticity()
    with open(MOCK_DIR / "elasticity.json", "w") as f:
        json.dump(elasticity, f, indent=2)
    print(f"  elasticity.json: {len(elasticity)} entries")

    backtest = generate_backtest()
    with open(MOCK_DIR / "backtest.json", "w") as f:
        json.dump(backtest, f, indent=2)
    print(f"  backtest.json: {len(backtest['monthly'])} months")

    print("\nAll mock data generated successfully!")


if __name__ == "__main__":
    main()
