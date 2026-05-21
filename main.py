from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.api.v1.endpoints.tracking import router as tracking_router

import app.models.user
import app.models.restaurant
import app.models.order
import app.models.building
import app.models.delivery
import app.models.support
import app.models.api_key
import app.models.visitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Birinchi admin yaratish
    await _create_default_admin()
    yield

async def _create_default_admin():
    from app.core.config import settings
    from app.core.security import hash_password
    from app.models.user import User, UserRole
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal

    if not settings.ADMIN_PHONE or not settings.ADMIN_PASSWORD:
        return

    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.role == UserRole.admin))
        if existing.scalar_one_or_none():
            return  # Admin allaqachon bor

        admin = User(
            full_name="Admin",
            phone=settings.ADMIN_PHONE,
            email=settings.ADMIN_EMAIL or None,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        db.add(admin)
        await db.commit()
        print(f"✓ Admin yaratildi: {settings.ADMIN_PHONE}")

app = FastAPI(
    title="PinPoint API",
    description="Kuryer yetkazib berish tizimi — AI tahlil, real-time tracking, 2.5D navigatsiya",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router)
app.include_router(tracking_router)  # /track/{token} — HTML sahifa

@app.get("/")
async def root():
    return {"message": "PinPoint API ishlamoqda 🚀"}
