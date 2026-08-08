from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.vehicles import router as vehicles_router
from app.api.routes.documents import router as documents_router
from app.api.routes.search import router as search_router
from app.config import settings
from app.db import engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(vehicles_router)
app.include_router(documents_router)
app.include_router(search_router)
