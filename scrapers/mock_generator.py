"""Dynamic mock market simulator for MOCK_MODE.

Generates realistic flight quotes with calibrated advance yield curves,
day-of-week surges, carrier tiering, ATF fuel drift, statutory tax
breakdown, and statistical outliers — all driven by JetIndex YAML configs.

Adapted from VayuSutra-V4 market_feed.py (240 lines).
"""

from __future__ import annotations

import datetime
import math
import random
import uuid
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Config loaders
# ---------------------------------------------------------------------------

_CONFIG_DIR = Path("config")


def _load_yaml(filename: str) -> dict:
    with open(_CONFIG_DIR / filename) as f:
        return yaml.safe_load(f) or {}


def _load_routes() -> list[dict]:
    return _load_yaml("routes.yaml").get("routes", [])


def _load_airlines() -> list[dict]:
    return _load_yaml("airlines.yaml").get("airlines", [])


def _load_tax_rules() -> dict:
    return _load_yaml("tax_rules.yaml").get("tax_rules", {})


def _load_windows() -> list[dict]:
    return _load_yaml("windows.yaml").get("windows", [])


# ---------------------------------------------------------------------------
# Simulation config
# ---------------------------------------------------------------------------


class SimulationConfig:
    """Tunable knobs for the synthetic feed."""

    def __init__(
        self,
        seed: int | None = 42,
        anomaly_rate: float = 0.015,
        multi_ota_ratio: float = 0.65,
        atf_trend_drift: float = 0.0012,
        enable_noise: bool = True,
    ):
        self.seed = seed
        self.anomaly_rate = anomaly_rate
        self.multi_ota_ratio = multi_ota_ratio
        self.atf_trend_drift = atf_trend_drift
        self.enable_noise = enable_noise


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------


