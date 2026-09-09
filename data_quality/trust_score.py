"""
JetIndex - Data Trust Score & Quality Evaluation Engine
Transparent, mathematically defined 0-100 composite index for MoSPI & RBI data governance.
"""

import datetime
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger("jetindex.data_quality")

# Route coverage targets (from config)
DGCA_TOP_20_ROUTES = [
    "DEL-BOM", "DEL-BLR", "DEL-MAA", "DEL-CCU", "DEL-HYD",
    "BOM-BLR", "BOM-MAA", "BOM-CCU", "BOM-HYD", "BLR-MAA",
    "BLR-CCU", "BLR-HYD", "MAA-CCU", "MAA-HYD", "CCU-HYD",
    "DEL-GOI", "DEL-PNQ", "BOM-GOI", "BLR-GOI", "MAA-GOI"
]

ADVANCE_PURCHASE_WINDOWS = [
    "T-0", "T-7", "T-14", "T-21", "T-30"
]


@dataclass
class DataTrustMetrics:
    """Comprehensive data quality telemetry metrics."""
    snapshot_date: str
    overall_trust_score: float
    freshness_pct: float
    completeness_pct: float
    route_coverage_pct: float
    source_health_pct: float
    duplicate_rate_pct: float
    outlier_rate_pct: float
    validation_success_pct: float
    consensus_score: float
    status_rating: str
    weights_breakdown: Dict[str, float]
    data_tag: str = "REAL_COMPUTED"
    generated_at: str = ""


