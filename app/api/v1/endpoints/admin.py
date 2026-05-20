from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant, MenuItem
from app.models.order import Order, OrderStatus
from app.models.visitor import TrackingPageVisit
from app.schemas.schemas import (
    UserOut, AdminUserUpdate, RestaurantOut,
    AdminRestaurantUpdate, StatsResponse
)

router = APIRouter(prefix="/admin", tags=["Admin"])

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Faqat adminlar uchun")
    return user

# ── Statistika ────────────────────────────────────────

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_restaurants = (await db.execute(select(func.count(Restaurant.id)))).scalar()
    total_orders = (await db.execute(select(func.count(Order.id)))).scalar()
    total_delivered = (await db.execute(
        select(func.count(Order.id)).where(Order.status == OrderStatus.delivered)
    )).scalar()
    total_revenue = (await db.execute(
        select(func.coalesce(func.sum(Order.total_price), 0)).where(Order.status == OrderStatus.delivered)
    )).scalar()

    # Har bir status bo'yicha buyurtmalar soni
    status_rows = (await db.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    )).all()
    orders_by_status = {row[0]: row[1] for row in status_rows}

    # Top 5 restoran (buyurtmalar soni bo'yicha)
    top_rows = (await db.execute(
        select(Restaurant.id, Restaurant.name, func.count(Order.id).label("order_count"))
        .join(Order, Order.restaurant_id == Restaurant.id, isouter=True)
        .group_by(Restaurant.id, Restaurant.name)
        .order_by(func.count(Order.id).desc())
        .limit(5)
    )).all()
    top_restaurants = [{"id": r[0], "name": r[1], "order_count": r[2]} for r in top_rows]

    # Tracking sahifasi tashriflari
    total_visits = (await db.execute(select(func.count(TrackingPageVisit.id)))).scalar()
    unique_visitors = (await db.execute(select(func.count(func.distinct(TrackingPageVisit.ip_address))))).scalar()
    today_visits = (await db.execute(
        select(func.count(TrackingPageVisit.id)).where(
            func.date(TrackingPageVisit.visited_at) == func.current_date()
        )
    )).scalar()

    return StatsResponse(
        total_users=total_users,
        total_restaurants=total_restaurants,
        total_orders=total_orders,
        total_delivered=total_delivered,
        total_revenue=float(total_revenue),
        orders_by_status=orders_by_status,
        top_restaurants=top_restaurants,
        total_tracking_visits=total_visits,
        unique_visitors=unique_visitors,
        today_visits=today_visits,
    )

# ── Foydalanuvchilar ──────────────────────────────────

@router.get("/users", response_model=list[UserOut])
async def list_users(
    role: UserRole | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = select(User)
    if role:
        query = query.where(User.role == role)
    result = await db.execute(query.order_by(User.created_at.desc()))
    return result.scalars().all()

@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: int, data: AdminUserUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.role is not None:
        user.role = data.role
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    await db.delete(user)
    await db.commit()
    return {"ok": True}

# ── Restoranlar ───────────────────────────────────────

@router.get("/restaurants", response_model=list[RestaurantOut])
async def list_all_restaurants(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(Restaurant).order_by(Restaurant.created_at.desc()))
    return result.scalars().all()

@router.patch("/restaurants/{restaurant_id}", response_model=RestaurantOut)
async def update_restaurant(restaurant_id: int, data: AdminRestaurantUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restoran topilmadi")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(restaurant, k, v)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant

@router.delete("/restaurants/{restaurant_id}")
async def delete_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restoran topilmadi")
    await db.delete(restaurant)
    await db.commit()
    return {"ok": True}

# ── Buyurtmalar ───────────────────────────────────────

@router.get("/orders")
async def list_all_orders(
    status: OrderStatus | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    result = await db.execute(query.order_by(Order.created_at.desc()))
    orders = result.scalars().all()
    return [
        {
            "id": o.id,
            "customer_id": o.customer_id,
            "restaurant_id": o.restaurant_id,
            "courier_id": o.courier_id,
            "status": o.status,
            "total_price": o.total_price,
            "delivery_address": o.delivery_address,
            "created_at": o.created_at,
        }
        for o in orders
    ]

@router.delete("/orders/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    await db.delete(order)
    await db.commit()
    return {"ok": True}
