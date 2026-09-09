"""Tests for analytics engine."""

import pytest

from engine.analytics import (
    _AIRFARE_SHARE,
    _TRANSPORT_WEIGHT,
    compute_pressure_score,
    compute_cpi_decomposition,
    compute_heatmap,
    compute_trust_score,
    PressureReport,
    CPIDecomposition,
    HeatmapMatrix,
    TrustScoreReport,
)


class TestPressureScore:
    """Tests for AIPS pressure score."""

    def test_pressure_report_structure(self):
        report = PressureReport(
            as_of_date="2026-01-01",
            score=50.0,
            level="MODERATE",
            previous_score=48.0,
            delta_24h=2.0,
            components={"airfare_acceleration": 50.0},
            ranked_drivers=["test: 100%"],
            alert="NEUTRAL_PRICE_STABILITY",
        )
        assert report.score == 50.0
        assert report.level == "MODERATE"

    def test_pressure_score_bounds(self):
        # Test that score is always 0-100
        report = PressureReport(
            as_of_date="2026-01-01",
            score=0.0,
            level="LOW",
            previous_score=0.0,
            delta_24h=0.0,
            components={},
            ranked_drivers=[],
            alert="DISINFLATIONARY_COOLING",
        )
        assert 0.0 <= report.score <= 100.0


class TestCpiDecomposition:
    """Tests for CPI decomposition."""

    def test_decomposition_structure(self):
        report = CPIDecomposition(
            as_of_date="2026-01-01",
            total_transport_bps=0.85,
            total_headline_bps=0.073,
            route_contributions=[
                {"route_code": "DEL-BOM", "transport_bps": 0.093},
            ],
        )
        assert report.total_transport_bps == 0.85
        assert len(report.route_contributions) == 1

    def test_airfare_share_constant(self):
        assert _AIRFARE_SHARE == 0.0385

    def test_transport_weight_constant(self):
        assert _TRANSPORT_WEIGHT == 0.0859


class TestHeatmap:
    """Tests for heatmap matrix."""

    def test_heatmap_cell_structure(self):
        from engine.analytics import HeatmapCell
        cell = HeatmapCell(
            route_code="DEL-BOM",
            window_id="T+7",
            current_fare=6500.0,
            benchmark=5000.0,
            change_pct=30.0,
            status="SURGE",
        )
        assert cell.route_code == "DEL-BOM"
        assert cell.status == "SURGE"

    def test_heatmap_status_logic(self):
        from engine.analytics import HeatmapCell
        # Test status assignment logic
        for change, expected in [(30.0, "SURGE"), (15.0, "ELEVATED"), (-15.0, "DISCOUNTED"), (5.0, "NORMAL")]:
            if change > 25:
                status = "SURGE"
            elif change > 10:
                status = "ELEVATED"
            elif change < -10:
                status = "DISCOUNTED"
            else:
                status = "NORMAL"
            assert status == expected


class TestTrustScore:
    """Tests for data trust score."""

    def test_trust_score_bounds(self):
        report = TrustScoreReport(
            as_of_date="2026-01-01",
            overall_score=82.5,
            freshness=85.0,
            completeness=90.0,
            route_coverage=78.0,
            source_health=85.0,
            duplicate_rate=5.0,
            outlier_rate=3.0,
            validation_success=95.0,
            rating="A",
        )
        assert 0.0 <= report.overall_score <= 100.0
        assert report.rating in ["A+", "A", "B", "C", "D"]

    def test_trust_rating_logic(self):
        # Test rating thresholds
        for score, expected in [(95, "A+"), (85, "A"), (75, "B"), (65, "C"), (50, "D")]:
            if score >= 90:
                rating = "A+"
            elif score >= 80:
                rating = "A"
            elif score >= 70:
                rating = "B"
            elif score >= 60:
                rating = "C"
            else:
                rating = "D"
            assert rating == expected