class MockMarketGenerator:
    """High-fidelity econometric market simulator."""

    def __init__(self, config: SimulationConfig | None = None):
        self.config = config or SimulationConfig()
        if self.config.seed is not None:
            random.seed(self.config.seed)

        # Load once
        self._routes = _load_routes()
        self._airlines = _load_airlines()
        self._tax = _load_tax_rules()
        self._windows = _load_windows()

    # -- yield curves -------------------------------------------------------

    def _advance_multiplier(self, window_id: str) -> float:
        """Non-linear yield curve per advance-purchase window."""
        ranges = {
            "T+1": (2.20, 3.15),
            "T+7": (1.45, 1.85),
            "T+15": (1.10, 1.28),
            "T+30": (0.96, 1.06),
            "T+45": (0.88, 0.96),
        }
        lo, hi = ranges.get(window_id, (1.0, 1.0))
        return random.uniform(lo, hi)

    def _day_of_week_multiplier(self, travel_date: datetime.date) -> float:
        """Demand surges: Fri evening + Sun return peaks, Tue/Wed troughs."""
        wd = travel_date.weekday()
        if wd == 4:
            return random.uniform(1.15, 1.24)
        elif wd == 6:
            return random.uniform(1.18, 1.28)
        elif wd in (1, 2):
            return random.uniform(0.90, 0.93)
        elif wd == 0:
            return random.uniform(1.02, 1.08)
        return random.uniform(0.98, 1.03)

    def _carrier_multiplier(self, airline_code: str) -> float:
        """FSC premium vs LCC discount."""
        code = airline_code.upper()
        if code == "AI":
            return random.uniform(1.12, 1.20)
        elif code == "6E":
            return random.uniform(0.99, 1.02)
        elif code in ("QP", "SG"):
            return random.uniform(0.92, 0.97)
        elif code == "IX":
            return random.uniform(0.96, 1.01)
        return random.uniform(0.98, 1.02)

    # -- tax breakdown ------------------------------------------------------

    def _calculate_taxes(self, base_and_fuel: float, is_ota: bool = False) -> dict[str, float]:
        """Statutory tax decomposition (ASF + PSF + UDF + GST + conv fee)."""
        t = self._tax
        asf = t.get("aviation_security_fee_asf", 200.0)
        psf = t.get("passenger_service_fee_psf", 91.0)
        udf = t.get("metro_udf_avg", 420.0)
        gst_rate = t.get("gst_rate_economy", 0.05)
        gst = round(base_and_fuel * gst_rate, 2)

        if is_ota:
            lo = t.get("ota_convenience_fee_min", 249.0)
            hi = t.get("ota_convenience_fee_max", 349.0)
            conv = round(random.uniform(lo, hi), 2)
        else:
            conv = t.get("direct_convenience_fee", 0.0)

        base_fare = round(base_and_fuel * 0.65, 2)
        fuel_surcharge = round(base_and_fuel * 0.35, 2)
        total = round(base_fare + fuel_surcharge + udf + psf + asf + gst + conv, 2)

        return {
            "base_fare": base_fare,
            "fuel_surcharge": fuel_surcharge,
            "udf": udf,
            "psf": psf,
            "asf": asf,
            "gst": gst,
            "convenience_fee": conv,
            "total_fare": total,
        }

    # -- quote generation ---------------------------------------------------

    def generate_quotes_for_date(
        self,
        booking_date: datetime.date,
        day_index: int = 0,
    ) -> list[dict[str, Any]]:
        """Generate simulated quotes for all routes across all advance windows."""
        quotes: list[dict[str, Any]] = []
        macro_drift = 1.0 + (day_index * self.config.atf_trend_drift) + (0.02 * math.sin(day_index / 5.0))

        for route in self._routes:
            for window in self._windows:
                travel_date = booking_date + datetime.timedelta(days=window.get("days_advance", 7))
                dow_mult = self._day_of_week_multiplier(travel_date)
                adv_mult = self._advance_multiplier(window["id"])

                # 4-6 flights per route-window
                flight_pool = [
                    ("6E", f"6E-{random.randint(100, 999)}", "06:15", "08:30"),
                    ("6E", f"6E-{random.randint(100, 999)}", "14:20", "16:40"),
                    ("6E", f"6E-{random.randint(100, 999)}", "19:45", "22:00"),
                    ("AI", f"AI-{random.randint(400, 899)}", "08:00", "10:15"),
                    ("AI", f"AI-{random.randint(400, 899)}", "17:30", "19:45"),
                    ("QP", f"QP-{random.randint(1100, 1499)}", "10:30", "12:45"),
                    ("SG", f"SG-{random.randint(100, 599)}", "12:15", "14:30"),
                ]
                sampled = random.sample(flight_pool, k=random.randint(4, len(flight_pool)))

                benchmark = route.get("base_fare_benchmark", 5000)

                for ccode, flt_num, dep, arr in sampled:
                    carrier_mult = self._carrier_multiplier(ccode)

                    base_price = (
                        benchmark * adv_mult * dow_mult * carrier_mult * macro_drift * random.uniform(0.97, 1.03)
                    )

                    # Direct portal quote
                    taxes = self._calculate_taxes(base_price, is_ota=False)

                    # Anomaly injection
                    is_anomaly = random.random() < self.config.anomaly_rate
                    if is_anomaly:
                        anomaly = random.choice(["HYPER_HIGH", "NEAR_ZERO", "CORRUPTED_ZERO"])
                        if anomaly == "HYPER_HIGH":
                            taxes["total_fare"] = round(taxes["total_fare"] * random.uniform(4.5, 7.5), 2)
                            taxes["base_fare"] = round(taxes["base_fare"] * 5.0, 2)
                        elif anomaly == "NEAR_ZERO":
                            taxes["total_fare"] = 149.00
                            taxes["base_fare"] = 10.00
                        else:
                            taxes["total_fare"] = 99999.00
                            taxes["base_fare"] = 85000.00

                    airline_name = ccode
                    for a in self._airlines:
                        if a.get("code") == ccode:
                            airline_name = a.get("name", ccode)
                            break

                    qid = f"Q-{booking_date:%Y%m%d}-{route['code']}-{window['id']}-{uuid.uuid4().hex[:8]}"
                    direct = {
                        "quote_id": qid,
                        "route_code": route["code"],
                        "origin": route["origin"],
                        "destination": route["destination"],
                        "airline_code": ccode,
                        "airline_name": airline_name,
                        "flight_number": flt_num,
                        "source_portal": f"DIRECT_{airline_name.upper().replace(' ', '')}",
                        "booking_date": booking_date.isoformat(),
                        "travel_date": travel_date.isoformat(),
                        "advance_window": window["id"],
                        "departure_time": dep,
                        "arrival_time": arr,
                        "is_direct": 1,
                        "currency": "INR",
                        "scraped_at": datetime.datetime.now(datetime.UTC).isoformat(),
                        **taxes,
                    }
                    quotes.append(direct)

                    # OTA duplicate for dedup testing
                    if random.random() < self.config.multi_ota_ratio and not is_anomaly:
                        ota = random.choice(["OTA_MAKEMYTRIP", "OTA_EASEMYTRIP", "OTA_CLEARTRIP"])
                        ota_taxes = self._calculate_taxes(base_price * random.uniform(0.99, 1.02), is_ota=True)
                        ota_q = {
                            "quote_id": f"OTA-{booking_date:%Y%m%d}-{route['code']}-{window['id']}-{uuid.uuid4().hex[:8]}",  # noqa: E501
                            "route_code": route["code"],
                            "origin": route["origin"],
                            "destination": route["destination"],
                            "airline_code": ccode,
                            "airline_name": airline_name,
                            "flight_number": flt_num,
                            "source_portal": ota,
                            "booking_date": booking_date.isoformat(),
                            "travel_date": travel_date.isoformat(),
                            "advance_window": window["id"],
                            "departure_time": dep,
                            "arrival_time": arr,
                            "is_direct": 0,
                            "currency": "INR",
                            "scraped_at": datetime.datetime.now(datetime.UTC).isoformat(),
                            **ota_taxes,
                        }
                        quotes.append(ota_q)

        return quotes

    def generate_multi_day(
        self,
        start_date: datetime.date,
        num_days: int = 35,
    ) -> list[dict[str, Any]]:
        """Generate a continuous daily panel across *num_days*."""
        all_quotes: list[dict[str, Any]] = []
        for d in range(num_days):
            current = start_date + datetime.timedelta(days=d)
            all_quotes.extend(self.generate_quotes_for_date(current, day_index=d))
        return all_quotes
