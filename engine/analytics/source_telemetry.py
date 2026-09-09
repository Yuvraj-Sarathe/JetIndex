"""
JetIndex - Dashboard Source Telemetry & Route Movement (Read-Only)
Ported from VayuSutra-V4 with SQLAlchemy adaptation.
"""

import datetime
import logging
from typing import Any

from db.models import CleanedQuote, RawQuote, RouteIndex
from db.session import SessionLocal

logger = logging.getLogger("jetindex.source_telemetry")

PORTAL_LABELS = {
    "DIRECT_INDIGO": ("IndiGo", "AIRLINE_DIRECT"),
    "DIRECT_AIRINDIA": ("Air India", "AIRLINE_DIRECT"),
    "DIRECT_AKASA": ("Akasa Air", "AIRLINE_DIRECT"),
    "DIRECT_SPICEJET": ("SpiceJet", "AIRLINE_DIRECT"),
    "OTA_MAKEMYTRIP": ("MakeMyTrip", "OTA_AGGREGATOR"),
    "OTA_EASEMYTRIP": ("EaseMyTrip", "OTA_AGGREGATOR"),
    "OTA_CLEARTRIP": ("Cleartrip", "OTA_AGGREGATOR"),
}

WINDOW_WEIGHTS = {1: 0.22, 7: 0.34, 15: 0.24, 30: 0.14, 45: 0.06}

DGCA_ROUTES = {
    "DEL-BOM": ("New Delhi", "Mumbai", 0.1092),
    "DEL-BLR": ("New Delhi", "Bengaluru", 0.0805),
    "BOM-BLR": ("Mumbai", "Bengaluru", 0.0712),
    "DEL-MAA": ("New Delhi", "Chennai", 0.0543),
    "BOM-DEL": ("Mumbai", "New Delhi", 0.0498),
    "DEL-CCU": ("New Delhi", "Kolkata", 0.0467),
    "BOM-MAA": ("Mumbai", "Chennai", 0.0412),
    "BLR-HYD": ("Bengaluru", "Hyderabad", 0.0389),
    "DEL-HYD": ("New Delhi", "Hyderabad", 0.0378),
    "BOM-CCU": ("Mumbai", "Kolkata", 0.0356),
    "DEL-GOI": ("New Delhi", "Goa", 0.0334),
    "BOM-GOI": ("Mumbai", "Goa", 0.0312),
    "BLR-CCU": ("Bengaluru", "Kolkata", 0.0298),
    "DEL-JAI": ("New Delhi", "Jaipur", 0.0287),
    "BOM-HYD": ("Mumbai", "Hyderabad", 0.0276),
    "DEL-AMD": ("New Delhi", "Ahmedabad", 0.0265),
    "BLR-MAA": ("Bengaluru", "Chennai", 0.0254),
    "CCU-BLR": ("Kolkata", "Bengaluru", 0.0243),
    "HYD-MAA": ("Hyderabad", "Chennai", 0.0232),
    "DEL-IXC": ("New Delhi", "Chandigarh", 0.0221),
}


