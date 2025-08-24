from backend.app.websocket_manager import manager
import asyncio
import json
from fastapi import Depends, APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import time

router = APIRouter()


@router.websocket("/orders/{order_id}")
async def websocket_endpoint(websocket: WebSocket, order_id: str):
    await manager.connect(order_id, websocket)
    print(f"WebSocket connection accepted for order_id={order_id}")
    await manager.broadcast_notification(f"User {order_id} đã tham gia cuộc trò chuyện")
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)
        print(f"WebSocket disconnected for order_id={order_id}")
        await manager.broadcast_notification(f"User {order_id} đã rời khỏi cuộc trò chuyện")


@router.websocket("/support/chat")
async def websocket_chat(
        websocket: WebSocket,
        token: str = Query(None),
        guest_id: str = Query(None),
        db: AsyncSession = Depends(get_db)
):
    print("WebSocket connection requested")
    await websocket.accept()
    print("WebSocket accepted")

    user_key = None

    try:
        if token:
            from backend.app.models import User
            from jose import JWTError, jwt
            from backend.app.config import settings

            SECRET_KEY = settings.SECRET_KEY
            ALGORITHM = settings.ALGORITHM

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = int(payload.get("sub"))
                user = await db.get(User, user_id)
                print(f"user.is_admin raw: {user.is_admin} ({type(user.is_admin)})")
                is_admin = bool(user.is_admin)
            except Exception as e:
                print(f"Token decode error: {e}")
                await websocket.close(code=1008)
                return

            if not user:
                print("User not found")
                await websocket.close(code=1008)
                return

            print(f"Authenticated user: {user.full_name}, role: {'admin' if is_admin else 'user'}")
            user_key = "admin" if is_admin else str(user.id)
        else:
            user_key = guest_id or f"guest-{id(websocket)}"
            print(f"Guest connected: {user_key}")

        await manager.connect(user_key, websocket)
        print(f"WebSocket connected: {user_key}")
        await manager.broadcast_user_list()
        await manager.broadcast_notification(f"{user_key} đã tham gia cuộc trò chuyện")

        while True:
            print(f"Waiting for message from {user_key}")
            data = await websocket.receive_text()
            print(f"Received from {user_key}: {data}")

            try:
                msg_obj = json.loads(data)
            except json.JSONDecodeError:
                print(f"Invalid JSON from {user_key}: {data}")
                continue

            msg_type = msg_obj.get("type")

            if msg_type == "typing":
                to_user = msg_obj.get("to")
                typing_msg = {
                    "type": "typing",
                    "from": user_key,
                    "typing": msg_obj.get("typing", False),
                    "timestamp": int(time.time() * 1000)
                }

                if user_key == "admin":
                    if to_user:
                        typing_msg["to"] = to_user
                        await manager.send_personal_message(to_user, typing_msg)
                else:
                    await manager.broadcast_to_admins(typing_msg)

                continue

            if user_key != "admin":
                message = {
                    "from": user_key,
                    "to": "admin",
                    "text": msg_obj.get("text"),
                    "timestamp": int(time.time() * 1000),
                }
                await manager.broadcast_to_admins(message)
                await manager.send_personal_message(user_key, message)
            else:
                to_user = msg_obj.get("to")
                text = msg_obj.get("text")

                if to_user == "AI" and text:
                    user_msg = {
                        "from": "admin",
                        "to": "AI",
                        "text": text,
                        "timestamp": int(time.time() * 1000),
                    }
                    await manager.send_personal_message("admin", user_msg)

                    typing_msg = {
                        "type": "typing",
                        "from": "AI",
                        "to": "admin",
                        "typing": True,
                        "timestamp": int(time.time() * 1000),
                    }
                    await manager.send_personal_message("admin", typing_msg)

                    await asyncio.sleep(1.5)

                    from backend.app.utils.ai_chat import ai_assistant
                    reply_text = ai_assistant.generate_reply(text)

                    reply_msg = {
                        "from": "AI",
                        "to": "admin",
                        "text": reply_text,
                        "timestamp": int(time.time() * 1000),
                    }
                    await manager.send_personal_message("admin", reply_msg)

                    typing_msg["typing"] = False
                    await manager.send_personal_message("admin", typing_msg)


    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {user_key}")
        manager.disconnect(user_key, websocket)
        await manager.broadcast_notification(f"{user_key} đã rời khỏi cuộc trò chuyện")

    except Exception as e:
        import traceback
        print(f"WebSocket error: {e}")
        traceback.print_exc()
        await websocket.close(code=1011)
        manager.disconnect(user_key, websocket)
        await manager.broadcast_notification(f"{user_key} đã rời khỏi cuộc trò chuyện")
