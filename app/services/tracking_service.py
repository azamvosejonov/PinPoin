import redis.asyncio as aioredis
import json
from app.core.config import settings

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

async def update_courier_location(courier_id: int, lat: float, lon: float):
    data = json.dumps({"lat": lat, "lon": lon})
    await redis_client.setex(f"courier:{courier_id}:location", 300, data)

async def get_courier_location(courier_id: int) -> dict | None:
    data = await redis_client.get(f"courier:{courier_id}:location")
    return json.loads(data) if data else None

async def get_all_available_couriers() -> list[dict]:
    keys = await redis_client.keys("courier:*:location")
    couriers = []
    for key in keys:
        data = await redis_client.get(key)
        if data:
            courier_id = int(key.split(":")[1])
            loc = json.loads(data)
            couriers.append({"courier_id": courier_id, **loc})
    return couriers

async def set_order_tracking(order_id: int, data: dict):
    await redis_client.setex(f"order:{order_id}:tracking", 3600, json.dumps(data))

async def get_order_tracking(order_id: int) -> dict | None:
    data = await redis_client.get(f"order:{order_id}:tracking")
    return json.loads(data) if data else None
