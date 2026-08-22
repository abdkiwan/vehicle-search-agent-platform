from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request

import logging
from time import perf_counter
from uuid import uuid4

from app.api.routes.health import router as health_router
from app.api.routes.vehicles import router as vehicles_router
from app.api.routes.documents import router as documents_router
from app.api.routes.search import router as search_router
from app.api.routes.auth import router as auth_router
from app.config import settings
from app.db import engine
from app.observability.logging import (
    configure_logging,
)
from app.observability.context import (
    reset_request_id,
    set_request_id,
)

configure_logging()

logger = logging.getLogger(
    __name__
)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    lifespan=lifespan,
)

@app.middleware("http")
async def request_observability(
    request: Request,
    call_next,
):
    request_id = str(
        uuid4()
    )

    token = set_request_id(
        request_id
    )

    started = perf_counter()

    status_code = 500

    try:
        response = await call_next(
            request
        )

        status_code = (
            response.status_code
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        return response

    except Exception:
        logger.exception(
            "http_request_failed",
            extra={
                "event_data": {
                    "method": (
                        request.method
                    ),
                    "path": (
                        request.url.path
                    ),
                }
            },
        )

        raise

    finally:
        latency_ms = (
            perf_counter()
            - started
        ) * 1000

        logger.info(
            "http_request_complete",
            extra={
                "event_data": {
                    "method": (
                        request.method
                    ),
                    "path": (
                        request.url.path
                    ),
                    "status_code": (
                        status_code
                    ),
                    "latency_ms": round(
                        latency_ms,
                        2,
                    ),
                }
            },
        )

        reset_request_id(
            token
        )

app.include_router(health_router)
app.include_router(vehicles_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(auth_router)
