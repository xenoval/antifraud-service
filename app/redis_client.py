import redis
import json
import hashlib
from app.config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )
    
    def get_cached_result(self, key: str):
        cached = self.client.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def set_cached_result(self, key: str, value: dict, ttl: int = None):
        if ttl is None:
            ttl = settings.cache_ttl

        self.client.setex(key, ttl, json.dumps(value))
    
    def generate_key(self, request_data: dict) -> str:
        data_str = json.dumps(request_data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        hash_hex = hash_obj.hexdigest()
        return f"antifraud:{hash_hex}"


# Создай глобальный экземпляр
redis_client = RedisClient()