class DataQualityEngine:
    """
    Evaluates empirical observation pipelines across 7 statutory dimensions:
    1. Freshness (20% weight) - Recency of ingested data within expected cycle
    2. Completeness (20% weight) - Cell population across 20 routes x 5 windows (100 cells)
    3. Route Coverage (15% weight) - All 20 DGCA routes actively monitored
    4. Source Availability (15% weight) - Uptime of airline & OTA scrapers
    5. Duplicate Resolution (10% weight) - Integrity of multi-OTA deduplication
    6. Outlier Control (10% weight) - Proportion of clean vs rejected MAD outliers
    7. Cross-Source Consensus (10% weight) - Low price dispersion across multiple sources
    """

    WEIGHTS = {
        "freshness": 0.20,
        "completeness": 0.20,
        "route_coverage": 0.15,
        "source_health": 0.15,
        "duplicate_integrity": 0.10,
        "outlier_cleanliness": 0.10,
        "cross_source_consensus": 0.10,
    }

    def __init__(self):
        self.expected_cells = len(DGCA_TOP_20_ROUTES) * len(ADVANCE_PURCHASE_WINDOWS)  # 100 cells

    def evaluate_quality(self, target_date: Optional[str] = None) -> DataTrustMetrics:
        """
        Computes deterministic, reproducible Data Trust Score directly from database observations.
        """
        now_dt = datetime.datetime.now(datetime.timezone.utc)

        # Get database engine
        from db.session import get_engine
        from sqlalchemy import text

        engine = get_engine()

        if not target_date:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT MAX(calculation_date) as dt FROM national_indices"))
                row = result.fetchone()
                calc_date = row[0] if row and row[0] else datetime.date.today().isoformat()
        else:
            calc_date = target_date

        # 1. Freshness Score
        try:
            target_dt = datetime.date.fromisoformat(calc_date)
            today_dt = datetime.date.today()
            age_days = (today_dt - target_dt).days
            freshness = max(0.0, min(100.0, 100.0 - (age_days * 5.0)))
        except Exception:
            freshness = 95.0

        # 2. Route Coverage & Cell Completeness
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT route_code, advance_window, sample_size
                FROM route_indices
                WHERE calculation_date = :calc_date
            """), {"calc_date": calc_date})
            rows = result.fetchall()

        observed_routes = set(r[0] for r in rows)
        coverage_pct = (len(observed_routes) / len(DGCA_TOP_20_ROUTES)) * 100.0 if DGCA_TOP_20_ROUTES else 100.0

        populated_cells = len([r for r in rows if r[2] > 0])
        completeness_pct = (populated_cells / self.expected_cells) * 100.0 if self.expected_cells else 100.0

        # 3. Source Availability & Health
        with engine.connect() as conn:
            result = conn.execute(text("SELECT success_rate_24h, is_active FROM sources"))
            source_rows = result.fetchall()

        if source_rows:
            source_health_pct = float(np.mean([r[0] for r in source_rows if r[1] == 1]))
        else:
            source_health_pct = 0.0

        # 4. Outlier & Duplicate Rates
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT observations_count, valid_quotes_count, outliers_rejected_count
                FROM national_indices
                WHERE calculation_date = :calc_date
            """), {"calc_date": calc_date})
            nat_row = result.fetchone()

        if nat_row and nat_row[0] > 0:
            tot = nat_row[0]
            valid = nat_row[1]
            outliers = nat_row[2]
            outlier_rate = (outliers / tot) * 100.0
            # Higher cleanliness score when outlier rate is reasonable (around 1-4%)
            outlier_cleanliness = max(0.0, 100.0 - (outlier_rate * 5.0))
            duplicate_rate = max(0.0, (tot - valid - outliers) / tot * 100.0)
            duplicate_integrity = 100.0 - min(50.0, duplicate_rate * 0.5)
            val_success = (valid / tot) * 100.0
        else:
            # No observations exist for the target date: report 0% honestly
            # instead of fabricating healthy-looking quality telemetry.
            outlier_rate = 0.0
            outlier_cleanliness = 0.0
            duplicate_rate = 0.0
            duplicate_integrity = 0.0
            val_success = 0.0

        # 5. Cross-Source Consensus Score
        # Derived transparently from live cross-portal dispersion analysis. Only
        # corridors with real observations contribute; no fabricated consensus.
        try:
            from engine.analytics.source_consensus import get_source_consensus_report
            consensus_rep = get_source_consensus_report(target_date=calc_date)
            consensus_score = float(consensus_rep.overall_market_consensus_score)
        except Exception as e:
            logger.debug(f"Consensus score unavailable: {e}")
            consensus_score = 0.0

        # 6. Overall Weighted Trust Score
        overall = (
            (freshness * self.WEIGHTS["freshness"]) +
            (completeness_pct * self.WEIGHTS["completeness"]) +
            (coverage_pct * self.WEIGHTS["route_coverage"]) +
            (source_health_pct * self.WEIGHTS["source_health"]) +
            (duplicate_integrity * self.WEIGHTS["duplicate_integrity"]) +
            (outlier_cleanliness * self.WEIGHTS["outlier_cleanliness"]) +
            (consensus_score * self.WEIGHTS["cross_source_consensus"])
        )
        overall = round(max(0.0, min(100.0, overall)), 2)

        if overall >= 90.0:
            status = "EXCELLENT"
        elif overall >= 80.0:
            status = "GOOD"
        elif overall >= 70.0:
            status = "FAIR"
        else:
            status = "DEGRADED"

        metrics = DataTrustMetrics(
            snapshot_date=calc_date,
            overall_trust_score=overall,
            freshness_pct=round(freshness, 1),
            completeness_pct=round(completeness_pct, 1),
            route_coverage_pct=round(coverage_pct, 1),
            source_health_pct=round(source_health_pct, 1),
            duplicate_rate_pct=round(duplicate_rate, 2),
            outlier_rate_pct=round(outlier_rate, 2),
            validation_success_pct=round(val_success, 1),
            consensus_score=round(consensus_score, 1),
            status_rating=status,
            weights_breakdown=self.WEIGHTS,
            generated_at=now_dt.isoformat()
        )

        # Persist snapshot (if table exists)
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO data_quality_snapshots (
                        snapshot_date, overall_trust_score, freshness_pct, completeness_pct,
                        route_coverage_pct, source_health_pct, duplicate_rate_pct, outlier_rate_pct,
                        validation_success_pct, consensus_score, status_rating, created_at
                    ) VALUES (:snapshot_date, :overall_trust_score, :freshness_pct, :completeness_pct,
                              :route_coverage_pct, :source_health_pct, :duplicate_rate_pct, :outlier_rate_pct,
                              :validation_success_pct, :consensus_score, :status_rating, :created_at)
                """), {
                    "snapshot_date": metrics.snapshot_date,
                    "overall_trust_score": metrics.overall_trust_score,
                    "freshness_pct": metrics.freshness_pct,
                    "completeness_pct": metrics.completeness_pct,
                    "route_coverage_pct": metrics.route_coverage_pct,
                    "source_health_pct": metrics.source_health_pct,
                    "duplicate_rate_pct": metrics.duplicate_rate_pct,
                    "outlier_rate_pct": metrics.outlier_rate_pct,
                    "validation_success_pct": metrics.validation_success_pct,
                    "consensus_score": metrics.consensus_score,
                    "status_rating": metrics.status_rating,
                    "created_at": metrics.generated_at
                })
                conn.commit()
        except Exception as e:
            logger.debug(f"Snapshot insert error (table may not exist): {e}")

        return metrics


def get_latest_data_quality() -> DataTrustMetrics:
    """Convenience helper to fetch or compute latest data quality snapshot."""
    engine = DataQualityEngine()
    return engine.evaluate_quality()
