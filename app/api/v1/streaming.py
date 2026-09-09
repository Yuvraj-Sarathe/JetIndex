"""WebSocket Real-Time Streaming API."""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from engine.services.streaming import stream_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time index updates and anomaly broadcasts."""
    await stream_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type", "ping")

                if msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": "now"}))
                elif msg_type == "subscribe":
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "channels": msg.get("channels", ["national_index"]),
                    }))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "message": "Invalid JSON"}))

    except WebSocketDisconnect:
        await stream_manager.disconnect(websocket)
