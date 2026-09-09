"""ML forecasting — feature engineering, Ridge+GBD ensemble, multi-horizon nowcast.

Adapted from VayuSutra-V4 model_trainer.py (267 lines) and nowcast_predictor.py (244 lines).
Uses JetIndex's TimescaleDB instead of SQLite, and stores forecasts in the forecasts table.
"""

from __future__ import annotations

import math
import pickle
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

_AIRFARE_SHARE = 0.0385
_TRANSPORT_WEIGHT = 0.0859
_MODELS_DIR = Path("data/models")
_MODELS_DIR.mkdir(parents=True, exist_ok=True)
_MODEL_PATH = _MODELS_DIR / "apix_nowcast_ensemble.pkl"


# ──────────────────────────────────────────────────────────────────────────────
# Feature Engineering
# ──────────────────────────────────────────────────────────────────────────────


FEATURE_NAMES = [
    "lag_1",
    "lag_2",
    "lag_3",
    "lag_7",
    "rolling_mean_7d",
    "rolling_std_7d",
    "rolling_mean_14d",
    "momentum_7d",
    "spot_t1_spread",
    "fisher_spread",
    "dow_sin",
    "dow_cos",
    "weekend",
    "atf_drift",
    "quote_density",
]


def build_feature_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Extract 15 econometric features from a national-index time series.

    Expects columns: calculation_date, laspeyres_index, fisher_index,
    spot_t1_index, valid_quotes_count, observations_count.

    Returns (X, y) where y is the next-day laspeyres index (target).
    """
    df = df.copy()
    df["calculation_date"] = pd.to_datetime(df["calculation_date"])
    df = df.sort_values("calculation_date").reset_index(drop=True)

    idx = df["laspeyres_index"]

    # Autoregressive lags
    df["lag_1"] = idx.shift(1)
    df["lag_2"] = idx.shift(2)
    df["lag_3"] = idx.shift(3)
    df["lag_7"] = idx.shift(7)

    # Rolling statistics
    df["rolling_mean_7d"] = idx.rolling(7, min_periods=1).mean()
    df["rolling_std_7d"] = idx.rolling(7, min_periods=1).std().fillna(0.5)
    df["rolling_mean_14d"] = idx.rolling(14, min_periods=1).mean()

    # Momentum & spreads
    lag7 = df["lag_7"].fillna(idx)
    df["momentum_7d"] = (idx - lag7) / idx.clip(lower=1.0)

    spot = df.get("spot_t1_index", idx * 2.45)
    df["spot_t1_spread"] = spot / idx.clip(lower=1.0)

    fisher = df.get("fisher_index", idx)
    df["fisher_spread"] = (fisher - idx) / idx.clip(lower=1.0)

    # Cyclical calendar encoding
    dow = df["calculation_date"].dt.weekday
    df["dow_sin"] = np.sin(2 * np.pi * dow / 7.0)
    df["dow_cos"] = np.cos(2 * np.pi * dow / 7.0)
    df["weekend"] = (dow >= 4).astype(float)

    # Macro proxies
    df["atf_drift"] = np.arange(len(df)) * 0.0015
    obs = df.get("observations_count", pd.Series(1.0, index=df.index))
    valid = df.get("valid_quotes_count", pd.Series(0.95, index=df.index))
    df["quote_density"] = (valid / obs.clip(lower=1.0)).fillna(0.95)

    # Target: next-day index
    df["target"] = idx.shift(-1)

    clean = df.dropna(subset=["lag_7", "target"]).reset_index(drop=True)
    return clean[FEATURE_NAMES], clean["target"]


# ──────────────────────────────────────────────────────────────────────────────
# Ensemble Model
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class TrainingMetrics:
    """Model evaluation results."""

    r2_train: float = 0.0
    r2_test: float = 0.0
    rmse_train: float = 0.0
    rmse_test: float = 0.0
    mae_test: float = 0.0
    mape_test: float = 0.0
    pearson_r: float = 0.0
    sample_size: int = 0
    train_size: int = 0
    test_size: int = 0
    feature_importances: dict[str, float] = field(default_factory=dict)
    model_version: str = "jetindex-v1.0"


class ForecastEnsemble:
    """Ridge + GradientBoosting hybrid for airfare index nowcasting.

    Training uses chronological 80/20 split (no lookahead).
    Inference blends 40% Ridge + 60% GBDT.
    """

    def __init__(
        self,
        alpha: float = 2.0,
        n_estimators: int = 100,
        max_depth: int = 2,
    ):
        self.ridge = Ridge(alpha=alpha, random_state=42)
        self.gbr = GradientBoostingRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=0.03,
            min_samples_leaf=2,
            subsample=0.80,
            random_state=42,
        )
        self.metrics: TrainingMetrics | None = None
        self.residual_std: float = 1.25
        self.is_trained: bool = False

    def fit(self, X: pd.DataFrame, y: pd.Series, test_ratio: float = 0.20) -> TrainingMetrics:  # noqa: N803
        """Train with chronological split (no future leakage)."""
        split = max(5, int(len(X) * (1.0 - test_ratio)))
        X_train, X_test = X.iloc[:split], X.iloc[split:]  # noqa: N806
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        self.ridge.fit(X_train, y_train)
        self.gbr.fit(X_train, y_train)

        pred_tr = 0.5 * self.ridge.predict(X_train) + 0.5 * self.gbr.predict(X_train)
        pred_te = 0.5 * self.ridge.predict(X_test) + 0.5 * self.gbr.predict(X_test)

        r2_tr = float(r2_score(y_train, pred_tr))
        r2_te = float(r2_score(y_test, pred_te))
        rmse_tr = float(np.sqrt(mean_squared_error(y_train, pred_tr)))
        rmse_te = float(np.sqrt(mean_squared_error(y_test, pred_te)))
        mae_te = float(mean_absolute_error(y_test, pred_te))
        mape_te = float(mean_absolute_percentage_error(y_test, pred_te) * 100)

        pearson = float(np.corrcoef(pred_te, y_test)[0, 1]) if np.std(pred_te) > 0 and np.std(y_test) > 0 else 1.0

        residuals = y_test.values - pred_te
        self.residual_std = float(np.std(residuals)) if len(residuals) > 1 else 1.25

        # Feature importances (blended)
        gbr_imp = self.gbr.feature_importances_
        ridge_imp = np.abs(self.ridge.coef_)
        ridge_imp = ridge_imp / (ridge_imp.sum() + 1e-6)
        blended = 0.5 * gbr_imp + 0.5 * ridge_imp
        feat_imp = {
            name: round(float(imp), 4)
            for name, imp in sorted(zip(FEATURE_NAMES, blended, strict=False), key=lambda x: x[1], reverse=True)
        }

        self.metrics = TrainingMetrics(
            r2_train=round(r2_tr, 4),
            r2_test=round(r2_te, 4),
            rmse_train=round(rmse_tr, 4),
            rmse_test=round(rmse_te, 4),
            mae_test=round(mae_te, 4),
            mape_test=round(mape_te, 4),
            pearson_r=round(pearson, 4),
            sample_size=len(X),
            train_size=len(X_train),
            test_size=len(X_test),
            feature_importances=feat_imp,
        )
        self.is_trained = True
        return self.metrics

    def predict(self, X: pd.DataFrame) -> float:  # noqa: N803
        """Single-step prediction (40% Ridge + 60% GBDT)."""
        pred = 0.4 * self.ridge.predict(X) + 0.6 * self.gbr.predict(X)
        return float(pred[0])

    def save(self, path: Path | str = _MODEL_PATH) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Path | str = _MODEL_PATH) -> ForecastEnsemble:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model not found at {path}")
        with open(path, "rb") as f:
            return pickle.load(f)  # noqa: S301


# ──────────────────────────────────────────────────────────────────────────────
# Multi-Horizon Nowcast
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class ForecastStep:
    """One day of the forward forecast."""

    forecast_date: str
    horizon_days: int
    predicted_index: float
    ci_lower_95: float
    ci_upper_95: float
    daily_change_pct: float
    transport_bps: float
    headline_bps: float


@dataclass
class NowcastReport:
    """Complete multi-horizon nowcast."""

    as_of_date: str
    current_index: float
    horizon_days: int
    mean_forecast: float
    net_transport_bps: float
    net_headline_bps: float
    alert_level: str
    steps: list[ForecastStep]
    feature_importances: dict[str, float]


def generate_nowcast(
    session: Session,
    horizon_days: int = 14,
    model_path: Path | str = _MODEL_PATH,
) -> NowcastReport:
    """Generate a multi-horizon forward nowcast from DB data.

    Uses autoregressive rollout: each predicted step feeds back as input
    for the next. Confidence intervals widen with sqrt(horizon).
    """
    from db import queries as db_queries

    # Load historical data
    rows = db_queries.get_apix_daily(session)
    if not rows or len(rows) < 15:
        raise ValueError(f"Need >= 15 days of index data, got {len(rows) if rows else 0}")

    df = pd.DataFrame(rows)
    df["calculation_date"] = pd.to_datetime(df["date"])
    df = df.rename(columns={"apix": "laspeyres_index"})
    # Fill missing columns with defaults
    if "fisher_index" not in df.columns:
        df["fisher_index"] = df["laspeyres_index"]
    if "spot_t1_index" not in df.columns:
        df["spot_t1_index"] = df["laspeyres_index"] * 2.45
    if "valid_quotes_count" not in df.columns:
        df["valid_quotes_count"] = 900
    if "observations_count" not in df.columns:
        df["observations_count"] = 950

    # Load or train model
    model_path = Path(model_path)
    if model_path.exists():
        try:
            model = ForecastEnsemble.load(model_path)
        except Exception:
            model = _train_model(df, model_path)
    else:
        model = _train_model(df, model_path)

    # Autoregressive rollout
    df_sim = df.copy()
    df_sim["calculation_date"] = pd.to_datetime(df_sim["calculation_date"])
    df_sim = df_sim.sort_values("calculation_date").reset_index(drop=True)

    latest_date = df_sim["calculation_date"].iloc[-1].date()
    current_index = float(df_sim["laspeyres_index"].iloc[-1])
    prev_idx = current_index
    residual_std = model.residual_std or 1.20

    steps: list[ForecastStep] = []

    for h in range(1, horizon_days + 1):
        next_date = latest_date + timedelta(days=h)
        tail = df_sim.tail(20).copy().reset_index(drop=True)
        idx = tail["laspeyres_index"]

        lag1 = float(idx.iloc[-1])
        lag2 = float(idx.iloc[-2]) if len(idx) >= 2 else lag1
        lag3 = float(idx.iloc[-3]) if len(idx) >= 3 else lag2
        lag7 = float(idx.iloc[-7]) if len(idx) >= 7 else lag3

        feat = {
            "lag_1": lag1,
            "lag_2": lag2,
            "lag_3": lag3,
            "lag_7": lag7,
            "rolling_mean_7d": float(idx.tail(7).mean()),
            "rolling_std_7d": float(idx.tail(7).std() or 0.5),
            "rolling_mean_14d": float(idx.tail(14).mean()),
            "momentum_7d": (lag1 - lag7) / max(1.0, lag1),
            "spot_t1_spread": float(tail.get("spot_t1_index", pd.Series([lag1 * 2.45])).iloc[-1]) / max(1.0, lag1),
            "fisher_spread": (float(tail.get("fisher_index", pd.Series([lag1])).iloc[-1]) - lag1) / max(1.0, lag1),
            "dow_sin": math.sin(2 * math.pi * next_date.weekday() / 7.0),
            "dow_cos": math.cos(2 * math.pi * next_date.weekday() / 7.0),
            "weekend": 1.0 if next_date.weekday() >= 4 else 0.0,
            "atf_drift": (len(df_sim) + h) * 0.0015,
            "quote_density": 0.95,
        }

        X_step = pd.DataFrame([feat])[FEATURE_NAMES]  # noqa: N806
        pred = model.predict(X_step)

        ci_width = 1.96 * residual_std * math.sqrt(h)
        daily_chg = ((pred - prev_idx) / prev_idx * 100.0) if prev_idx > 0 else 0.0
        bps_trans = round(daily_chg * _AIRFARE_SHARE * 100.0, 4)
        bps_head = round(bps_trans * _TRANSPORT_WEIGHT, 4)

        steps.append(
            ForecastStep(
                forecast_date=next_date.isoformat(),
                horizon_days=h,
                predicted_index=round(pred, 2),
                ci_lower_95=round(pred - ci_width, 2),
                ci_upper_95=round(pred + ci_width, 2),
                daily_change_pct=round(daily_chg, 4),
                transport_bps=bps_trans,
                headline_bps=bps_head,
            )
        )

        # Feed prediction back into synthetic frame
        new_row = {
            "calculation_date": pd.to_datetime(next_date),
            "laspeyres_index": pred,
            "fisher_index": pred,
            "spot_t1_index": pred * 2.45,
        }
        df_sim = pd.concat([df_sim, pd.DataFrame([new_row])], ignore_index=True)
        prev_idx = pred

    # Summary
    final = steps[-1].predicted_index
    net_pct = ((final - current_index) / current_index * 100.0) if current_index else 0
    net_trans = round(net_pct * _AIRFARE_SHARE * 100.0, 2)
    net_head = round(net_trans * _TRANSPORT_WEIGHT, 4)

    if net_head > 0.50:
        alert = "HIGH_INFLATION_SURGE_WATCH"
    elif net_head > 0.15:
        alert = "MODERATE_INFLATIONARY_PRESSURE"
    elif net_head < -0.15:
        alert = "DISINFLATIONARY_COOLING"
    else:
        alert = "NEUTRAL_PRICE_STABILITY"

    return NowcastReport(
        as_of_date=latest_date.isoformat(),
        current_index=round(current_index, 2),
        horizon_days=horizon_days,
        mean_forecast=round(float(np.mean([s.predicted_index for s in steps])), 2),
        net_transport_bps=net_trans,
        net_headline_bps=net_head,
        alert_level=alert,
        steps=steps,
        feature_importances=model.metrics.feature_importances if model.metrics else {},
    )


def _train_model(df: pd.DataFrame, save_path: Path) -> ForecastEnsemble:
    """Internal: train and persist the ensemble."""
    X, y = build_feature_matrix(df)  # noqa: N806
    ensemble = ForecastEnsemble()
    metrics = ensemble.fit(X, y)
    ensemble.save(save_path)
    logger.info(
        "Forecast model trained: R²={}, RMSE={}, MAPE={}%, n={}",
        metrics.r2_test,
        metrics.rmse_test,
        metrics.mape_test,
        metrics.sample_size,
    )
    return ensemble
