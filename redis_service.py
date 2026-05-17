import redis
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for caching and geofencing"""
    
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        try:
            self.redis_client = redis.Redis(
                host='redis',
                port=6379,
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using fallback mode.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        return self.redis_client is not None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set key with TTL"""
        if self.is_available():
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get key value"""
        if self.is_available():
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        return None
    
    def delete(self, key: str):
        """Delete key"""
        if self.is_available():
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        return False
    
    def cache_nearby_buildings(self, courier_id: str, buildings: list, ttl: int = 300):
        """Cache nearby buildings for courier"""
        key = f"nearby_buildings:{courier_id}"
        return self.set(key, buildings, ttl)
    
    def get_nearby_buildings(self, courier_id: str) -> Optional[list]:
        """Get cached nearby buildings"""
        key = f"nearby_buildings:{courier_id}"
        return self.get(key)
    
    def cache_domofon_codes(self, building_id: str, codes: list, ttl: int = 600):
        """Cache domofon codes for building"""
        key = f"domofon_codes:{building_id}"
        return self.set(key, codes, ttl)
    
    def get_domofon_codes(self, building_id: str) -> Optional[list]:
        """Get cached domofon codes"""
        key = f"domofon_codes:{building_id}"
        return self.get(key)
    
    def update_courier_location(self, courier_id: str, location: dict, ttl: int = 10):
        """Update courier location in Redis (10s TTL)"""
        key = f"courier_location:{courier_id}"
        return self.set(key, location, ttl)
    
    def get_courier_location(self, courier_id: str) -> Optional[dict]:
        """Get courier location from cache"""
        key = f"courier_location:{courier_id}"
        return self.get(key)
    
    def get_all_courier_locations(self) -> Dict[str, dict]:
        """Get all courier locations"""
        locations = {}
        if self.is_available():
            try:
                keys = self.redis_client.keys("courier_location:*")
                for key in keys:
                    courier_id = key.split(":")[1]
                    location = self.get(key)
                    if location:
                        locations[courier_id] = location
            except Exception as e:
                logger.error(f"Redis get all locations error: {e}")
        return locations


redis_service = RedisService()
