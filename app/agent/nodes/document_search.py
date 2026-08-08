from langgraph.runtime import Runtime

from app.agent.context import AgentRuntimeContext
from app.agent.state import AgentState
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.schemas.document_search import (
    DocumentSearchResponse,
)
from app.schemas.query_plan import (
    DocumentScope,
    SearchRoute,
)
from app.services.document_search import (
    DocumentSearchService,
)


async def document_search(
    state: AgentState,
    runtime: Runtime[AgentRuntimeContext],
) -> dict:
    """
    Execute authorization-aware hybrid document retrieval.

    For hybrid searches, structured results may constrain
    which dealer or vehicle documents can be retrieved.
    """

    plan = state["plan"]

    if plan.document_search is None:
        raise ValueError(
            "Document search requested without "
            "a DocumentSearchRequest."
        )

    request = plan.document_search

    if plan.route == SearchRoute.HYBRID:
        structured_results = state.get(
            "structured_results"
        )

        if structured_results is None:
            raise ValueError(
                "Hybrid document retrieval requires "
                "structured results first."
            )

        if (
            plan.document_scope
            == DocumentScope.MATCHED_DEALERS
        ):
            dealer_ids = list(
                {
                    item.dealer.id
                    for item
                    in structured_results.items
                }
            )

            if not dealer_ids:
                return {
                    "document_results":
                        DocumentSearchResponse(
                            query=request.query,
                            items=[],
                            returned=0,
                        )
                }

            request = request.model_copy(
                update={
                    "dealer_ids": dealer_ids,
                }
            )

        elif (
            plan.document_scope
            == DocumentScope.MATCHED_VEHICLES
        ):
            vehicle_ids = [
                item.id
                for item
                in structured_results.items
            ]

            if not vehicle_ids:
                return {
                    "document_results":
                        DocumentSearchResponse(
                            query=request.query,
                            items=[],
                            returned=0,
                        )
                }

            request = request.model_copy(
                update={
                    "vehicle_ids": vehicle_ids,
                }
            )

    repository = DocumentRepository(
        runtime.context.session
    )

    service = DocumentSearchService(
        repository=repository,
        embeddings=runtime.context.embeddings,
    )

    results = await service.search(
        request=request,
        role=runtime.context.role,
    )

    return {
        "document_results": results,
    }