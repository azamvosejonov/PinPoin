from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.api_key import APIKey
from app.models.order import Order, OrderItem, OrderStatus
from app.models.restaurant import Restaurant, MenuItem
from app.services.tracking_service import get_all_available_couriers
from app.services.map_service import find_nearest_courier
from app.services.notification_service import notify_courier_assigned
import httpx
from pydantic import BaseModel, field_validator
from typing import Optional
import re

router = APIRouter(prefix="/integration", tags=["Integration"])

class ExternalOrderItem(BaseModel):
    name: str
    quantity: int
    price: float

class ExternalOrderCreate(BaseModel):
    delivery_address: str
    delivery_lat: float
    delivery_lon: float
    items: list[ExternalOrderItem]
    customer_phone: Optional[str] = None
    webhook_url: Optional[str] = None

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v):
        if v is None:
            return v
        # Faqat https yoki http (localhost va private IP lar taqiqlangan)
        if not re.match(r'^https?://', v):
            raise ValueError("webhook_url http yoki https bilan boshlanishi kerak")
        blocked = ["localhost", "127.", "0.0.0.0", "10.", "192.168.", "172.16.", "169.254."]
        if any(b in v for b in blocked):
            raise ValueError("Ichki tarmoq manzillariga webhook yuborib bo'lmaydi")
        return v

class WebhookConfig(BaseModel):
    url: str
    secret: Optional[str] = None

# ── API Key boshqaruvi ────────────────────────────────

@router.post("/api-keys", status_code=201)
async def create_api_key(name: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role not in (UserRole.restaurant, UserRole.company, UserRole.admin):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    api_key = APIKey(owner_id=user.id, name=name)
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return {"id": api_key.id, "key": api_key.key, "name": api_key.name}

@router.get("/api-keys")
async def list_api_keys(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(APIKey).where(APIKey.owner_id == user.id))
    keys = result.scalars().all()
    return [{"id": k.id, "name": k.name, "is_active": k.is_active, "last_used_at": k.last_used_at} for k in keys]

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(key_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(APIKey).where(APIKey.id == key_id, APIKey.owner_id == user.id))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key topilmadi")
    key.is_active = False
    await db.commit()
    return {"ok": True}

# ── API key orqali autentifikatsiya ──────────────────

async def get_api_key_owner(x_api_key: str = Header(...), db: AsyncSession = Depends(get_db)) -> tuple[APIKey, User]:
    result = await db.execute(select(APIKey).where(APIKey.key == x_api_key, APIKey.is_active == True))
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=401, detail="Noto'g'ri yoki faol bo'lmagan API key")

    user_result = await db.execute(select(User).where(User.id == api_key.owner_id))
    owner = user_result.scalar_one_or_none()

    api_key.last_used_at = datetime.utcnow()
    await db.commit()
    return api_key, owner

# ── Tashqi tizimdan buyurtma qabul qilish ────────────

@router.post("/orders", status_code=201)
async def external_create_order(
    data: ExternalOrderCreate,
    auth: tuple = Depends(get_api_key_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Tashqi tizim (iiko, poster, custom POS) API key orqali buyurtma yuboradi.
    Header: X-Api-Key: pp_xxxxx
    """
    _, owner = auth

    # Ownerning birinchi aktiv restoranini topish
    rest_result = await db.execute(select(Restaurant).where(Restaurant.owner_id == owner.id, Restaurant.is_active == True))
    restaurant = rest_result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Aktiv restoran topilmadi")

    total = sum(i.price * i.quantity for i in data.items)

    available_couriers = await get_all_available_couriers()
    nearest = find_nearest_courier(available_couriers, data.delivery_lat, data.delivery_lon)

    order = Order(
        restaurant_id=restaurant.id,
        courier_id=nearest["courier_id"] if nearest else None,
        delivery_address=data.delivery_address,
        delivery_lat=data.delivery_lat,
        delivery_lon=data.delivery_lon,
        items_price=total,
        delivery_fee=restaurant.delivery_fee,
        total_price=total + restaurant.delivery_fee,
    )
    db.add(order)
    await db.flush()

    for item in data.items:
        db.add(OrderItem(order_id=order.id, menu_item_id=None, quantity=item.quantity, price=item.price))

    await db.commit()
    await db.refresh(order)

    if nearest:
        courier_result = await db.execute(select(User).where(User.id == nearest["courier_id"]))
        courier = courier_result.scalar_one_or_none()
        if courier and courier.fcm_token:
            await notify_courier_assigned(courier.fcm_token, order.id, restaurant.name)

    tracking_link = f"{settings.BASE_URL}/track/{order.tracking_token}"

    # Webhook — tashqi tizimga darhol xabar berish
    if data.webhook_url:
        await _send_webhook(data.webhook_url, {
            "event": "order_created",
            "order_id": order.id,
            "tracking_link": tracking_link,
            "status": order.status,
        })

    return {
        "order_id": order.id,
        "tracking_token": order.tracking_token,
        "tracking_link": tracking_link,
        "courier_assigned": nearest is not None,
    }

@router.post("/webhook/order-status/{order_id}")
async def notify_external_webhook(order_id: int, webhook_url: str, db: AsyncSession = Depends(get_db)):
    """Buyurtma holati o'zgarganda tashqi tizimga xabar beradi"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    await _send_webhook(webhook_url, {"event": "status_changed", "order_id": order_id, "status": order.status})
    return {"ok": True}

async def _send_webhook(url: str, payload: dict):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(url, json=payload)
    except Exception:
        pass
