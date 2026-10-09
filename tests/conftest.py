import pytest

import app.logic as logic
from app.redis_client import RedisClient


class FakeRedisClient(RedisClient):
    def __init__(self):
        self.store: dict = {}

    def get_cached_result(self, key):
        return self.store.get(key)

    def set_cached_result(self, key, value, ttl=None):
        self.store[key] = value


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    fake = FakeRedisClient()
    monkeypatch.setattr(logic, "redis_client", fake)
    return fake
