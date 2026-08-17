import json
from datetime import datetime

from app.redis.redis_client import RedisClient


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CacheService:
    def __init__(self):
        self.client = RedisClient()

    def get(self, key: str):
        raw = self.client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return raw

    def set(self, key: str, value, ttl: int = 60):
        raw = json.dumps(value, cls=DateTimeEncoder)
        self.client.set(key, raw, ttl=ttl)

    def delete(self, key: str):
        self.client.delete(key)

    def clear_namespace(self, prefix: str):
        pattern = f"{prefix}*"
        keys = self.client.keys(pattern)
        for key in keys:
            self.client.delete(key)
