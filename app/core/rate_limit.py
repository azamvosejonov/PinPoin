import os
from fastapi import Request, HTTPException

TESTING = os.getenv("TESTING", "false").lower() == "true"

async def rate_limit(request: Request):
    if TESTING:
        return
    from app.services.tracking_service import redis_client
    from app.core.config import settings
    ip = request.client.host
    key = f"rate:{ip}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)
    if count > settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Juda ko'p so'rov. 1 daqiqa kuting.")
