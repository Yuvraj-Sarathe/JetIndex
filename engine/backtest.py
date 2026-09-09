"""Backtest — compare APIx vs DGCA benchmark, compute MAPE/RMSE.

Also compares APIx against real MoSPI CPI transport data.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from loguru import logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

_MOSPI_CSV = Path("data/reference/mospi_esankhyiki_cpi_actual.csv")


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


def load_mospi_cpi_data() -> list[dict]:
    """Load MoSPI eSankhyiki CPI data from CSV."""
    if not _MOSPI_CSV.exists():
        logger.warning("MoSPI CPI CSV not found at {}", _MOSPI_CSV)
        return []
    with open(_MOSPI_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def compare_with_mospi_cpi(session: Session | None = None) -> dict:
    """Compare APIx index movements against real MoSPI Transport CPI data.

    Uses YoY inflation rates from MoSPI to validate that APIx captures
    the same inflationary trends as official government statistics.
    """
    from db import queries as db_queries
    from db.session import SessionLocal

    owns_session = False
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        cpi_data = load_mospi_cpi_data()
        if not cpi_data:
            return {"status": "NO_DATA", "message": "MoSPI CPI CSV not found"}

        # Get APIx monthly data
        apix_monthly = db_queries.get_apix_monthly(session)
        apix_map = {}
        for row in apix_monthly:
            if "month_start" in row and row["month_start"]:
                ms = row["month_start"]
                m_str = ms.strftime("%Y-%m") if hasattr(ms, "strftime") else str(ms)[:7]
                apix_map[m_str] = float(row.get("apix") or 0.0)

        # Parse CPI data
        cpi_by_month = {}
        for row in cpi_data:
            month_str = f"{row['Year']}-{int(row['Month']):02d}"
            cpi_by_month[month_str] = {
                "transport_combined": float(row["Transport_Combined"]),
                "headline_cpi": float(row["Headline_CPI_Combined"]),
                "airfare_subgroup": float(row["Airfare_SubGroup_Index"]),
                "yoy_transport_pct": float(row["YoY_Inflation_Transport_Pct"]),
                "yoy_headline_pct": float(row["YoY_Inflation_Headline_Pct"]),
            }

        # Compare YoY inflation rates
        common_months = sorted(set(apix_map.keys()) & set(cpi_by_month.keys()))

        comparisons = []
        for month in common_months:
            apix_val = apix_map[month]
            cpi_info = cpi_by_month[month]

            # Compute APIx YoY change if we have 12-month lookback
            prev_year = f"{int(month[:4]) - 1}-{month[5:]}"
            if prev_year in apix_map:
                apix_yoy_pct = ((apix_val - apix_map[prev_year]) / apix_map[prev_year]) * 100.0
            else:
                apix_yoy_pct = None

            comparisons.append({
                "month": month,
                "apix_index": round(apix_val, 2),
                "mospi_transport_cpi": cpi_info["transport_combined"],
                "mospi_airfare_subgroup": cpi_info["airfare_subgroup"],
                "mospi_yoy_transport_pct": cpi_info["yoy_transport_pct"],
                "apix_yoy_pct": round(apix_yoy_pct, 2) if apix_yoy_pct is not None else None,
            })

        # Compute correlation between APIx and transport CPI
        if len(comparisons) > 2:
            apix_vals = np.array([c["apix_index"] for c in comparisons])
            transport_vals = np.array([c["mospi_transport_cpi"] for c in comparisons])
            correlation = compute_correlation(apix_vals, transport_vals)
        else:
            correlation = 0.0

        return {
            "status": "SUCCESS",
            "correlation_with_transport_cpi": round(correlation, 4),
            "months_compared": len(comparisons),
            "data_tag": "REAL_MOSPI_DATA",
            "comparisons": comparisons,
        }
    finally:
        if owns_session:
            session.close()
