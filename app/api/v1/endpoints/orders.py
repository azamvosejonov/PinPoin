from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus, CourierEarning
from app.models.restaurant import MenuItem, Restaurant
from app.schemas.schemas import OrderCreate, OrderOut
from app.services.ai_service import analyze_order
from app.services.tracking_service import get_all_available_couriers
from app.services.map_service import find_nearest_courier, calculate_distance
from app.services.notification_service import notify_order_status, notify_courier_assigned
from pydantic import BaseModel

router = APIRouter(prefix="/orders", tags=["Orders"])

class CancelRequest(BaseModel):
    reason: str

class PaymentUpdate(BaseModel):
    payment_method: str

async def _run_ai_analysis(order_id: int, items_info: list, db: AsyncSession):
    try:
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            order.ai_analysis = await analyze_order(items_info)
            await db.commit()
    except Exception:
        pass

def _check_restaurant_open(restaurant: Restaurant) -> bool:
    now = datetime.now().strftime("%H:%M")
    return restaurant.open_time <= now <= restaurant.close_time

@router.post("/", status_code=201)
async def create_order(data: OrderCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != UserRole.customer:
        raise HTTPException(status_code=403, detail="Faqat mijozlar buyurtma bera oladi")

    restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == data.restaurant_id))
    restaurant = restaurant_result.scalar_one_or_none()
    if not restaurant or not restaurant.is_active:
        raise HTTPException(status_code=404, detail="Restoran topilmadi yoki yopiq")
    if not _check_restaurant_open(restaurant):
        raise HTTPException(status_code=400, detail=f"Restoran hozir yopiq. Ish vaqti: {restaurant.open_time}–{restaurant.close_time}")

    total = 0.0
    items_info = []
    order_items = []

    for item_in in data.items:
        result = await db.execute(select(MenuItem).where(MenuItem.id == item_in.menu_item_id, MenuItem.is_available == True))
        menu_item = result.scalar_one_or_none()
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menyu elementi {item_in.menu_item_id} topilmadi")
        total += menu_item.price * item_in.quantity
        items_info.append({"name": menu_item.name, "calories": menu_item.calories, "temperature_sensitive": menu_item.temperature_sensitive})
        order_items.append(OrderItem(menu_item_id=item_in.menu_item_id, quantity=item_in.quantity, price=menu_item.price))

    if total < restaurant.min_order_price:
        raise HTTPException(status_code=400, detail=f"Minimal buyurtma narxi: {restaurant.min_order_price:,.0f} so'm")

    available_couriers = await get_all_available_couriers()
    nearest = find_nearest_courier(available_couriers, data.delivery_lat, data.delivery_lon)

    order = Order(
        customer_id=user.id,
        restaurant_id=data.restaurant_id,
        courier_id=nearest["courier_id"] if nearest else None,
        delivery_address=data.delivery_address,
        delivery_lat=data.delivery_lat,
        delivery_lon=data.delivery_lon,
        building_id=data.building_id,
        apartment_number=data.apartment_number,
        floor=data.floor,
        items_price=total,
        delivery_fee=restaurant.delivery_fee,
        total_price=total + restaurant.delivery_fee,
    )
    db.add(order)
    await db.flush()

    for oi in order_items:
        oi.order_id = order.id
        db.add(oi)

    await db.commit()
    await db.refresh(order)

    background_tasks.add_task(_run_ai_analysis, order.id, items_info, db)

    if nearest:
        await notify_courier_assigned(nearest["courier_id"], order.id, restaurant.name)

    return {
        "id": order.id,
        "status": order.status,
        "items_price": order.items_price,
        "delivery_fee": order.delivery_fee,
        "total_price": order.total_price,
        "delivery_address": order.delivery_address,
        "tracking_token": order.tracking_token,
        "tracking_link": f"{settings.BASE_URL}/track/{order.tracking_token}",
    }

