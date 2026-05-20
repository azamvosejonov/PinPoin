import random
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.core.security import hash_password, get_current_user
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant, RestaurantCourier
from app.schemas.schemas import StaffCreate
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/staff", tags=["Staff"])

class AssignCourierSchema(BaseModel):
    courier_id: int
    restaurant_ids: list[int]  # bo'sh list = barcha restoranlardan ajratish

def _generate_password(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

async def _require_owner(user: User):
    if user.role not in (UserRole.restaurant, UserRole.company):
        raise HTTPException(status_code=403, detail="Faqat restoran yoki kompaniya uchun")

async def _get_my_restaurant_ids(user_id: int, db: AsyncSession) -> list[int]:
    result = await db.execute(select(Restaurant.id).where(Restaurant.owner_id == user_id))
    return [r[0] for r in result.all()]

async def _get_my_courier(courier_id: int, user_id: int, db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where(User.id == courier_id, User.created_by == user_id)
    )
    courier = result.scalar_one_or_none()
    if not courier:
        raise HTTPException(status_code=404, detail="Kuryer topilmadi yoki sizga tegishli emas")
    return courier

# ── Kuryer qo'shish ───────────────────────────────────

@router.post("/couriers", status_code=201)
async def add_courier(data: StaffCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _require_owner(user)

    existing = await db.execute(select(User).where(User.phone == data.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan")

    plain_password = _generate_password()
    courier = User(
        full_name=data.full_name,
        phone=data.phone,
        hashed_password=hash_password(plain_password),
        role=UserRole.courier,
        vehicle_type=data.vehicle_type,
        created_by=user.id,
    )
    db.add(courier)
    await db.commit()
    await db.refresh(courier)

    return {
        "id": courier.id,
        "full_name": courier.full_name,
        "phone": courier.phone,
        "role": courier.role,
        "vehicle_type": courier.vehicle_type,
        "plain_password": plain_password,
    }

# ── O'z kuryerlari ro'yxati ───────────────────────────

@router.get("/couriers")
async def my_couriers(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _require_owner(user)

    result = await db.execute(
        select(User).where(User.created_by == user.id, User.role == UserRole.courier)
    )
    couriers = result.scalars().all()

    # Har bir kuryer qaysi restoranlarga biriktirilganini ham qaytaramiz
    output = []
    for c in couriers:
        rc_result = await db.execute(
            select(RestaurantCourier.restaurant_id).where(RestaurantCourier.courier_id == c.id)
        )
        assigned_restaurant_ids = [r[0] for r in rc_result.all()]
        output.append({
            "id": c.id,
            "full_name": c.full_name,
            "phone": c.phone,
            "vehicle_type": c.vehicle_type,
            "is_active": c.is_active,
            "is_available": c.is_available,
            "assigned_restaurants": assigned_restaurant_ids,
        })
    return output

# ── Kuryerni restoran(lar)ga biriktirish ──────────────

@router.post("/couriers/assign")
async def assign_courier_to_restaurants(
    data: AssignCourierSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    courier_id + restaurant_ids → kuryerni tanlangan restoranlarga biriktiradi.
    restaurant_ids bo'sh bo'lsa — barcha restoranlardan ajratadi.
    """
    await _require_owner(user)
    courier = await _get_my_courier(data.courier_id, user.id, db)

    my_restaurant_ids = await _get_my_restaurant_ids(user.id, db)

    # Faqat o'ziga tegishli restoranlarni tekshirish
    invalid = set(data.restaurant_ids) - set(my_restaurant_ids)
    if invalid:
        raise HTTPException(status_code=403, detail=f"Bu restoranlar sizga tegishli emas: {list(invalid)}")

    # Avvalgi barcha biriktirmalarni o'chirish (faqat o'z restoranlari uchun)
    existing = await db.execute(
        select(RestaurantCourier).where(
            RestaurantCourier.courier_id == courier.id,
            RestaurantCourier.restaurant_id.in_(my_restaurant_ids),
        )
    )
    for rc in existing.scalars().all():
        await db.delete(rc)

    # Yangi biriktirmalar
    for rid in data.restaurant_ids:
        db.add(RestaurantCourier(restaurant_id=rid, courier_id=courier.id))

    await db.commit()
    return {
        "courier_id": courier.id,
        "assigned_restaurants": data.restaurant_ids,
    }

# ── Restoran bo'yicha kuryerlar ───────────────────────

@router.get("/restaurants/{restaurant_id}/couriers")
async def restaurant_couriers(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Bitta restoranning barcha biriktirilgan kuryerlari"""
    await _require_owner(user)

    # Restoran o'ziga tegishliligini tekshirish
    r_result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id, Restaurant.owner_id == user.id)
    )
    if not r_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Bu restoran sizga tegishli emas")

    result = await db.execute(
        select(User)
        .join(RestaurantCourier, RestaurantCourier.courier_id == User.id)
        .where(RestaurantCourier.restaurant_id == restaurant_id)
    )
    couriers = result.scalars().all()
    return [
        {
            "id": c.id,
            "full_name": c.full_name,
            "phone": c.phone,
            "vehicle_type": c.vehicle_type,
            "is_active": c.is_active,
            "is_available": c.is_available,
        }
        for c in couriers
    ]

# ── Barcha restoranlar va ularning kuryerlari ─────────

@router.get("/overview")
async def my_overview(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Barcha restoranlar va ularga biriktirilgan kuryerlar — umumiy ko'rinish"""
    await _require_owner(user)

    r_result = await db.execute(select(Restaurant).where(Restaurant.owner_id == user.id))
    restaurants = r_result.scalars().all()

    output = []
    for r in restaurants:
        rc_result = await db.execute(
            select(User)
            .join(RestaurantCourier, RestaurantCourier.courier_id == User.id)
            .where(RestaurantCourier.restaurant_id == r.id)
        )
        couriers = rc_result.scalars().all()
        output.append({
            "restaurant_id": r.id,
            "restaurant_name": r.name,
            "is_active": r.is_active,
            "couriers": [
                {
                    "id": c.id,
                    "full_name": c.full_name,
                    "phone": c.phone,
                    "is_available": c.is_available,
                }
                for c in couriers
            ],
        })

    # Hech qaysi restoranga biriktirilmagan kuryerlar
    all_courier_ids_result = await db.execute(
        select(User.id).where(User.created_by == user.id, User.role == UserRole.courier)
    )
    all_ids = {r[0] for r in all_courier_ids_result.all()}

    assigned_ids_result = await db.execute(
        select(RestaurantCourier.courier_id).where(
            RestaurantCourier.restaurant_id.in_([r["restaurant_id"] for r in output])
        )
    )
    assigned_ids = {r[0] for r in assigned_ids_result.all()}
    unassigned_ids = all_ids - assigned_ids

    unassigned = []
    for uid in unassigned_ids:
        u_result = await db.execute(select(User).where(User.id == uid))
        u = u_result.scalar_one_or_none()
        if u:
            unassigned.append({"id": u.id, "full_name": u.full_name, "phone": u.phone})

    return {"restaurants": output, "unassigned_couriers": unassigned}

# ── Parol yangilash ───────────────────────────────────

@router.patch("/couriers/{courier_id}/reset-password")
async def reset_courier_password(courier_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _require_owner(user)
    courier = await _get_my_courier(courier_id, user.id, db)
    plain_password = _generate_password()
    courier.hashed_password = hash_password(plain_password)
    await db.commit()
    return {"phone": courier.phone, "new_password": plain_password}

# ── Bloklash / faollashtirish ─────────────────────────

@router.patch("/couriers/{courier_id}/toggle")
async def toggle_courier(courier_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _require_owner(user)
    courier = await _get_my_courier(courier_id, user.id, db)
    courier.is_active = not courier.is_active
    await db.commit()
    return {"id": courier_id, "is_active": courier.is_active}

# ── O'chirish ─────────────────────────────────────────

@router.delete("/couriers/{courier_id}")
async def delete_courier(courier_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _require_owner(user)
    courier = await _get_my_courier(courier_id, user.id, db)
    await db.delete(courier)
    await db.commit()
    return {"ok": True}
