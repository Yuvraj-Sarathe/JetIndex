"""Proxy manager for rotation, backoff on 429/403."""

import time

from loguru import logger

from app.core.config import settings


class ProxyManager:
    """Manages proxy rotation with backoff for rate-limited/blocked responses.

    If PROXY_ENABLED=false, all requests go direct (no proxy).
    """

    # After this many consecutive failures the cooldown escalates.
    ESCALATION_THRESHOLD = 5
    ESCALATED_COOLDOWN = 300.0  # 5 minutes

    def __init__(self):
        self.enabled = settings.PROXY_ENABLED
        self.proxies: list[str] = []
        if settings.PROXY_URL:
            self.proxies = [p.strip() for p in settings.PROXY_URL.split(",") if p.strip()]
        self._current_index = 0
        self._bad_proxies: dict[str, float] = {}  # proxy -> cooldown until (epoch)
        self._failure_counts: dict[str, int] = {}  # proxy -> consecutive failure count

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self) -> str | None:
        """Get the next available proxy, or None if direct."""
        if not self.enabled or not self.proxies:
            return None

        # Purge expired cooldowns before selecting
        self.cleanup_expired()

        now = time.time()
        available = [
            p for p in self.proxies
            if p not in self._bad_proxies or self._bad_proxies[p] < now
        ]

        if not available:
            logger.warning("All proxies in cooldown, using direct connection")
            return None

        proxy = available[self._current_index % len(available)]
        self._current_index += 1
        return proxy

    def mark_bad(self, proxy: str, cooldown_seconds: float = 60.0) -> None:
        """Mark a proxy as bad (rate-limited/blocked) with a cooldown.

        After ``ESCALATION_THRESHOLD`` consecutive failures the cooldown is
        automatically escalated to ``ESCALATED_COOLDOWN`` seconds.
        """
        # Increment consecutive failure counter
        self._failure_counts[proxy] = self._failure_counts.get(proxy, 0) + 1
        count = self._failure_counts[proxy]

        effective_cooldown = cooldown_seconds
        if count >= self.ESCALATION_THRESHOLD:
            effective_cooldown = max(cooldown_seconds, self.ESCALATED_COOLDOWN)
            logger.warning(
                f"Proxy {proxy} has {count} consecutive failures — "
                f"escalating cooldown to {effective_cooldown}s"
            )

        self._bad_proxies[proxy] = time.time() + effective_cooldown
        logger.warning(f"Proxy {proxy} marked bad, cooldown {effective_cooldown}s (failures: {count})")

    def backoff(self, status_code: int) -> float:
        """Calculate backoff time based on HTTP status code."""
        if status_code == 429:
            return 30.0  # Rate limited — wait 30s
        elif status_code in (403, 401):
            return 60.0  # Blocked — wait 60s
        elif status_code >= 500:
            return 10.0  # Server error — wait 10s
        return 0.0

    def cleanup_expired(self) -> int:
        """Remove proxies from ``_bad_proxies`` whose cooldown has expired.

        Returns the number of entries removed.
        """
        now = time.time()
        expired = [p for p, until in self._bad_proxies.items() if until < now]
        for p in expired:
            del self._bad_proxies[p]
            # Reset failure counter when cooldown expires
            self._failure_counts.pop(p, None)
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired proxy cooldown(s)")
        return len(expired)

    def get_stats(self) -> dict:
        """Return a summary of the proxy pool's health.

        Returns a dict with keys: ``total``, ``available``, ``in_cooldown``.
        """
        now = time.time()
        in_cooldown = sum(1 for until in self._bad_proxies.values() if until >= now)
        return {
            "total": len(self.proxies),
            "available": len(self.proxies) - in_cooldown,
            "in_cooldown": in_cooldown,
        }
