from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user, decrypt
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.restaurant import Restaurant
from app.models.building import Building, ApartmentAccess
from app.schemas.schemas import CourierLocationUpdate, RouteResponse
from app.services.map_service import get_route, calculate_distance
from app.services.fuel_service import calculate_fuel_cost
from app.services.tracking_service import (
    update_courier_location, get_courier_location,
    set_order_tracking, get_order_tracking
)
from app.services.ai_service import get_navigation_instructions
from app.services.notification_service import notify_order_status
import asyncio

router = APIRouter(prefix="/delivery", tags=["Delivery"])

@router.patch("/availability")
async def update_availability(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Kuryer ish holatini almashtiradi: band / bo'sh"""
    if user.role != UserRole.courier:
        raise HTTPException(status_code=403, detail="Faqat kuryerlar uchun")
    user.is_available = not user.is_available
    await db.commit()
    return {"is_available": user.is_available}

@router.post("/orders/{order_id}/accept")
async def accept_order(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Kuryer buyurtmani qabul qiladi — status confirmed ga o'tadi"""
    if user.role != UserRole.courier:
        raise HTTPException(status_code=403, detail="Faqat kuryerlar uchun")

    result = await db.execute(select(Order).where(Order.id == order_id, Order.courier_id == user.id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi yoki sizga tegishli emas")
    if order.status != OrderStatus.pending:
        raise HTTPException(status_code=400, detail=f"Buyurtma holati: {order.status}, qabul qilib bo'lmaydi")

    order.status = OrderStatus.confirmed
    user.is_available = False  # Qabul qilgandan keyin band bo'ladi
    await db.commit()

    if order.customer_id:
        await notify_order_status(order.customer_id, order_id, "confirmed")

    return {"ok": True, "status": order.status}

@router.post("/location")
async def update_location(data: CourierLocationUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role != UserRole.courier:
        raise HTTPException(status_code=403, detail="Faqat kuryerlar uchun")
    user.current_lat = data.lat
    user.current_lon = data.lon
    await db.commit()
    await update_courier_location(user.id, data.lat, data.lon)
    return {"ok": True}

@router.get("/route/{order_id}", response_model=RouteResponse)
async def get_delivery_route(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

    courier_loc = await get_courier_location(user.id)
    if not courier_loc:
        if not user.current_lat:
            raise HTTPException(status_code=400, detail="Kuryer joylashuvi noma'lum")
        courier_loc = {"lat": user.current_lat, "lon": user.current_lon}

    restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id))
    restaurant = restaurant_result.scalar_one_or_none()

    route_to_restaurant = await get_route(courier_loc["lat"], courier_loc["lon"], restaurant.lat, restaurant.lon)
    route_to_customer = await get_route(restaurant.lat, restaurant.lon, order.delivery_lat, order.delivery_lon)

    combined_route = route_to_restaurant["route"] + route_to_customer["route"]
    combined_steps = (
        ["=== Restoranga ==="] + route_to_restaurant["navigation_steps"] +
        ["=== Mijozga ==="] + route_to_customer["navigation_steps"]
    )
    total_minutes = route_to_restaurant["estimated_minutes"] + route_to_customer["estimated_minutes"]
    total_km = round(route_to_restaurant["distance_km"] + route_to_customer["distance_km"], 2)

    await set_order_tracking(order_id, {"route": combined_route, "estimated_minutes": total_minutes})

    return RouteResponse(
        route=combined_route,
        estimated_minutes=total_minutes,
        distance_km=total_km,
        navigation_steps=combined_steps,
    )

@router.get("/fuel-cost/{order_id}")
async def get_fuel_cost(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Buyurtma uchun yoqilg'i/elektr xarajatini hisoblaydi"""
    if user.role != UserRole.courier:
        raise HTTPException(status_code=403, detail="Faqat kuryerlar uchun")

    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

    courier_loc = await get_courier_location(user.id)
    if not courier_loc:
        if not user.current_lat:
            raise HTTPException(status_code=400, detail="Kuryer joylashuvi noma'lum")
        courier_loc = {"lat": user.current_lat, "lon": user.current_lon}

    restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id))
    restaurant = restaurant_result.scalar_one_or_none()

    # Umumiy masofa: kuryer → restoran → mijoz
    d1 = calculate_distance(courier_loc["lat"], courier_loc["lon"], restaurant.lat, restaurant.lon)
    d2 = calculate_distance(restaurant.lat, restaurant.lon, order.delivery_lat, order.delivery_lon)
    total_km = round(d1 + d2, 3)

    cost_info = calculate_fuel_cost(total_km)

    return {
        "order_id": order_id,
        "distance_to_restaurant_km": d1,
        "distance_to_customer_km": d2,
        **cost_info,
    }

@router.get("/navigate/{order_id}")
async def building_navigation(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order or not order.building_id:
        raise HTTPException(status_code=404, detail="Buyurtma yoki bino topilmadi")

    building_result = await db.execute(select(Building).where(Building.id == order.building_id))
    building = building_result.scalar_one_or_none()

    access_result = await db.execute(
        select(ApartmentAccess).where(
            ApartmentAccess.customer_id == order.customer_id,
            ApartmentAccess.building_id == order.building_id,
            ApartmentAccess.apartment_number == order.apartment_number,
        )
    )
    access = access_result.scalar_one_or_none()

    steps = await get_navigation_instructions(
        floor=order.floor or 1,
        apartment=order.apartment_number or "?",
        has_elevator=building.has_elevator if building else False,
        floor_map=building.floor_map if building else None,
    )

    return {
        "building_address": building.address if building else None,
        "entrance_code": building.entrance_code if building else None,
        "floor": order.floor,
        "apartment": order.apartment_number,
        "door_code": decrypt(access.door_code_encrypted) if access and access.door_code_encrypted else None,
        "has_elevator": building.has_elevator if building else False,
        "navigation_steps": steps,
        "apartment_position": access.position if access else None,
    }

@router.get("/track/{order_id}")
async def track_order(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

    courier_loc = None
    if order.courier_id:
        courier_loc = await get_courier_location(order.courier_id)

    return {
        "order_id": order_id,
        "status": order.status,
        "courier_location": courier_loc,
        "tracking": await get_order_tracking(order_id),
    }

@router.websocket("/ws/{order_id}")
async def websocket_tracking(websocket: WebSocket, order_id: int, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            result = await db.execute(select(Order).where(Order.id == order_id))
            order = result.scalar_one_or_none()
            if not order:
                await websocket.send_json({"error": "Buyurtma topilmadi"})
                break
            courier_loc = None
            if order.courier_id:
                courier_loc = await get_courier_location(order.courier_id)
            await websocket.send_json({"status": order.status, "courier_location": courier_loc})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

# ── Mehmon tracking (login shart emas) ───────────────────────

@router.get("/guest/{tracking_token}")
async def guest_track(tracking_token: str, db: AsyncSession = Depends(get_db)):
    """
    Login shart emas. Link orqali buyurtmani kuzatish.
    GET /api/v1/delivery/guest/{tracking_token}
    """
    result = await db.execute(select(Order).where(Order.tracking_token == tracking_token))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

    courier_loc = None
    if order.courier_id:
        courier_loc = await get_courier_location(order.courier_id)

    restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id))
    restaurant = restaurant_result.scalar_one_or_none()

    return {
        "order_id": order.id,
        "status": order.status,
        "delivery_address": order.delivery_address,
        "restaurant_name": restaurant.name if restaurant else None,
        "courier_location": courier_loc,
        "estimated_minutes": (await get_order_tracking(order.id) or {}).get("estimated_minutes"),
        "created_at": order.created_at,
    }

@router.websocket("/guest/ws/{tracking_token}")
async def guest_websocket_tracking(websocket: WebSocket, tracking_token: str, db: AsyncSession = Depends(get_db)):
    """
    Login shart emas. WebSocket orqali real-time kuzatish.
    WS /api/v1/delivery/guest/ws/{tracking_token}
    """
    result = await db.execute(select(Order).where(Order.tracking_token == tracking_token))
    order = result.scalar_one_or_none()
    if not order:
        await websocket.close(code=4004)
        return

    await websocket.accept()
    try:
        while True:
            # Har 5 sekundda yangi ma'lumot yuborish
            await db.refresh(order)
            courier_loc = None
            if order.courier_id:
                courier_loc = await get_courier_location(order.courier_id)

            restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id))
            restaurant = restaurant_result.scalar_one_or_none()

            await websocket.send_json({
                "status": order.status,
                "courier_location": courier_loc,
                "restaurant_name": restaurant.name if restaurant else None,
                "estimated_minutes": (await get_order_tracking(order.id) or {}).get("estimated_minutes"),
            })

            if order.status in ("delivered", "cancelled"):
                break

            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
