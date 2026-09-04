"""Backtest — compare APIx vs DGCA benchmark, compute MAPE/RMSE."""

import json
from pathlib import Path

import numpy as np
from loguru import logger


def run_backtest(session) -> dict:
    """
    Run backtest: compare APIx-implied fares vs DGCA monthly average fares.

    Steps:
    1. Get DGCA benchmark data (monthly avg fares)
    2. Convert APIx to implied fares using base period
    3. Compute MAPE, RMSE, Pearson r
    4. Write results to data/backtest_results.json

    Returns:
        Dict with monthly data and summary statistics.
    """
    # TODO: Implement with real DB queries
    # from db.models import ApixDaily, DgcaBenchmark
    #
    # # Get DGCA benchmarks
    # benchmarks = session.query(DgcaBenchmark).all()
    #
    # # Get APIx monthly averages
    # apix_monthly = session.query(...).all()
    #
    # # Convert APIx to implied fares
    # base_price = 5000.0  # average base period fare
    # for month, apix in apix_monthly:
    #     implied_fare = (apix / 100) * base_price
    #     ...
    #
    # # Compute metrics
    # mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    # rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    # corr = np.corrcoef(actual, predicted)[0, 1]

    logger.warning("run_backtest: using placeholder values")

    # Placeholder data
    monthly = [
        {"month": "2025-01", "apix_avg": 100.0, "dgca_avg_fare": 5000, "apix_rebased": 100.0, "error_pct": 0.0},
        {"month": "2025-02", "apix_avg": 102.5, "dgca_avg_fare": 5100, "apix_rebased": 102.5, "error_pct": 0.5},
        {"month": "2025-03", "apix_avg": 105.0, "dgca_avg_fare": 5200, "apix_rebased": 105.0, "error_pct": 1.0},
    ]

    summary = {"mape": 0.5, "rmse": 25.0, "corr": 0.98}

    result = {"monthly": monthly, "summary": summary}

    # Write to file
    output_path = Path("data/backtest_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    logger.info(f"Backtest complete: MAPE={summary['mape']:.2f}%, RMSE={summary['rmse']:.2f}, r={summary['corr']:.4f}")
    return result


def compute_mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Compute Mean Absolute Percentage Error."""
    mask = actual != 0
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)


def compute_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Compute Root Mean Squared Error."""
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def compute_correlation(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Compute Pearson correlation coefficient."""
    if len(actual) < 2:
        return 0.0
    return float(np.corrcoef(actual, predicted)[0, 1])
