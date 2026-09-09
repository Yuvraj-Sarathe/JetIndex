"""
JetIndex - Real-Time WebSockets & Server-Sent Events (SSE) Streaming Service
Ported from VayuSutra-V4.
"""

import asyncio
import collections
import datetime
import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("jetindex.streaming")


class ConnectionManager:
    """Manages concurrent WebSocket subscriber connections with resilient heartbeat and broadcast queues."""

    def __init__(self, max_history_events: int = 100):
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()
        self.event_history: collections.deque = collections.deque(maxlen=max_history_events)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

        # Send recent events upon connection
        try:
            for event in list(self.event_history)[-10:]:
                await websocket.send_text(json.dumps(event))
        except Exception as e:
            logger.debug(f"Error replaying event history: {e}")

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast_event(self, event_type: str, data: dict[str, Any], message: str = "") -> None:
        """Broadcasts a structured JSON event to all connected WebSocket subscribers."""
        event = {
            "event_type": event_type,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "message": message,
            "data": data,
        }
        self.event_history.append(event)

        async with self._lock:
            dead_connections = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(event))
                except Exception:
                    dead_connections.append(connection)

            for dead in dead_connections:
                if dead in self.active_connections:
                    self.active_connections.remove(dead)

    def get_recent_events(self, limit: int = 30) -> list[dict[str, Any]]:
        return list(self.event_history)[-limit:]


# Global singleton instance
stream_manager = ConnectionManager()
