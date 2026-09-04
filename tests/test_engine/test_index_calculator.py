"""Tests for engine/ package — index calculator."""

import pytest

from engine.index_calculator import geometric_young, laspeyres


def test_laspeyres_base_period():
    """Laspeyres index should be 100 when current = base prices."""
    p_t = {"DEL-BOM": 5000, "DEL-BLR": 5500, "BOM-BLR": 4500}
    p_0 = {"DEL-BOM": 5000, "DEL-BLR": 5500, "BOM-BLR": 4500}
    q_0 = {"DEL-BOM": 0.4, "DEL-BLR": 0.35, "BOM-BLR": 0.25}

    result = laspeyres(p_t, p_0, q_0)
    assert result == pytest.approx(100.0)


def test_laspeyres_price_increase():
    """Laspeyres should be > 100 when prices increase."""
    p_t = {"DEL-BOM": 5500, "DEL-BLR": 6050, "BOM-BLR": 4950}
    p_0 = {"DEL-BOM": 5000, "DEL-BLR": 5500, "BOM-BLR": 4500}
    q_0 = {"DEL-BOM": 0.4, "DEL-BLR": 0.35, "BOM-BLR": 0.25}

    result = laspeyres(p_t, p_0, q_0)
    assert result > 100.0
    assert result == pytest.approx(110.0)


def test_laspeyres_price_decrease():
    """Laspeyres should be < 100 when prices decrease."""
    p_t = {"DEL-BOM": 4500, "DEL-BLR": 4950, "BOM-BLR": 4050}
    p_0 = {"DEL-BOM": 5000, "DEL-BLR": 5500, "BOM-BLR": 4500}
    q_0 = {"DEL-BOM": 0.4, "DEL-BLR": 0.35, "BOM-BLR": 0.25}

    result = laspeyres(p_t, p_0, q_0)
    assert result < 100.0
    assert result == pytest.approx(90.0)


def test_geometric_young_base_period():
    """Geometric Young index should be 100 when current = base prices."""
    p_t = {"DEL-BOM": 5000, "DEL-BLR": 5500, "BOM-BLR": 4500}
    p_0 = {"DEL-BOM": 5000, "DEL-BLR": 5500, "BOM-BLR": 4500}
    q_0 = {"DEL-BOM": 0.4, "DEL-BLR": 0.35, "BOM-BLR": 0.25}

    result = geometric_young(p_t, p_0, q_0)
    assert result == pytest.approx(100.0)
