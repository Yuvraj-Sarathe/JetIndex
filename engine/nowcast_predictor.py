"""
JetIndex - Multi-Horizon Inflation Nowcasting & Policy Forecasting Engine
Generates 7-day, 14-day, and 30-day forward CPI nowcast trajectories with 95% confidence intervals
for the Reserve Bank of India (RBI) Monetary Policy Committee and MoSPI.
"""

import datetime
import logging
import math
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .model_trainer import (
    CPI_WEIGHTS,
    MODEL_ARTIFACT_PATH,
    EconometricNowcastEnsemble,
    FeatureEngineer,
    train_nowcast_model,
)

logger = logging.getLogger("jetindex.nowcast")


@dataclass
class ForecastStep:
    """A single daily forward forecast step with uncertainty bands and CPI transmission."""

    forecast_date: str
    horizon_days: int
    predicted_laspeyres_index: float
    confidence_interval_95_lower: float
    confidence_interval_95_upper: float
    projected_daily_change_pct: float
    projected_transport_impact_bps: float
    projected_headline_cpi_impact_bps: float


@dataclass
class NowcastReport:
    """Complete multi-horizon macroeconomic nowcast report."""

    as_of_date: str
    current_index: float
    model_version: str
    forecast_horizon_days: int
    summary_mean_forecast: float
    net_projected_transport_bps: float
    net_projected_headline_cpi_bps: float
    monetary_policy_alert: str
    forecast_steps: list[ForecastStep]
    feature_importances: dict[str, float]
    generated_at: str


