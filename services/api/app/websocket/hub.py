from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from loguru import logger

websocket_router = APIRouter()

# Active connections: channel -> set of websockets
connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        logger.info(f"WebSocket disconnected from channel: {channel}")

    async def broadcast(self, channel: str, message: dict):
        if channel in self.active_connections:
            dead = set()
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    dead.add(connection)
            for conn in dead:
                self.active_connections[channel].discard(conn)

    async def send_personal(self, websocket: WebSocket, message: dict):
        await websocket.send_text(json.dumps(message))


manager = ConnectionManager()


@websocket_router.websocket("/ws/v1")
async def websocket_endpoint(websocket: WebSocket):
    channel = "global"
    await manager.connect(websocket, channel)
    try:
        # Send welcome message
        await manager.send_personal(websocket, {
            "type": "connected",
            "message": "Connected to Supply Chain Intelligence Platform",
            "channels": ["global", "company:{ticker}", "risk:{ticker}", "alerts"],
        })
        
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action")
                
                if action == "subscribe":
                    new_channel = msg.get("channel", "global")
                    manager.disconnect(websocket, channel)
                    channel = new_channel
                    await manager.connect(websocket, channel)
                    await manager.send_personal(websocket, {
                        "type": "subscribed",
                        "channel": channel,
                    })
                
                elif action == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})
                
                elif action == "unsubscribe":
                    manager.disconnect(websocket, channel)
                    channel = "global"
                    await manager.connect(websocket, channel)
            
            except json.JSONDecodeError:
                pass
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


@websocket_router.websocket("/ws/v1/{channel}")
async def websocket_channel(websocket: WebSocket, channel: str):
    await manager.connect(websocket, channel)
    try:
        await manager.send_personal(websocket, {
            "type": "connected",
            "channel": channel,
        })
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("action") == "ping":
                await manager.send_personal(websocket, {"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
