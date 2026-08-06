import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.vehicle_search import (
    VehicleSearchRequest,
    VehicleSearchResponse,
)
from app.services.vehicle_search import VehicleSearchService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/vehicles",
    tags=["vehicles"],
)


@router.post(
    "/search",
    response_model=VehicleSearchResponse,
)
async def search_vehicles(
    request: VehicleSearchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> VehicleSearchResponse:
    service = VehicleSearchService(
        VehicleRepository(session)
    )

    try:
        return await service.search(request)
    except SQLAlchemyError as exc:
        logger.exception("Structured vehicle search failed")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vehicle search is temporarily unavailable",
        ) from exc
