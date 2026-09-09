"""Tests for forecasting engine."""

import math

import numpy as np
import pandas as pd
import pytest

from engine.forecasting import (
    FEATURE_NAMES,
    ForecastEnsemble,
    TrainingMetrics,
    build_feature_matrix,
)


class TestFeatureMatrix:
    """Tests for feature engineering."""

    def _make_df(self, n: int = 30) -> pd.DataFrame:
        """Create a synthetic time series DataFrame."""
        dates = pd.date_range("2025-01-01", periods=n, freq="D")
        np.random.seed(42)
        base = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
        return pd.DataFrame({
            "calculation_date": dates,
            "laspeyres_index": base,
            "fisher_index": base + np.random.randn(n) * 0.1,
            "spot_t1_index": base * 2.45,
            "valid_quotes_count": np.full(n, 900),
            "observations_count": np.full(n, 950),
        })

    def test_build_feature_matrix_returns_correct_shape(self):
        df = self._make_df(30)
        X, y = build_feature_matrix(df)
        assert len(X) == len(y)
        assert list(X.columns) == FEATURE_NAMES

    def test_build_feature_matrix_drops_nans(self):
        df = self._make_df(30)
        X, y = build_feature_matrix(df)
        assert X.isna().sum().sum() == 0
        assert y.isna().sum() == 0

    def test_build_feature_matrix_has_all_features(self):
        df = self._make_df(30)
        X, _ = build_feature_matrix(df)
        for feat in FEATURE_NAMES:
            assert feat in X.columns


class TestForecastEnsemble:
    """Tests for the Ridge+GBDT ensemble."""

    def _make_data(self, n: int = 50):
        """Create synthetic training data."""
        np.random.seed(42)
        X = pd.DataFrame(np.random.randn(n, len(FEATURE_NAMES)), columns=FEATURE_NAMES)
        y = pd.Series(100.0 + np.cumsum(np.random.randn(n) * 0.3))
        return X, y

    def test_fit_returns_metrics(self):
        X, y = self._make_data()
        ensemble = ForecastEnsemble()
        metrics = ensemble.fit(X, y)
        assert isinstance(metrics, TrainingMetrics)
        assert metrics.sample_size == len(X)
        assert metrics.train_size + metrics.test_size == len(X)
        # R2 can be negative on random data — just check it's a valid float
        assert isinstance(metrics.r2_test, float)

    def test_predict_returns_float(self):
        X, y = self._make_data()
        ensemble = ForecastEnsemble()
        ensemble.fit(X, y)
        pred = ensemble.predict(X.iloc[:1])
        assert isinstance(pred, float)

    def test_is_trained_after_fit(self):
        X, y = self._make_data()
        ensemble = ForecastEnsemble()
        assert not ensemble.is_trained
        ensemble.fit(X, y)
        assert ensemble.is_trained

    def test_residual_std_after_fit(self):
        X, y = self._make_data()
        ensemble = ForecastEnsemble()
        ensemble.fit(X, y)
        assert ensemble.residual_std > 0.0

    def test_feature_importances_populated(self):
        X, y = self._make_data()
        ensemble = ForecastEnsemble()
        metrics = ensemble.fit(X, y)
        assert len(metrics.feature_importances) == len(FEATURE_NAMES)
        assert all(v >= 0 for v in metrics.feature_importances.values())


class TestCpiTransmission:
    """Tests for CPI transmission calculation."""

    def test_transmission_basic(self):
        from engine.forecasting import _AIRFARE_SHARE, _TRANSPORT_WEIGHT
        # 1% airfare change → 3.85 bps transport → 0.33 bps headline
        daily_pct = 1.0
        transport_bps = daily_pct * _AIRFARE_SHARE * 100.0
        headline_bps = transport_bps * _TRANSPORT_WEIGHT
        assert abs(transport_bps - 3.85) < 0.01
        assert abs(headline_bps - 0.3307) < 0.01
