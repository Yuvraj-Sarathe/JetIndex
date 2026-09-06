"""Tests for ProxyManager — rotation, cooldown, failure escalation."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from scrapers.proxy_manager import ProxyManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_manager(proxies: list[str] | None = None, enabled: bool = True) -> ProxyManager:
    """Build a ProxyManager with overridden settings (no .env needed)."""
    with patch("scrapers.proxy_manager.settings") as mock_settings:
        mock_settings.PROXY_ENABLED = enabled
        mock_settings.PROXY_URL = ",".join(proxies) if proxies else ""
        return ProxyManager()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRoundRobin:
    def test_cycles_through_proxies(self):
        pm = _make_manager(["http://a:1", "http://b:2", "http://c:3"])
        results = [pm.get() for _ in range(6)]
        # Should cycle: a, b, c, a, b, c
        assert results[0] != results[1]
        assert results[:3] == results[3:]

    def test_single_proxy(self):
        pm = _make_manager(["http://only:1"])
        assert pm.get() == "http://only:1"
        assert pm.get() == "http://only:1"


class TestMarkBad:
    def test_marked_proxy_not_returned(self):
        pm = _make_manager(["http://a:1", "http://b:2"])
        pm.mark_bad("http://a:1", cooldown_seconds=600)
        # Only b should be returned
        results = {pm.get() for _ in range(5)}
        assert results == {"http://b:2"}

    def test_all_proxies_bad_returns_none(self):
        pm = _make_manager(["http://a:1", "http://b:2"])
        pm.mark_bad("http://a:1", cooldown_seconds=600)
        pm.mark_bad("http://b:2", cooldown_seconds=600)
        assert pm.get() is None


class TestCooldownExpiry:
    def test_expired_proxy_becomes_available(self):
        pm = _make_manager(["http://a:1"])
        # Set cooldown in the past
        pm._bad_proxies["http://a:1"] = time.time() - 1
        assert pm.get() == "http://a:1"
        # Should also be cleaned up from _bad_proxies
        assert "http://a:1" not in pm._bad_proxies


class TestCleanupExpired:
    def test_removes_expired_entries(self):
        pm = _make_manager(["http://a:1", "http://b:2"])
        pm._bad_proxies = {
            "http://a:1": time.time() - 10,  # expired
            "http://b:2": time.time() + 600,  # still active
        }
        pm._failure_counts = {"http://a:1": 3, "http://b:2": 1}
        removed = pm.cleanup_expired()
        assert removed == 1
        assert "http://a:1" not in pm._bad_proxies
        assert "http://a:1" not in pm._failure_counts
        assert "http://b:2" in pm._bad_proxies


class TestFailureEscalation:
    def test_escalates_cooldown_after_threshold(self):
        pm = _make_manager(["http://a:1", "http://b:2"])
        for _ in range(5):
            pm.mark_bad("http://a:1", cooldown_seconds=60)

        # After 5 failures the cooldown should be >= ESCALATED_COOLDOWN (300s)
        cooldown_until = pm._bad_proxies["http://a:1"]
        assert cooldown_until >= time.time() + 299  # ~300s from now

    def test_failure_count_tracks_correctly(self):
        pm = _make_manager(["http://a:1"])
        pm.mark_bad("http://a:1")
        pm.mark_bad("http://a:1")
        assert pm._failure_counts["http://a:1"] == 2


class TestDisabled:
    def test_disabled_always_returns_none(self):
        pm = _make_manager(["http://a:1", "http://b:2"], enabled=False)
        assert pm.get() is None
        assert pm.get() is None

    def test_no_proxies_returns_none(self):
        pm = _make_manager([], enabled=True)
        assert pm.get() is None


class TestGetStats:
    def test_stats_all_available(self):
        pm = _make_manager(["http://a:1", "http://b:2", "http://c:3"])
        stats = pm.get_stats()
        assert stats == {"total": 3, "available": 3, "in_cooldown": 0}

    def test_stats_with_bad_proxies(self):
        pm = _make_manager(["http://a:1", "http://b:2", "http://c:3"])
        pm.mark_bad("http://a:1", cooldown_seconds=600)
        stats = pm.get_stats()
        assert stats == {"total": 3, "available": 2, "in_cooldown": 1}

    def test_stats_empty_pool(self):
        pm = _make_manager([], enabled=True)
        stats = pm.get_stats()
        assert stats == {"total": 0, "available": 0, "in_cooldown": 0}
