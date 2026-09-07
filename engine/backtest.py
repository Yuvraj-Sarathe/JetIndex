"""Backtest — compare APIx vs DGCA benchmark, compute MAPE/RMSE."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from loguru import logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def run_backtest(session: Session | None = None) -> dict:
    """
    Run backtest: compare APIx-implied fares vs DGCA monthly average fares.

    Steps:
    1. Get DGCA benchmark data (monthly avg fares)
    2. Get APIx monthly rollups
    3. Convert APIx to implied fares using base period
    4. Compute MAPE, RMSE, Pearson r
    5. Write results to data/backtest_results.json

    Returns:
        Dict with monthly data and summary statistics.
    """
    from db import queries as db_queries
    from db.session import SessionLocal

    owns_session = False
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        benchmarks = db_queries.get_dgca_benchmarks(session)
        apix_monthly = db_queries.get_apix_monthly(session)

        bench_by_month: dict[str, list[float]] = defaultdict(list)
        for b in benchmarks:
            if b.get("month") and b.get("avg_fare"):
                bench_by_month[b["month"]].append(float(b["avg_fare"]))

        bench_map = {m: sum(fares) / len(fares) for m, fares in bench_by_month.items() if fares}
        apix_map = {}
        for row in apix_monthly:
            if "month_start" in row and row["month_start"]:
                ms = row["month_start"]
                m_str = ms.strftime("%Y-%m") if hasattr(ms, "strftime") else str(ms)[:7]
                apix_map[m_str] = float(row.get("apix") or 0.0)

        common_months = sorted(set(bench_map.keys()) & set(apix_map.keys()))

        monthly = []
        if common_months:
            # Base price reference from the first common month or benchmark average
            base_bench = bench_map[common_months[0]] if bench_map[common_months[0]] > 0 else 5000.0

            actual_fares = []
            implied_fares = []

            for month in common_months:
                apix_val = apix_map[month]
                dgca_val = bench_map[month]
                implied = (apix_val / 100.0) * base_bench
                error_pct = abs(implied - dgca_val) / dgca_val * 100.0 if dgca_val > 0 else 0.0

                actual_fares.append(dgca_val)
                implied_fares.append(implied)

                monthly.append(
                    {
                        "month": month,
                        "apix_avg": round(apix_val, 4),
                        "dgca_avg_fare": round(dgca_val, 2),
                        "apix_rebased": round(apix_val, 4),
                        "implied_fare": round(implied, 2),
                        "error_pct": round(error_pct, 2),
                    }
                )

            actual_arr = np.array(actual_fares, dtype=float)
            implied_arr = np.array(implied_fares, dtype=float)

            mape = compute_mape(actual_arr, implied_arr)
            rmse = compute_rmse(actual_arr, implied_arr)
            corr = compute_correlation(actual_arr, implied_arr)

            summary = {
                "mape": round(mape, 2),
                "rmse": round(rmse, 2),
                "corr": round(corr, 4),
            }
        else:
            logger.warning("run_backtest: no overlapping months found between apix_daily and dgca_benchmark")
            summary = {"mape": 0.0, "rmse": 0.0, "corr": 0.0}

        result = {"monthly": monthly, "summary": summary}

        output_path = Path("data/backtest_results.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)

        logger.info(
            "Backtest complete: MAPE={:.2f}%, RMSE={:.2f}, r={:.4f}",
            summary["mape"],
            summary["rmse"],
            summary["corr"],
        )
        return result
    finally:
        if owns_session:
            session.close()


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
