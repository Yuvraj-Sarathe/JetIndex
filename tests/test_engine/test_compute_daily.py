"""Tests for engine compute_daily, weights, aggregator, and backtest."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from engine.aggregator import monthly_rollup, weekly_rollup
from engine.backtest import run_backtest
from engine.elasticity import compute_elasticity, compute_elasticity_coefficient
from engine.index_calculator import compute_daily
from engine.weights import get_base_period_prices


def test_compute_daily_with_mock_db():
    """Verify compute_daily properly aggregates fares, calls laspeyres, and upserts."""
    mock_session = MagicMock()

    mock_fare_rows = [
        {"route_id": 1, "lead_time": 1, "median_fare": 5000.0, "median_base_fare": 4000.0, "n_quotes": 10},
        {"route_id": 1, "lead_time": 7, "median_fare": 5200.0, "median_base_fare": 4200.0, "n_quotes": 12},
        {"route_id": 2, "lead_time": 1, "median_fare": 6000.0, "median_base_fare": 5000.0, "n_quotes": 8},
        {"route_id": 2, "lead_time": 7, "median_fare": 6200.0, "median_base_fare": 5200.0, "n_quotes": 10},
    ]
    mock_weights = {1: 0.6, 2: 0.4}
    mock_base_prices = {1: 5100.0, 2: 6100.0}

    with (
        patch("db.queries.get_median_fares_by_route", return_value=mock_fare_rows) as mock_get_fares,
        patch("db.queries.get_weights", return_value=mock_weights) as mock_get_weights,
        patch("db.queries.get_base_period_prices", return_value=mock_base_prices) as mock_get_base,
        patch("db.queries.upsert_apix_daily") as mock_upsert,
    ):
        result = compute_daily("2026-10-13", session=mock_session)

        mock_get_fares.assert_called_once_with(
            session=mock_session,
            scrape_date=date(2026, 10, 13),
            lead_times=(1, 7, 15, 30, 45),
        )
        mock_get_weights.assert_called_once_with(mock_session)
        mock_get_base.assert_called_once_with(mock_session)
        mock_upsert.assert_called_once()

        assert result["date"] == "2026-10-13"
        assert result["n_quotes"] == 40
        assert result["n_routes"] == 2
        assert result["method"] == "laspeyres"
        assert result["apix"] == pytest.approx(100.0, abs=0.1)
        assert "apix_base_only" in result


def test_compute_daily_empty_data_fallback():
    """Verify compute_daily handles empty query results gracefully."""
    mock_session = MagicMock()

    with (
        patch("db.queries.get_median_fares_by_route", return_value=[]),
        patch("db.queries.get_weights", return_value={}),
        patch("db.queries.get_base_period_prices", return_value={}),
        patch("db.queries.upsert_apix_daily") as mock_upsert,
    ):
        result = compute_daily(date(2026, 10, 13), session=mock_session)

        assert result["apix"] == 100.0
        assert result["apix_base_only"] == 100.0
        assert result["n_quotes"] == 0
        assert result["n_routes"] == 0
        mock_upsert.assert_called_once()


def test_weights_get_base_period_prices_delegation():
    """Verify engine/weights.get_base_period_prices delegates to db.queries."""
    mock_session = MagicMock()
    mock_return = {1: 4500.0, 2: 5500.0}

    with patch("db.queries.get_base_period_prices", return_value=mock_return) as mock_query:
        prices = get_base_period_prices(session=mock_session, n_days=14)
        mock_query.assert_called_once_with(mock_session, n_days=14)
        assert prices == mock_return


def test_aggregator_rollups_delegation():
    """Verify aggregator rollups delegate to db.queries functions."""
    mock_session = MagicMock()
    mock_weekly = [{"week_start": date(2026, 10, 12), "apix": 102.5, "n_quotes": 100}]
    mock_monthly = [{"month_start": date(2026, 10, 1), "apix": 101.8, "n_quotes": 450}]

    with (
        patch("db.queries.get_apix_weekly", return_value=mock_weekly) as mock_get_weekly,
        patch("db.queries.get_apix_monthly", return_value=mock_monthly) as mock_get_monthly,
    ):
        w_res = weekly_rollup(session=mock_session, start_date=date(2026, 10, 1), end_date=date(2026, 10, 31))
        mock_get_weekly.assert_called_once_with(
            mock_session,
            from_date=date(2026, 10, 1),
            to_date=date(2026, 10, 31),
        )
        assert len(w_res) == 1
        assert w_res[0]["apix_avg"] == 102.5

        m_res = monthly_rollup(session=mock_session)
        mock_get_monthly.assert_called_once_with(mock_session, from_date=None, to_date=None)
        assert len(m_res) == 1
        assert m_res[0]["month"] == "2026-10"
        assert m_res[0]["apix_avg"] == 101.8


def test_backtest_run_with_data(tmp_path):
    """Verify run_backtest computes metrics when overlapping data is available."""
    mock_session = MagicMock()
    mock_benchmarks = [
        {"month": "2026-07", "avg_fare": 5000.0},
        {"month": "2026-08", "avg_fare": 5200.0},
    ]
    mock_apix_monthly = [
        {"month_start": date(2026, 7, 1), "apix": 100.0},
        {"month_start": date(2026, 8, 1), "apix": 104.0},
    ]

    with (
        patch("db.queries.get_dgca_benchmarks", return_value=mock_benchmarks),
        patch("db.queries.get_apix_monthly", return_value=mock_apix_monthly),
        patch("engine.backtest.Path") as mock_path_cls,
    ):
        mock_out_file = tmp_path / "backtest_results.json"
        mock_path_cls.return_value = mock_out_file

        result = run_backtest(session=mock_session)

        assert len(result["monthly"]) == 2
        assert "summary" in result
        assert "mape" in result["summary"]
        assert "rmse" in result["summary"]
        assert "corr" in result["summary"]
        assert mock_out_file.exists()


def test_elasticity_compute_with_route_id_returns_data():
    """Verify compute_elasticity with route_id queries DB and formats output."""
    mock_session = MagicMock()
    mock_rows = [
        {"lead_time": 1, "median_fare": 6500.0, "median_base_fare": 5500.0, "n_quotes": 15},
        {"lead_time": 7, "median_fare": 5800.0, "median_base_fare": 4800.0, "n_quotes": 20},
        {"lead_time": 15, "median_fare": 5200.0, "median_base_fare": 4200.0, "n_quotes": 18},
    ]

    with patch("db.queries.get_elasticity_data", return_value=mock_rows) as mock_get_elasticity:
        results = compute_elasticity(session=mock_session, route_id=1, route_date=date(2026, 10, 13))

        mock_get_elasticity.assert_called_once_with(mock_session, route_id=1, route_date=date(2026, 10, 13))
        assert len(results) == 3
        assert results[0] == {
            "route_id": 1,
            "lead_time": 1,
            "avg_total_fare": 6500.0,
            "avg_base_fare": 5500.0,
            "n": 15,
        }


def test_elasticity_compute_without_route_id_aggregates_active_routes():
    """Verify compute_elasticity without route_id queries active routes and concatenates results."""
    mock_session = MagicMock()
    mock_route1 = MagicMock()
    mock_route1.id = 10
    mock_route2 = MagicMock()
    mock_route2.id = 20

    mock_rows_r1 = [{"lead_time": 1, "median_fare": 5000.0, "median_base_fare": 4000.0, "n_quotes": 5}]
    mock_rows_r2 = [{"lead_time": 7, "median_fare": 4500.0, "median_base_fare": 3500.0, "n_quotes": 8}]

    with (
        patch("db.queries.get_active_routes", return_value=[mock_route1, mock_route2]) as mock_get_routes,
        patch("db.queries.get_elasticity_data", side_effect=[mock_rows_r1, mock_rows_r2]) as mock_get_elasticity,
    ):
        results = compute_elasticity(session=mock_session)

        mock_get_routes.assert_called_once_with(mock_session)
        assert mock_get_elasticity.call_count == 2
        assert len(results) == 2
        assert results[0]["route_id"] == 10
        assert results[1]["route_id"] == 20


def test_elasticity_compute_coefficient_returns_valid_slope():
    """Verify compute_elasticity_coefficient computes correct negative elasticity slope."""
    lead_times = [1, 7, 15, 30, 45]
    fares = [7000.0, 5800.0, 5000.0, 4400.0, 4000.0]

    coeff = compute_elasticity_coefficient(fares, lead_times)
    assert coeff is not None
    assert coeff < 0.0  # fares decrease as lead time increases


def test_elasticity_compute_coefficient_insufficient_data_returns_none():
    """Verify compute_elasticity_coefficient handles empty/short inputs gracefully."""
    assert compute_elasticity_coefficient([], []) is None
    assert compute_elasticity_coefficient([5000.0], [1]) is None
    assert compute_elasticity_coefficient([0.0, 0.0], [1, 7]) is None
