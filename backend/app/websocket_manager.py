import time

from fastapi import WebSocket
from typing import Dict, List, Union
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.admins: List[WebSocket] = []

    async def connect(self, user_id: str, websocket: WebSocket):
        if user_id == "admin":
            if websocket not in self.admins:
                self.admins.append(websocket)
                print(f"Admin websocket connected. Total admins: {len(self.admins)}")
        else:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            if websocket not in self.active_connections[user_id]:
                self.active_connections[user_id].append(websocket)
            print(
                f"User {user_id} websocket connected. Total connections for user: {len(self.active_connections[user_id])}")
        await self.broadcast_user_list()

    def disconnect(self, order_id: str, websocket: WebSocket):
        if order_id == "admin":
            if websocket in self.admins:
                self.admins.remove(websocket)
        else:
            if order_id in self.active_connections:
                if websocket in self.active_connections[order_id]:
                    self.active_connections[order_id].remove(websocket)
                if not self.active_connections[order_id]:
                    del self.active_connections[order_id]

    async def send_update(self, order_id: str, message: Union[str, dict]):
        if order_id in self.active_connections:
            disconnected = []
            for conn in self.active_connections[order_id]:
                try:
                    if isinstance(message, dict):
                        await conn.send_text(json.dumps(message))
                    else:
                        await conn.send_text(message)
                except Exception as e:
                    print(f"Send error: {e}")
                    disconnected.append(conn)
            for conn in disconnected:
                self.active_connections[order_id].remove(conn)
            if not self.active_connections[order_id]:
                del self.active_connections[order_id]

    async def broadcast_to_admins(self, message: Union[str, dict]):
        disconnected = []
        for admin_ws in self.admins:
            try:
                if isinstance(message, dict):
                    await admin_ws.send_text(json.dumps(message))
                else:
                    await admin_ws.send_text(message)
            except Exception as e:
                print(f"Send error to admin: {e}")
                disconnected.append(admin_ws)
        for ws in disconnected:
            self.admins.remove(ws)

    async def send_personal_message(self, user_id: str, message: Union[str, dict]):
        print(f"send_personal_message called with user_id={user_id}")
        if user_id == "admin":
            disconnected = []
            for admin_ws in self.admins:
                try:
                    if isinstance(message, dict):
                        await admin_ws.send_text(json.dumps(message))
                    else:
                        await admin_ws.send_text(message)
                except Exception as e:
                    print(f"Send personal message error to admin: {e}")
                    disconnected.append(admin_ws)
            for ws in disconnected:
                self.admins.remove(ws)
        else:
            if user_id in self.active_connections:
                disconnected = []
                for conn in self.active_connections[user_id]:
                    try:
                        if isinstance(message, dict):
                            await conn.send_text(json.dumps(message))
                        else:
                            await conn.send_text(message)
                    except Exception as e:
                        print(f"Send personal message error: {e}")
                        disconnected.append(conn)
                for conn in disconnected:
                    self.active_connections[user_id].remove(conn)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]

    async def broadcast(self, message: dict):
        disconnected_users = []
        for user_id, conns in list(self.active_connections.items()):
            to_remove = []
            for conn in conns:
                try:
                    await conn.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Broadcast send error to user {user_id}: {e}")
                    to_remove.append(conn)
            for conn in to_remove:
                conns.remove(conn)
            if not conns:
                disconnected_users.append(user_id)
        for user_id in disconnected_users:
            del self.active_connections[user_id]

        disconnected_admins = []
        for admin_ws in self.admins:
            try:
                await admin_ws.send_text(json.dumps(message))
            except Exception as e:
                print(f"Broadcast send error to admin: {e}")
                disconnected_admins.append(admin_ws)
        for ws in disconnected_admins:
            self.admins.remove(ws)

    async def broadcast_notification(self, text: str):
        message = {
            "type": "notification",
            "text": text,
            "timestamp": int(time.time() * 1000)
        }
        for user, conns in self.active_connections.items():
            for ws in conns:
                await ws.send_json(message)

    async def broadcast_user_list(self):
        user_list = list(self.active_connections.keys())
        message = {
            "type": "online_users",
            "users": user_list,
        }
        await self.broadcast_json(message)

    async def broadcast_json(self, data: dict):
        disconnected_users = []

        for user_id, ws_list in self.active_connections.items():
            to_remove = []
            for ws in ws_list:
                try:
                    await ws.send_json(data)
                except Exception:
                    to_remove.append(ws)
            for ws in to_remove:
                ws_list.remove(ws)
            if not ws_list:
                disconnected_users.append(user_id)

        for user_id in disconnected_users:
            del self.active_connections[user_id]

        disconnected_admins = []
        for admin_ws in self.admins:
            try:
                await admin_ws.send_json(data)
            except Exception:
                disconnected_admins.append(admin_ws)
        for ws in disconnected_admins:
            self.admins.remove(ws)


manager = ConnectionManager()
