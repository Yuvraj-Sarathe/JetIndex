"""Session manager — cookie/token persistence per source."""

import json
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger

SESSION_DIR = Path("data/raw/.sessions")

# Default TTL for sessions that do not carry an explicit expiry field.
DEFAULT_TTL_SECONDS = 3600  # 1 hour


class SessionManager:
    """Persist and reload cookies/tokens per source to disk.

    Sessions are stored at data/raw/.sessions/{source}.json.
    """

    def __init__(self):
        SESSION_DIR.mkdir(parents=True, exist_ok=True)

    def load(self, source: str) -> dict:
        """Load saved session data for a source."""
        session_file = SESSION_DIR / f"{source}.json"
        if session_file.exists():
            try:
                with open(session_file) as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                logger.warning("Failed to load session for {}: {}", source, e)
        return {}

    def save(self, source: str, data: dict) -> None:
        """Save session data for a source.

        Automatically injects a ``saved_at`` ISO-8601 timestamp so that
        expiry can be computed even when the session itself does not carry
        an explicit TTL.
        """
        session_file = SESSION_DIR / f"{source}.json"
        data_with_ts = {**data, "saved_at": datetime.now(UTC).isoformat()}
        try:
            with open(session_file, "w") as f:
                json.dump(data_with_ts, f, indent=2)
        except OSError as e:
            logger.warning("Failed to save session for {}: {}", source, e)

    def clear(self, source: str) -> None:
        """Clear session data for a source."""
        session_file = SESSION_DIR / f"{source}.json"
        if session_file.exists():
            session_file.unlink()

    # ------------------------------------------------------------------
    # Expiry helpers
    # ------------------------------------------------------------------

    def is_expired(self, source: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> bool:
        """Check if the stored session for *source* has expired.

        Expiry is determined by (in priority order):
        1. ``valid_till`` — an ISO-8601 deadline stored in the session.
        2. ``expires_at`` — same semantics as ``valid_till``.
        3. ``saved_at + ttl_seconds`` — fallback when no explicit deadline
           is present.

        Returns ``True`` if expired **or** if no session exists.
        """
        data = self.load(source)
        if not data:
            return True

        now = datetime.now(UTC)

        # Check explicit deadline fields
        for key in ("valid_till", "expires_at"):
            deadline_str = data.get(key)
            if deadline_str:
                try:
                    deadline = datetime.fromisoformat(deadline_str)
                    # Ensure timezone-aware comparison
                    if deadline.tzinfo is None:
                        deadline = deadline.replace(tzinfo=UTC)
                    return now >= deadline
                except (ValueError, TypeError):
                    pass  # malformed — fall through to saved_at check

        # Fallback: saved_at + ttl
        saved_at_str = data.get("saved_at")
        if saved_at_str:
            try:
                saved_at = datetime.fromisoformat(saved_at_str)
                if saved_at.tzinfo is None:
                    saved_at = saved_at.replace(tzinfo=UTC)
                return (now - saved_at).total_seconds() >= ttl_seconds
            except (ValueError, TypeError):
                pass

        # No timing information at all — treat as expired to be safe
        return True

    def get_or_refresh(self, source: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> dict:
        """Return the session if it is still valid, otherwise clear and return ``{}``.

        This is the primary entry-point used by ``BaseScraper.fetch()``.
        """
        if self.is_expired(source, ttl_seconds):
            self.clear(source)
            return {}
        return self.load(source)
