import logging

from botocore.exceptions import ClientError
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.api.dependencies import (
    get_current_role,
)
from app.db import get_db_session
from app.schemas.document_search import (
    UserRole,
)
from app.schemas.query_plan import (
    NaturalLanguageSearchRequest,
    QueryPlan,
    UnifiedSearchResponse,
)
from app.services.query_planner import (
    QueryPlannerService,
    QueryPlanningError,
)
from app.services.search_router import (
    SearchRouterService,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1/search",
    tags=["search"],
)


@router.post(
    "/plan",
    response_model=QueryPlan,
)
async def create_search_plan(
    request: NaturalLanguageSearchRequest,
) -> QueryPlan:
    planner = QueryPlannerService()

    try:
        return await planner.plan(
            request.query
        )

    except (
        ClientError,
        QueryPlanningError,
    ) as exc:
        logger.exception(
            "Query planning failed"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Query planning is temporarily "
                "unavailable"
            ),
        ) from exc


@router.post(
    "/retrieve",
    response_model=UnifiedSearchResponse,
)
async def retrieve(
    request: NaturalLanguageSearchRequest,
    role: UserRole = Depends(
        get_current_role
    ),
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> UnifiedSearchResponse:
    planner = QueryPlannerService()

    try:
        plan = await planner.plan(
            request.query
        )

        router_service = (
            SearchRouterService(session)
        )

        return await router_service.execute(
            original_query=request.query,
            plan=plan,
            role=role,
        )

    except (
        ClientError,
        QueryPlanningError,
    ) as exc:
        logger.exception(
            "Search planning failed"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Search is temporarily unavailable"
            ),
        ) from exc