"""Fare unbundler — maps vendor-specific labels to canonical components."""

import re

from loguru import logger

from pipeline.schemas import CleanQuote, RawQuote

# IndiGo fee label mapping
INDIGO_FEE_MAP = {
    r"base\s*fare": "base_fare",
    r"fare": "base_fare",
    r"airfare": "base_fare",
    r"user\s*development\s*fee|udf|adf": "udf",
    r"psf|asf|aviation\s*security": "taxes",
    r"gst|k3|cute": "taxes",
    r"convenience\s*fee|service\s*fee|platform\s*fee": "convenience_fee",
    r"fuel\s*surcharge|yq|seat|meal|insurance": "other_fees",
}

# MakeMyTrip fee label mapping
MMT_FEE_MAP = {
    r"base\s*fare": "base_fare",
    r"fare": "base_fare",
    r"airfare": "base_fare",
    r"user\s*development\s*fee|udf|adf": "udf",
    r"psf|asf|aviation\s*security": "taxes",
    r"gst|k3|cute": "taxes",
    r"convenience\s*fee|service\s*fee|platform\s*fee": "convenience_fee",
    r"fuel\s*surcharge|yq|seat|meal|insurance": "other_fees",
}

# Source-specific maps
SOURCE_MAPS = {
    "indigo": INDIGO_FEE_MAP,
    "makemytrip": MMT_FEE_MAP,
    "airindia": INDIGO_FEE_MAP,  # default to indigo map
    "akasa": INDIGO_FEE_MAP,
    "easemytrip": MMT_FEE_MAP,
}

# Statutory fee constants (INR) — used by reverse-decompose fallback
_STATUTORY_FEES = {
    "asf": 200.0,
    "psf": 91.0,
    "udf": 420.0,
    "gst_rate": 0.05,
    "base_fuel_split": (0.65, 0.35),  # 65% base, 35% fuel surcharge
}


def _match_label(label: str, fee_map: dict[str, str]) -> str | None:
    """Match a vendor label against a fee map, returning canonical field or None."""
    label_lower = label.lower().strip()
    for pattern, canonical in fee_map.items():
        if re.search(pattern, label_lower):
            return canonical
    return None


def unbundle(q: RawQuote) -> CleanQuote:
    """
    Convert a RawQuote to a CleanQuote by unbundling fare_breakdown
    into canonical components (base_fare, udf, taxes, convenience_fee, other_fees).
    """
    fee_map = SOURCE_MAPS.get(q.source, INDIGO_FEE_MAP)

    # Accumulate components
    components: dict[str, float] = {
        "base_fare": 0.0,
        "udf": 0.0,
        "taxes": 0.0,
        "convenience_fee": 0.0,
        "other_fees": 0.0,
    }

    unmapped_labels = []

    for label, amount in q.fare_breakdown.items():
        canonical = _match_label(label, fee_map)
        if canonical:
            components[canonical] += amount
        else:
            # Regex fallback — try to categorize by common keywords
            if any(kw in label.lower() for kw in ["base", "fare", "ticket"]):
                components["base_fare"] += amount
            elif any(kw in label.lower() for kw in ["tax", "gst", "surcharge", "fee"]):
                components["taxes"] += amount
            else:
                unmapped_labels.append(label)
                components["other_fees"] += amount

    if unmapped_labels:
        logger.warning(f"Unmapped labels for {q.flight_no}: {unmapped_labels}")

    # Check sum consistency
    computed_total = sum(components.values())
    quality_flag = "ok"
    if abs(computed_total - q.total_fare) > 5.0:
        quality_flag = "sum_mismatch"
        logger.warning(
            f"Sum mismatch for {q.flight_no}: computed={computed_total:.2f}, "
            f"reported={q.total_fare:.2f}, diff={abs(computed_total - q.total_fare):.2f}"
        )

    return CleanQuote(
        route_code=q.route_code,
        origin=q.origin,
        destination=q.destination,
        carrier=q.carrier,
        flight_no=q.flight_no,
        depart_date=q.depart_date,
        depart_time=q.depart_time,
        scrape_date=q.scrape_date,
        scraped_at=q.scraped_at,
        lead_time=q.lead_time,
        fare_class=q.fare_class,
        stops=q.stops,
        is_refundable=q.is_refundable,
        source=q.source,
        currency=q.currency,
        base_fare=round(components["base_fare"], 2),
        udf=round(components["udf"], 2),
        taxes=round(components["taxes"], 2),
        convenience_fee=round(components["convenience_fee"], 2),
        other_fees=round(components["other_fees"], 2),
        total_fare=q.total_fare,
        quality_flag=quality_flag,
        raw_ref=q.raw_ref,
    )


def reverse_decompose(total_fare: float, is_ota: bool = False) -> dict[str, float]:
    """Reverse-engineer statutory components from a total fare.

    Use this when a scraper only provides a single total fare number
    (no breakdown).  The approach:

    1. Subtract statutory airport fees (ASF + PSF + UDF) and convenience fee
    2. The remainder is base + fuel + GST
    3. Remove GST (5% on base + fuel) to get net base+fuel
    4. Split base vs fuel 65/35 (typical Indian aviation split)

    Returns a dict with: base_fare, fuel_surcharge, asf, psf, udf,
    gst, convenience_fee, total_fare.
    """
    f = _STATUTORY_FEES
    conv_fee = 300.0 if is_ota else 0.0

    net_after_fees = max(1000.0, total_fare - (f["asf"] + f["psf"] + f["udf"] + conv_fee))
    base_plus_fuel = net_after_fees / (1.0 + f["gst_rate"])
    gst = net_after_fees - base_plus_fuel

    base_share, fuel_share = f["base_fuel_split"]
    base_fare = round(base_plus_fuel * base_share, 2)
    fuel_surcharge = round(base_plus_fuel * fuel_share, 2)

    return {
        "base_fare": base_fare,
        "fuel_surcharge": fuel_surcharge,
        "udf": f["udf"],
        "psf": f["psf"],
        "asf": f["asf"],
        "gst": round(gst, 2),
        "convenience_fee": round(conv_fee, 2),
        "total_fare": round(total_fare, 2),
    }