@router.get("/my/list")
async def my_orders(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == UserRole.customer:
        result = await db.execute(select(Order).where(Order.customer_id == user.id).order_by(Order.created_at.desc()))
    elif user.role == UserRole.courier:
        result = await db.execute(select(Order).where(Order.courier_id == user.id).order_by(Order.created_at.desc()))
    else:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    orders = result.scalars().all()
    return [{"id": o.id, "status": o.status, "total_price": o.total_price, "delivery_address": o.delivery_address, "created_at": o.created_at} for o in orders]

@router.get("/{order_id}")
async def get_order(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    if order.customer_id != user.id and order.courier_id != user.id and user.role not in (UserRole.admin, UserRole.restaurant):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    return order

@router.patch("/{order_id}/status")
async def update_status(order_id: int, status: OrderStatus, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

    if user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Mijozlar status o'zgartira olmaydi")
    if user.role == UserRole.courier and order.courier_id != user.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    if user.role == UserRole.restaurant:
        rest_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id, Restaurant.owner_id == user.id))
        if not rest_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id))
    restaurant = restaurant_result.scalar_one_or_none()

    order.status = status
    if status == OrderStatus.delivered:
        order.delivered_at = datetime.utcnow()
        if order.courier_id:
            dist = calculate_distance(restaurant.lat, restaurant.lon, order.delivery_lat, order.delivery_lon) if restaurant else 0
            db.add(CourierEarning(courier_id=order.courier_id, order_id=order.id, amount=order.delivery_fee, distance_km=dist))

    await db.commit()

    if order.customer_id:
        await notify_order_status(order.customer_id, order_id, status)

    return {"status": status}

@router.post("/{order_id}/cancel")
async def cancel_order(order_id: int, data: CancelRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    if order.status not in (OrderStatus.pending, OrderStatus.confirmed):
        raise HTTPException(status_code=400, detail="Bu holatda buyurtmani bekor qilib bo'lmaydi")
    if user.role == UserRole.customer and order.customer_id != user.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    if user.role == UserRole.courier and order.courier_id != user.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    order.status = OrderStatus.cancelled
    order.cancelled_by = user.role
    order.cancel_reason = data.reason
    await db.commit()

    if order.customer_id:
        await notify_order_status(order.customer_id, order_id, "cancelled")

    return {"ok": True, "reason": data.reason}

@router.post("/{order_id}/reject")
async def courier_reject_order(order_id: int, data: CancelRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != UserRole.courier:
        raise HTTPException(status_code=403, detail="Faqat kuryerlar uchun")

    result = await db.execute(select(Order).where(Order.id == order_id, Order.courier_id == user.id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    if order.status not in (OrderStatus.pending, OrderStatus.confirmed):
        raise HTTPException(status_code=400, detail="Bu holatda rad etib bo'lmaydi")

    couriers = [c for c in await get_all_available_couriers() if c["courier_id"] != user.id]
    nearest = find_nearest_courier(couriers, order.delivery_lat, order.delivery_lon)
    order.courier_id = nearest["courier_id"] if nearest else None
    await db.commit()

    if nearest:
        rest_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id))
        restaurant = rest_result.scalar_one_or_none()
        await notify_courier_assigned(nearest["courier_id"], order.id, restaurant.name if restaurant else "Restoran")

    return {"ok": True, "new_courier_id": order.courier_id}

@router.patch("/{order_id}/payment")
async def update_payment(order_id: int, data: PaymentUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    if order.customer_id != user.id and user.role not in (UserRole.admin, UserRole.courier):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    order.payment_status = PaymentStatus.paid
    order.payment_method = data.payment_method
    await db.commit()
    return {"payment_status": "paid", "method": data.payment_method}

@router.get("/courier/earnings")
async def courier_earnings(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != UserRole.courier:
        raise HTTPException(status_code=403, detail="Faqat kuryerlar uchun")

    total = (await db.execute(select(func.coalesce(func.sum(CourierEarning.amount), 0)).where(CourierEarning.courier_id == user.id))).scalar()
    total_km = (await db.execute(select(func.coalesce(func.sum(CourierEarning.distance_km), 0)).where(CourierEarning.courier_id == user.id))).scalar()
    count = (await db.execute(select(func.count(CourierEarning.id)).where(CourierEarning.courier_id == user.id))).scalar()
    result = await db.execute(select(CourierEarning).where(CourierEarning.courier_id == user.id).order_by(CourierEarning.earned_at.desc()).limit(20))

    return {
        "total_earned": float(total),
        "total_km": float(total_km),
        "total_deliveries": count,
        "history": [{"order_id": e.order_id, "amount": e.amount, "distance_km": e.distance_km, "earned_at": e.earned_at} for e in result.scalars().all()],
    }
