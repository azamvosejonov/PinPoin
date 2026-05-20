from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant, MenuItem
from app.schemas.schemas import RestaurantCreate, RestaurantOut, MenuItemCreate, MenuItemOut

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

@router.post("/", response_model=RestaurantOut, status_code=201)
async def create_restaurant(data: RestaurantCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role not in (UserRole.restaurant, UserRole.company):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    r = Restaurant(**data.model_dump(), owner_id=user.id)
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r

@router.get("/", response_model=list[RestaurantOut])
async def list_restaurants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Restaurant).where(Restaurant.is_active == True))
    return result.scalars().all()

@router.get("/{restaurant_id}/menu", response_model=list[MenuItemOut])
async def get_menu(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem).where(MenuItem.restaurant_id == restaurant_id, MenuItem.is_available == True))
    return result.scalars().all()

@router.post("/{restaurant_id}/menu", response_model=MenuItemOut, status_code=201)
async def add_menu_item(restaurant_id: int, data: MenuItemCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id, Restaurant.owner_id == user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Bu restoran sizniki emas")
    item = MenuItem(**data.model_dump(), restaurant_id=restaurant_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
