from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.core.security import get_current_user, encrypt, decrypt
from app.models.user import User, UserRole
from app.models.building import Building, ApartmentAccess
from app.schemas.schemas import BuildingCreate, BuildingOut, ApartmentAccessCreate, ApartmentAccessOut

router = APIRouter(prefix="/buildings", tags=["Buildings"])

@router.post("/", response_model=BuildingOut, status_code=201)
async def create_building(data: BuildingCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role not in (UserRole.company, UserRole.restaurant, UserRole.admin):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    building = Building(**data.model_dump())
    db.add(building)
    await db.commit()
    await db.refresh(building)
    return building

@router.get("/", response_model=list[BuildingOut])
async def list_buildings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Building))
    return result.scalars().all()

@router.post("/apartment-access", status_code=201)
async def save_apartment_access(data: ApartmentAccessCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    existing = await db.execute(
        select(ApartmentAccess).where(
            and_(
                ApartmentAccess.customer_id == user.id,
                ApartmentAccess.building_id == data.building_id,
                ApartmentAccess.apartment_number == data.apartment_number,
            )
        )
    )
    access = existing.scalar_one_or_none()

    encrypted_code = encrypt(data.door_code) if data.door_code else None

    if access:
        access.floor = data.floor
        access.door_code_encrypted = encrypted_code
        access.position = data.position
    else:
        access = ApartmentAccess(
            customer_id=user.id,
            building_id=data.building_id,
            apartment_number=data.apartment_number,
            floor=data.floor,
            door_code_encrypted=encrypted_code,
            position=data.position,
        )
        db.add(access)

    await db.commit()
    await db.refresh(access)

    return {
        "id": access.id,
        "building_id": access.building_id,
        "apartment_number": access.apartment_number,
        "floor": access.floor,
        "has_door_code": access.door_code_encrypted is not None,
    }

@router.get("/apartment-access/{building_id}")
async def get_my_apartment_access(building_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(ApartmentAccess).where(
            ApartmentAccess.customer_id == user.id,
            ApartmentAccess.building_id == building_id,
        )
    )
    accesses = result.scalars().all()
    return [
        {
            "id": a.id,
            "apartment_number": a.apartment_number,
            "floor": a.floor,
            "door_code": decrypt(a.door_code_encrypted) if a.door_code_encrypted else None,
            "position": a.position,
        }
        for a in accesses
    ]