def get_source_telemetry() -> dict[str, Any]:
    """Per-channel collection status: quote counts, latest activity, fare movement."""
    db = SessionLocal()
    try:
        from sqlalchemy import func

        # Get latest two booking dates
        dates = db.query(RawQuote.booking_date).distinct().order_by(RawQuote.booking_date.desc()).limit(2).all()
        latest_date = str(dates[0][0]) if dates else None
        prev_date = str(dates[1][0]) if len(dates) > 1 else None

        channels: list[dict[str, Any]] = []
        summary = {
            "as_of_date": latest_date,
            "previous_date": prev_date,
            "channels_healthy": 0,
            "channels_total": 0,
            "quotes_today_total": 0,
            "validated_quotes_today": 0,
            "outliers_today": 0,
            "average_fare_today_inr": None,
            "average_fare_previous_inr": None,
            "national_fare_change_pct": None,
            "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }

        today_stats_all: list[float] = []
        prev_stats_all: list[float] = []

        for portal, (label, stype) in PORTAL_LABELS.items():
            # Current date stats
            cur_row = (
                db.query(
                    func.count().label("cnt"),
                    func.avg(RawQuote.total_fare).label("avg_fare"),
                )
                .filter(
                    RawQuote.source_portal == portal,
                    RawQuote.booking_date == latest_date,
                )
                .first()
                if latest_date
                else None
            )

            cur_cnt = cur_row[0] if cur_row else 0
            cur_avg = float(cur_row[1]) if cur_row and cur_row[1] else None

            # Previous date stats
            prev_row = (
                db.query(
                    func.count().label("cnt"),
                    func.avg(RawQuote.total_fare).label("avg_fare"),
                )
                .filter(
                    RawQuote.source_portal == portal,
                    RawQuote.booking_date == prev_date,
                )
                .first()
                if prev_date
                else None
            )

            prev_row[0] if prev_row else 0
            prev_avg = float(prev_row[1]) if prev_row and prev_row[1] else None

            if cur_avg is not None:
                today_stats_all.append(cur_avg)
            if prev_avg is not None:
                prev_stats_all.append(prev_avg)

            # 30-day count
            cnt30 = (
                db.query(func.count())
                .filter(
                    RawQuote.source_portal == portal,
                )
                .scalar()
                or 0
            )

            health = "SUCCESS" if cur_cnt and cur_cnt > 0 else "DELAYED"

            fare_change = None
            if cur_avg is not None and prev_avg:
                fare_change = round((cur_avg - prev_avg) / prev_avg * 100.0, 2)

            channels.append(
                {
                    "channel_key": portal,
                    "display_name": label,
                    "source_type": stype,
                    "health": health,
                    "quotes_today": cur_cnt,
                    "quotes_30d": cnt30,
                    "avg_fare_today_inr": round(cur_avg, 2) if cur_avg else None,
                    "avg_fare_previous_inr": round(prev_avg, 2) if prev_avg else None,
                    "fare_change_pct": fare_change,
                }
            )

        # Pipeline cleanliness
        if latest_date:
            clean_row = (
                db.query(
                    func.count().label("c"),
                    func.sum(func.cast(CleanedQuote.outlier_flag == 0, type_=func.count())),
                    func.sum(func.cast(CleanedQuote.outlier_flag == 1, type_=func.count())),
                )
                .filter(CleanedQuote.booking_date == latest_date)
                .first()
            )
            if clean_row:
                summary["validated_quotes_today"] = int(clean_row[1] or 0)
                summary["outliers_today"] = int(clean_row[2] or 0)

        summary["channels_total"] = len(channels)
        summary["channels_healthy"] = sum(1 for c in channels if c["health"] == "SUCCESS")
        summary["quotes_today_total"] = sum(c["quotes_today"] or 0 for c in channels)
        if today_stats_all:
            summary["average_fare_today_inr"] = round(sum(today_stats_all) / len(today_stats_all), 2)
        if prev_stats_all:
            summary["average_fare_previous_inr"] = round(sum(prev_stats_all) / len(prev_stats_all), 2)
        if summary["average_fare_today_inr"] and summary["average_fare_previous_inr"]:
            summary["national_fare_change_pct"] = round(
                (summary["average_fare_today_inr"] - summary["average_fare_previous_inr"])
                / summary["average_fare_previous_inr"]
                * 100.0,
                2,
            )

        return {"summary": summary, "channels": channels, "data_tag": "REAL_COMPUTED"}

    finally:
        db.close()


def get_route_movements(lookback_days: int = 7) -> dict[str, Any]:
    """Route-level composite movement between the latest two calculation dates."""
    db = SessionLocal()
    try:
        dates = [
            str(r[0])
            for r in db.query(RouteIndex.calculation_date).distinct().order_by(RouteIndex.calculation_date.desc()).all()
        ]
        if len(dates) < 2:
            return {
                "as_of_date": dates[0] if dates else None,
                "comparison_date": None,
                "routes": [],
                "national": None,
                "data_tag": "REAL_COMPUTED",
            }

        latest = dates[0]
        target = latest
        for d in dates[1:]:
            if (datetime.date.fromisoformat(latest) - datetime.date.fromisoformat(d)).days >= max(1, lookback_days):
                target = d
                break
        if target == latest:
            target = dates[-1]

        def route_snapshot(date_str: str) -> dict[str, dict[str, Any]]:
            rows = db.query(RouteIndex).filter(RouteIndex.calculation_date == date_str).all()
            snap: dict[str, dict[str, Any]] = {}
            for r in rows:
                w = int(r.advance_window.replace("T+", "").replace("T", "") or 7)
                wt = WINDOW_WEIGHTS.get(w, 0.2)
                e = snap.setdefault(r.route_code, {"rel_wsum": 0.0, "fare_wsum": 0.0, "wsum": 0.0, "cnt": 0})
                e["rel_wsum"] += float(r.composite_route_relative or 0.0)
                e["fare_wsum"] += wt * float(r.jevons_mean_fare or 0.0)
                e["wsum"] += wt
                e["cnt"] += 1
            out = {}
            for rc, e in snap.items():
                out[rc] = {
                    "composite_relative": e["rel_wsum"] / e["cnt"] if e["cnt"] else 1.0,
                    "composite_fare_inr": e["fare_wsum"] / e["wsum"] if e["wsum"] else None,
                }
            return out

        cur = route_snapshot(latest)
        prev = route_snapshot(target)

        routes_out = []
        for rc, (origin, dest, weight) in DGCA_ROUTES.items():
            if rc not in cur:
                continue
            c, p = cur[rc], prev.get(rc)
            if p is None or not p["composite_fare_inr"] or not c["composite_fare_inr"]:
                continue
            change_pct = round((c["composite_fare_inr"] - p["composite_fare_inr"]) / p["composite_fare_inr"] * 100.0, 2)
            routes_out.append(
                {
                    "route_code": rc,
                    "origin_city": origin,
                    "destination_city": dest,
                    "dgca_weight_pct": round(weight * 100.0, 2),
                    "current_fare_inr": round(c["composite_fare_inr"], 2),
                    "previous_fare_inr": round(p["composite_fare_inr"], 2),
                    "current_composite_relative": round(c["composite_relative"], 4),
                    "change_pct": change_pct,
                }
            )

        routes_out.sort(key=lambda x: x["change_pct"], reverse=True)

        wsum_nat = sum(x["dgca_weight_pct"] for x in routes_out) or 1.0
        nat_cur = sum(x["current_fare_inr"] * x["dgca_weight_pct"] for x in routes_out) / wsum_nat
        nat_prev = sum(x["previous_fare_inr"] * x["dgca_weight_pct"] for x in routes_out) / wsum_nat
        national = {
            "current_fare_inr": round(nat_cur, 2),
            "previous_fare_inr": round(nat_prev, 2),
            "change_pct": round((nat_cur - nat_prev) / nat_prev * 100.0, 2) if nat_prev else None,
            "routes_covered": len(routes_out),
        }

        return {
            "as_of_date": latest,
            "comparison_date": target,
            "lookback_days_requested": lookback_days,
            "routes": routes_out,
            "national": national,
            "data_tag": "REAL_COMPUTED",
        }

    finally:
        db.close()
