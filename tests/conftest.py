import json

import pytest

import app.logic as logic


class FakeRedis:
    def __init__(self):
        self.store = {}

    def generate_key(self, data):
        return json.dumps(data, sort_keys=True)

    def get_cached_result(self, key):
        return self.store.get(key)

    def set_cached_result(self, key, value, ttl=None):
        self.store[key] = value


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    monkeypatch.setattr(logic, "redis_client", FakeRedis())
