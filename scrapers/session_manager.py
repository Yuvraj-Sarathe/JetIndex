"""Session manager — cookie/token persistence per source."""

import json
from pathlib import Path

from loguru import logger

SESSION_DIR = Path("data/raw/.sessions")


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
                logger.warning(f"Failed to load session for {source}: {e}")
        return {}

    def save(self, source: str, data: dict) -> None:
        """Save session data for a source."""
        session_file = SESSION_DIR / f"{source}.json"
        try:
            with open(session_file, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            logger.warning(f"Failed to save session for {source}: {e}")

    def clear(self, source: str) -> None:
        """Clear session data for a source."""
        session_file = SESSION_DIR / f"{source}.json"
        if session_file.exists():
            session_file.unlink()
