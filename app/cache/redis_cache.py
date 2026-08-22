import hashlib
import json
import logging
from functools import lru_cache
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import settings
from app.observability.telemetry import (
    RunTelemetry,
)


logger = logging.getLogger(
    __name__
)


class RedisCache:
    """
    Small fail-open cache abstraction.

    Cache failures must never make the vehicle
    search API unavailable.
    """

    def __init__(
        self,
        *,
        url: str,
        enabled: bool,
    ) -> None:
        self._enabled = enabled

        self._client = Redis.from_url(
            url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=(
                settings
                .redis_socket_timeout_seconds
            ),
            socket_timeout=(
                settings
                .redis_socket_timeout_seconds
            ),
            health_check_interval=30,
        )

    @staticmethod
    def build_key(
        namespace: str,
        payload: Any,
        *,
        version: str,
    ) -> str:
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

        digest = hashlib.sha256(
            canonical.encode(
                "utf-8"
            )
        ).hexdigest()

        return (
            f"vehicle-search:"
            f"{version}:"
            f"{namespace}:"
            f"{digest}"
        )

    async def get_json(
        self,
        key: str,
        *,
        telemetry:
            RunTelemetry | None = None,
    ) -> Any | None:

        if not self._enabled:
            return None

        try:
            value = await self._client.get(
                key
            )

            if value is None:
                if telemetry:
                    telemetry.record_cache_miss()

                return None

            try:
                parsed = json.loads(
                    value
                )
            except json.JSONDecodeError:
                if telemetry:
                    telemetry.record_cache_error()

                await self._client.delete(
                    key
                )

                logger.warning(
                    "invalid_cache_payload",
                )

                return None

            if telemetry:
                telemetry.record_cache_hit()

            return parsed

        except RedisError:
            if telemetry:
                telemetry.record_cache_error()

            logger.warning(
                "redis_get_failed",
                exc_info=True,
            )

            return None

    async def set_json(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int,
        telemetry:
            RunTelemetry | None = None,
    ) -> None:

        if not self._enabled:
            return

        try:
            payload = json.dumps(
                value,
                separators=(",", ":"),
                default=str,
            )

            await self._client.set(
                key,
                payload,
                ex=ttl_seconds,
            )

        except RedisError:
            if telemetry:
                telemetry.record_cache_error()

            logger.warning(
                "redis_set_failed",
                exc_info=True,
            )

    async def ping(
        self,
    ) -> bool:

        if not self._enabled:
            return False

        try:
            return bool(
                await self._client.ping()
            )

        except RedisError:
            return False

    async def close(
        self,
    ) -> None:
        await self._client.aclose()


@lru_cache
def get_redis_cache() -> RedisCache:
    return RedisCache(
        url=settings.redis_url,
        enabled=settings.cache_enabled,
    )