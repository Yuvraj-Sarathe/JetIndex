"""Proxy manager for rotation, backoff on 429/403."""

from loguru import logger

from app.core.config import settings


class ProxyManager:
    """Manages proxy rotation with backoff for rate-limited/blocked responses.

    If PROXY_ENABLED=false, all requests go direct (no proxy).
    """

    def __init__(self):
        self.enabled = settings.PROXY_ENABLED
        self.proxies: list[str] = []
        if settings.PROXY_URL:
            self.proxies = [p.strip() for p in settings.PROXY_URL.split(",") if p.strip()]
        self._current_index = 0
        self._bad_proxies: dict[str, float] = {}  # proxy -> cooldown until

    def get(self) -> str | None:
        """Get the next available proxy, or None if direct."""
        if not self.enabled or not self.proxies:
            return None

        # Filter out proxies in cooldown
        import time

        now = time.time()
        available = [p for p in self.proxies if p not in self._bad_proxies or self._bad_proxies[p] < now]

        if not available:
            logger.warning("All proxies in cooldown, using direct connection")
            return None

        proxy = available[self._current_index % len(available)]
        self._current_index += 1
        return proxy

    def mark_bad(self, proxy: str, cooldown_seconds: float = 60.0) -> None:
        """Mark a proxy as bad (rate-limited/blocked) with a cooldown."""
        import time

        self._bad_proxies[proxy] = time.time() + cooldown_seconds
        logger.warning(f"Proxy {proxy} marked bad, cooldown {cooldown_seconds}s")

    def backoff(self, status_code: int) -> float:
        """Calculate backoff time based on HTTP status code."""
        if status_code == 429:
            return 30.0  # Rate limited — wait 30s
        elif status_code in (403, 401):
            return 60.0  # Blocked — wait 60s
        elif status_code >= 500:
            return 10.0  # Server error — wait 10s
        return 0.0
