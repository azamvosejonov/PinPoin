"""
Push Notification tizimi — FCM siz, to'liq o'zimizniki.

Arxitektura:
  notify_*() → Redis PUBLISH → WebSocket listener → Client

Har bir foydalanuvchi login bo'lganda:
  WS /api/v1/notifications/ws?token=<jwt>
ga ulanadi va real-time xabarlar oladi.

Xabar formati:
  {
    "type": "order_status" | "new_order" | "support_reply" | "courier_location",
    "title": "...",
    "body": "...",
    "data": {...}
  }
"""

import json
from app.services.tracking_service import redis_client

CHANNEL_PREFIX = "notify:user:"

async def _publish(user_id: int, payload: dict):
    """Redis orqali foydalanuvchiga xabar yuboradi"""
    await redis_client.publish(f"{CHANNEL_PREFIX}{user_id}", json.dumps(payload))

# ── Buyurtma holati ───────────────────────────────────

ORDER_MESSAGES = {
    "confirmed":  ("Buyurtma tasdiqlandi ✅", "Restoran buyurtmangizni qabul qildi"),
    "preparing":  ("Tayyorlanmoqda 👨‍🍳", "Ovqatingiz tayyorlanmoqda"),
    "picked_up":  ("Kuryer oldi 🛵", "Kuryer buyurtmangizni restorandan oldi"),
    "on_the_way": ("Yo'lda 🚀", "Kuryer sizga kelmoqda"),
    "delivered":  ("Yetkazildi 🎉", "Buyurtmangiz yetkazib berildi. Ishtaha bo'lsin!"),
    "cancelled":  ("Bekor qilindi ❌", "Buyurtmangiz bekor qilindi"),
}

async def notify_order_status(user_id: int, order_id: int, status: str):
    title, body = ORDER_MESSAGES.get(status, ("Yangilik", f"Buyurtma #{order_id} holati: {status}"))
    await _publish(user_id, {
        "type": "order_status",
        "title": title,
        "body": body,
        "data": {"order_id": order_id, "status": status},
    })

async def notify_courier_assigned(courier_id: int, order_id: int, restaurant_name: str):
    await _publish(courier_id, {
        "type": "new_order",
        "title": "Yangi buyurtma 📦",
        "body": f"{restaurant_name} dan buyurtma tayinlandi",
        "data": {"order_id": order_id},
    })

async def notify_support_reply(user_id: int, ticket_id: int):
    await _publish(user_id, {
        "type": "support_reply",
        "title": "Support javobi 💬",
        "body": "Murojaatingizga javob keldi",
        "data": {"ticket_id": ticket_id},
    })
