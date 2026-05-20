import os
os.environ["TESTING"] = "true"

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.database import Base, get_db
from main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_db():
    async with TestSession() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest_asyncio.fixture
async def customer_token(client):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Test Mijoz", "phone": "+998901111111",
        "password": "test1234", "role": "customer"
    })
    r = await client.post("/api/v1/auth/login", json={"phone": "+998901111111", "password": "test1234"})
    return r.json()["access_token"]

@pytest_asyncio.fixture
async def courier_token(client):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Test Kuryer", "phone": "+998902222222",
        "password": "test1234", "role": "courier"
    })
    r = await client.post("/api/v1/auth/login", json={"phone": "+998902222222", "password": "test1234"})
    return r.json()["access_token"]

@pytest_asyncio.fixture
async def restaurant_token(client):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Test Restoran", "phone": "+998903333333",
        "password": "test1234", "role": "restaurant"
    })
    r = await client.post("/api/v1/auth/login", json={"phone": "+998903333333", "password": "test1234"})
    return r.json()["access_token"]

@pytest_asyncio.fixture
async def admin_token(client):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Admin", "phone": "+998900000000",
        "password": "admin1234", "role": "admin"
    })
    r = await client.post("/api/v1/auth/login", json={"phone": "+998900000000", "password": "admin1234"})
    return r.json()["access_token"]

@pytest_asyncio.fixture
async def restaurant_id(client, restaurant_token):
    r = await client.post("/api/v1/restaurants/", json={
        "name": "Test Restoran", "address": "Toshkent",
        "lat": 41.2995, "lon": 69.2401,
        "open_time": "00:00", "close_time": "23:59",
        "delivery_fee": 5000, "min_order_price": 0
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    return r.json()["id"]

@pytest_asyncio.fixture
async def menu_item_id(client, restaurant_token, restaurant_id):
    r = await client.post(f"/api/v1/restaurants/{restaurant_id}/menu", json={
        "name": "Osh", "price": 25000, "calories": 500, "temperature_sensitive": True
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    return r.json()["id"]
