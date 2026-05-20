from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.tracking_service import redis_client
import asyncio
import json

router = APIRouter(prefix="/notifications", tags=["Notifications"])

CHANNEL_PREFIX = "notify:user:"

@router.websocket("/ws")
async def notification_websocket(websocket: WebSocket, token: str, db: AsyncSession = Depends(get_db)):
    """
    Barcha push notificationlar shu kanal orqali keladi.
    Ulanish: ws://host/api/v1/notifications/ws?token=<jwt>

    Xabar formatlari:
      {"type": "order_status",   "title": "...", "body": "...", "data": {"order_id": 1, "status": "..."}}
      {"type": "new_order",      "title": "...", "body": "...", "data": {"order_id": 1}}
      {"type": "support_reply",  "title": "...", "body": "...", "data": {"ticket_id": 1}}
    """
    # Token tekshirish
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            await websocket.close(code=4001)
            return
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        await websocket.close(code=4001)
        return

    user_result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    if not user_result.scalar_one_or_none():
        await websocket.close(code=4001)
        return

    await websocket.accept()

    # Redis Pub/Sub — foydalanuvchiga tegishli kanalga obuna bo'lamiz
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"{CHANNEL_PREFIX}{user_id}")

    async def listen():
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    await websocket.send_text(message["data"])
                except Exception:
                    break

    listener_task = asyncio.create_task(listen())

    try:
        # Client dan ping kutamiz (ulanish tirik ekanligini tekshirish)
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                # 30 soniyada ping yo'q bo'lsa ham ulanish davom etadi
                pass
    except WebSocketDisconnect:
        pass
    finally:
        listener_task.cancel()
        await pubsub.unsubscribe(f"{CHANNEL_PREFIX}{user_id}")
        await pubsub.aclose()
