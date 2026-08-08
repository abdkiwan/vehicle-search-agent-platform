import logging

from botocore.exceptions import ClientError
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.agent.workflow import (
    VehicleSearchWorkflow,
)
from app.api.dependencies import (
    get_current_role,
)
from app.db import get_db_session
from app.schemas.document_search import UserRole
from app.schemas.query_plan import (
    NaturalLanguageSearchRequest,
    QueryPlan,
    UnifiedSearchResponse,
)
from app.services.query_planner import (
    QueryPlannerService,
    QueryPlanningError,
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
    """
    Diagnostic endpoint exposing only query planning.
    """

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
    """
    Execute the LangGraph retrieval workflow.
    """

    workflow = VehicleSearchWorkflow(
        session=session,
        role=role,
    )

    try:
        return await workflow.execute(
            request.query
        )

    except QueryPlanningError as exc:
        logger.exception(
            "Query planning failed"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Search planning is temporarily "
                "unavailable"
            ),
        ) from exc

    except ClientError as exc:
        logger.exception(
            "AWS service call failed"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Search is temporarily unavailable"
            ),
        ) from exc

    except SQLAlchemyError as exc:
        logger.exception(
            "Database operation failed"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Search is temporarily unavailable"
            ),
        ) from exc