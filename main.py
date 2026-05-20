from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
    yield

app = FastAPI(
    title="PinPoint API",
    description="Kuryer yetkazib berish tizimi — AI tahlil, real-time tracking, 2.5D navigatsiya",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router)
app.include_router(tracking_router)  # /track/{token} — HTML sahifa

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "PinPoint API ishlamoqda 🚀"}

@app.get("/guest")
async def guest_page():
    """Mehmon sahifasi - faslga qarab o'zgaruvchan dizayn"""
    return FileResponse("static/guest/index.html")
