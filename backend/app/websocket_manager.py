from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, order_id: str, websocket: WebSocket):
        await websocket.accept()
        if order_id not in self.active_connections:
            self.active_connections[order_id] = []
        self.active_connections[order_id].append(websocket)

    def disconnect(self, order_id: str, websocket: WebSocket):
        if order_id in self.active_connections:
            self.active_connections[order_id].remove(websocket)
            if not self.active_connections[order_id]:
                del self.active_connections[order_id]

    async def send_update(self, order_id: str, message: str):
        if order_id in self.active_connections:
            disconnected_connections = []
            for connection in self.active_connections[order_id]:
                try:
                    await connection.send_text(json.dumps({"status": message}))
                except Exception as e:
                    print(f"Failed to send WebSocket message to order {order_id}: {e}")
                    disconnected_connections.append(connection)

            for connection in disconnected_connections:
                self.active_connections[order_id].remove(connection)

            if not self.active_connections[order_id]:
                del self.active_connections[order_id]


manager = ConnectionManager()