class InflationNowcastPredictor:
    """
    Executes multi-step autoregressive forward simulation using trained econometric ensemble.
    """

    def __init__(self, model_path: str = MODEL_ARTIFACT_PATH):
        self.model_path = model_path
        self._model: EconometricNowcastEnsemble | None = None

    def get_model(self) -> EconometricNowcastEnsemble:
        """Retrieves active model or triggers initial training."""
        if self._model is not None:
            return self._model

        if os.path.exists(self.model_path):
            try:
                self._model = EconometricNowcastEnsemble.load(self.model_path)
                return self._model
            except Exception as e:
                logger.warning(f"Failed to load cached model {e}, retraining...")

        model, _ = train_nowcast_model()
        self._model = model
        return self._model

    def generate_nowcast(self, horizon_days: int = 14) -> NowcastReport:
        """
        Generates autoregressive forward nowcasts up to horizon_days (e.g. 7, 14, 30 days).
        """
        model = self.get_model()

        # Load historical data from database
        from db.session import get_engine

        engine = get_engine()

        with engine.connect() as conn:
            df_raw = pd.read_sql(
                """
                SELECT calculation_date, laspeyres_index, fisher_index, paasche_index,
                       spot_t1_index, daily_pct_change, bps_transport_impact,
                       bps_headline_cpi_impact, observations_count, valid_quotes_count,
                       outliers_rejected_count
                FROM national_indices
                ORDER BY calculation_date ASC
            """,
                conn,
            )

        if len(df_raw) < 10:
            from engine.backtest import DGCABacktestEngine

            DGCABacktestEngine().run_backtest(num_days=35)
            with engine.connect() as conn:
                df_raw = pd.read_sql(
                    """
                    SELECT calculation_date, laspeyres_index, fisher_index, paasche_index,
                           spot_t1_index, daily_pct_change, bps_transport_impact,
                           bps_headline_cpi_impact, observations_count, valid_quotes_count,
                           outliers_rejected_count
                    FROM national_indices
                    ORDER BY calculation_date ASC
                """,
                    conn,
                )

        # Working copy for iterative autoregressive rollout
        df_sim = df_raw.copy()
        df_sim["calculation_date"] = pd.to_datetime(df_sim["calculation_date"])
        df_sim = df_sim.sort_values("calculation_date").reset_index(drop=True)

        latest_date = df_sim["calculation_date"].iloc[-1].date()
        current_index = float(df_sim["laspeyres_index"].iloc[-1])

        forecast_steps: list[ForecastStep] = []
        prev_idx = current_index
        residual_std = model.residual_std or 1.20

        for h in range(1, horizon_days + 1):
            next_date = latest_date + datetime.timedelta(days=h)

            # 1. Engineer feature vector from the rolling synthetic tail
            tail_df = df_sim.tail(20).copy().reset_index(drop=True)

            # Compute rolling statistics
            lag1 = float(tail_df["laspeyres_index"].iloc[-1])
            lag2 = float(tail_df["laspeyres_index"].iloc[-2]) if len(tail_df) >= 2 else lag1
            lag3 = float(tail_df["laspeyres_index"].iloc[-3]) if len(tail_df) >= 3 else lag2
            lag7 = float(tail_df["laspeyres_index"].iloc[-7]) if len(tail_df) >= 7 else lag3

            r_mean7 = float(tail_df["laspeyres_index"].tail(7).mean())
            r_std7 = float(tail_df["laspeyres_index"].tail(7).std() or 0.5)
            r_mean14 = float(tail_df["laspeyres_index"].tail(14).mean())

            momentum7 = (lag1 - lag7) / max(1.0, lag1)
            spot_val = float(tail_df["spot_t1_index"].iloc[-1]) if "spot_t1_index" in tail_df else lag1 * 2.45
            spot_spread = spot_val / max(1.0, lag1)
            fisher_val = float(tail_df["fisher_index"].iloc[-1]) if "fisher_index" in tail_df else lag1
            fisher_spread = (fisher_val - lag1) / max(1.0, lag1)

            dow = next_date.weekday()
            dow_sin = math.sin(2 * math.pi * dow / 7.0)
            dow_cos = math.cos(2 * math.pi * dow / 7.0)
            weekend_ind = 1.0 if dow >= 4 else 0.0
            atf_proxy = (len(df_sim) + h) * 0.0015
            quote_density = 0.95

            feature_dict = {
                "lag_1_laspeyres": lag1,
                "lag_2_laspeyres": lag2,
                "lag_3_laspeyres": lag3,
                "lag_7_laspeyres": lag7,
                "rolling_mean_7d": r_mean7,
                "rolling_std_7d": r_std7,
                "rolling_mean_14d": r_mean14,
                "momentum_7d": momentum7,
                "spot_t1_spread_ratio": spot_spread,
                "fisher_relative_spread": fisher_spread,
                "day_of_week_sin": dow_sin,
                "day_of_week_cos": dow_cos,
                "weekend_indicator": weekend_ind,
                "atf_drift_proxy": atf_proxy,
                "valid_quote_density": quote_density,
            }

            X_step = pd.DataFrame([feature_dict])[FeatureEngineer.FEATURE_NAMES]
            pred_index = model.predict_one_step(X_step)

            # Standard error grows with forecast horizon: sigma_h = sigma * sqrt(h)
            h_uncertainty = 1.96 * residual_std * math.sqrt(h)
            ci_lower = round(pred_index - h_uncertainty, 2)
            ci_upper = round(pred_index + h_uncertainty, 2)

            daily_chg = round(((pred_index - prev_idx) / prev_idx) * 100.0, 4) if prev_idx > 0 else 0.0

            # CPI Transmission Calculations
            w_air = CPI_WEIGHTS["airfare_share_within_transport"]  # 0.0385
            w_trans = CPI_WEIGHTS["transport_and_communication_cpi_weight"]  # 0.0859

            bps_trans = round(daily_chg * w_air * 100.0, 4)
            bps_head = round(bps_trans * w_trans, 4)

            step_record = ForecastStep(
                forecast_date=next_date.isoformat(),
                horizon_days=h,
                predicted_laspeyres_index=round(pred_index, 2),
                confidence_interval_95_lower=ci_lower,
                confidence_interval_95_upper=ci_upper,
                projected_daily_change_pct=daily_chg,
                projected_transport_impact_bps=bps_trans,
                projected_headline_cpi_impact_bps=bps_head,
            )
            forecast_steps.append(step_record)

            # Append forward step into synthetic rolling frame for autoregression
            new_row = {
                "calculation_date": pd.to_datetime(next_date),
                "laspeyres_index": pred_index,
                "fisher_index": pred_index * (1.0 + fisher_spread),
                "paasche_index": pred_index * (1.0 - abs(fisher_spread)),
                "spot_t1_index": pred_index * spot_spread,
                "daily_pct_change": daily_chg,
                "bps_transport_impact": bps_trans,
                "bps_headline_cpi_impact": bps_head,
                "observations_count": 950,
                "valid_quotes_count": 900,
                "outliers_rejected_count": 50,
            }
            df_sim = pd.concat([df_sim, pd.DataFrame([new_row])], ignore_index=True)
            prev_idx = pred_index

        # Aggregate summary metrics
        final_forecast = forecast_steps[-1].predicted_laspeyres_index
        net_pct_change = ((final_forecast - current_index) / current_index) * 100.0
        net_trans_bps = round(net_pct_change * CPI_WEIGHTS["airfare_share_within_transport"] * 100.0, 2)
        net_head_bps = round(net_trans_bps * CPI_WEIGHTS["transport_and_communication_cpi_weight"], 4)

        if net_head_bps > 0.50:
            alert = "HIGH_INFLATION_SURGE_WATCH"
        elif net_head_bps > 0.15:
            alert = "MODERATE_INFLATIONARY_PRESSURE"
        elif net_head_bps < -0.15:
            alert = "DISINFLATIONARY_COOLING"
        else:
            alert = "NEUTRAL_PRICE_STABILITY"

        feat_importances = model.metrics.feature_importances if model.metrics else {}

        return NowcastReport(
            as_of_date=latest_date.isoformat(),
            current_index=round(current_index, 2),
            model_version=model.metrics.model_version if model.metrics else "v1.0.0-JetIndex",
            forecast_horizon_days=horizon_days,
            summary_mean_forecast=round(float(np.mean([s.predicted_laspeyres_index for s in forecast_steps])), 2),
            net_projected_transport_bps=net_trans_bps,
            net_projected_headline_cpi_bps=net_head_bps,
            monetary_policy_alert=alert,
            forecast_steps=forecast_steps,
            feature_importances=feat_importances,
            generated_at=datetime.datetime.now(datetime.UTC).isoformat(),
        )
