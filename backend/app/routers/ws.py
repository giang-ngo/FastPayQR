from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.websocket_manager import manager  # đảm bảo đã đúng import
import asyncio

router = APIRouter()

@router.websocket("/ws/orders/{order_id}")
async def websocket_endpoint(websocket: WebSocket, order_id: str):
    await manager.connect(order_id, websocket)
    print(f"WebSocket connection accepted for order_id={order_id}")
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)
        print(f"WebSocket disconnected for order_id={order_id}")

