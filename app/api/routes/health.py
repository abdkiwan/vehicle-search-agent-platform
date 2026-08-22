from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.cache.redis_cache import (
    get_redis_cache,
)

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc

    return {"status": "ready"}


@router.get("/health/cache")
async def cache_health():
    cache = get_redis_cache()

    healthy = await cache.ping()

    return {
        "status": (
            "healthy"
            if healthy
            else "unavailable"
        )
    }
