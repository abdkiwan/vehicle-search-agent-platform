from app.cache.redis_cache import (
    RedisCache,
)


def test_cache_key_is_deterministic():
    payload = {
        "query": (
            "Find Volkswagen Golf"
        ),
        "model": "test-model",
    }

    key_1 = RedisCache.build_key(
        "planner",
        payload,
        version="v1",
    )

    key_2 = RedisCache.build_key(
        "planner",
        payload,
        version="v1",
    )

    assert key_1 == key_2


def test_payload_change_changes_key():
    key_1 = RedisCache.build_key(
        "planner",
        {
            "query": "Volkswagen Golf"
        },
        version="v1",
    )

    key_2 = RedisCache.build_key(
        "planner",
        {
            "query": "BMW 320"
        },
        version="v1",
    )

    assert key_1 != key_2


def test_version_change_invalidates_key():
    payload = {
        "query": "Volkswagen Golf"
    }

    key_v1 = RedisCache.build_key(
        "planner",
        payload,
        version="v1",
    )

    key_v2 = RedisCache.build_key(
        "planner",
        payload,
        version="v2",
    )

    assert key_v1 != key_v2