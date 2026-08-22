from langgraph.runtime import Runtime

from app.agent.context import AgentRuntimeContext
from app.agent.state import AgentState
from app.repositories.vehicle_repository import (
    VehicleRepository,
)
from app.services.vehicle_search import (
    VehicleSearchService,
)
from app.observability.nodes import (
    observed_stage,
)


@observed_stage("structured_search")
async def structured_search(
    state: AgentState,
    runtime: Runtime[AgentRuntimeContext],
) -> dict:
    """
    Execute deterministic structured vehicle search.
    """

    plan = state["plan"]

    if plan.vehicle_search is None:
        raise ValueError(
            "Structured search requested without "
            "a VehicleSearchRequest."
        )

    repository = VehicleRepository(
        runtime.context.session
    )

    service = VehicleSearchService(
        repository
    )

    results = await service.search(
        plan.vehicle_search
    )

    return {
        "structured_results": results,
    }