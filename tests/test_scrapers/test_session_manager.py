"""Tests for SessionManager — persistence, expiry, and refresh."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scrapers.session_manager import SessionManager, SESSION_DIR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clean_sessions(tmp_path, monkeypatch):
    """Redirect SESSION_DIR to a temp directory for test isolation."""
    test_dir = tmp_path / ".sessions"
    test_dir.mkdir()
    monkeypatch.setattr("scrapers.session_manager.SESSION_DIR", test_dir)
    yield


@pytest.fixture
def mgr():
    return SessionManager()


# ---------------------------------------------------------------------------
# Tests — basic persistence
# ---------------------------------------------------------------------------

class TestSaveAndLoad:
    def test_roundtrip(self, mgr):
        mgr.save("indigo", {"token": "abc123", "cookies": {"sid": "xyz"}})
        loaded = mgr.load("indigo")
        assert loaded["token"] == "abc123"
        assert loaded["cookies"]["sid"] == "xyz"

    def test_saved_at_injected(self, mgr):
        mgr.save("indigo", {"foo": "bar"})
        loaded = mgr.load("indigo")
        assert "saved_at" in loaded
        # Should be a valid ISO timestamp
        datetime.fromisoformat(loaded["saved_at"])

    def test_load_missing_returns_empty(self, mgr):
        assert mgr.load("nonexistent") == {}


class TestClear:
    def test_clear_removes_file(self, mgr, tmp_path):
        mgr.save("indigo", {"x": 1})
        mgr.clear("indigo")
        assert mgr.load("indigo") == {}

    def test_clear_nonexistent_is_noop(self, mgr):
        mgr.clear("nonexistent")  # should not raise


# ---------------------------------------------------------------------------
# Tests — expiry
# ---------------------------------------------------------------------------

class TestIsExpired:
    def test_no_session_is_expired(self, mgr):
        assert mgr.is_expired("nonexistent") is True

    def test_fresh_session_not_expired(self, mgr):
        mgr.save("indigo", {"data": 1})
        assert mgr.is_expired("indigo", ttl_seconds=3600) is False

    def test_old_session_expired(self, mgr, tmp_path):
        """Manually set saved_at to the past."""
        old_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        session_file = tmp_path / ".sessions" / "indigo.json"
        session_file.write_text(json.dumps({"saved_at": old_time}))
        assert mgr.is_expired("indigo", ttl_seconds=3600) is True

    def test_valid_till_in_future_not_expired(self, mgr, tmp_path):
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        session_file = tmp_path / ".sessions" / "indigo.json"
        session_file.write_text(json.dumps({"valid_till": future, "saved_at": datetime.now(timezone.utc).isoformat()}))
        assert mgr.is_expired("indigo") is False

    def test_valid_till_in_past_is_expired(self, mgr, tmp_path):
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        session_file = tmp_path / ".sessions" / "indigo.json"
        session_file.write_text(json.dumps({"valid_till": past, "saved_at": datetime.now(timezone.utc).isoformat()}))
        assert mgr.is_expired("indigo") is True

    def test_expires_at_field_respected(self, mgr, tmp_path):
        future = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        session_file = tmp_path / ".sessions" / "indigo.json"
        session_file.write_text(json.dumps({"expires_at": future, "saved_at": datetime.now(timezone.utc).isoformat()}))
        assert mgr.is_expired("indigo") is False


# ---------------------------------------------------------------------------
# Tests — get_or_refresh
# ---------------------------------------------------------------------------

class TestGetOrRefresh:
    def test_valid_session_returned(self, mgr):
        mgr.save("indigo", {"token": "fresh"})
        data = mgr.get_or_refresh("indigo", ttl_seconds=3600)
        assert data["token"] == "fresh"

    def test_expired_session_cleared(self, mgr, tmp_path):
        old_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        session_file = tmp_path / ".sessions" / "indigo.json"
        session_file.write_text(json.dumps({"saved_at": old_time, "token": "stale"}))

        data = mgr.get_or_refresh("indigo", ttl_seconds=3600)
        assert data == {}
        # File should be deleted
        assert not session_file.exists()

    def test_missing_session_returns_empty(self, mgr):
        assert mgr.get_or_refresh("missing") == {}
