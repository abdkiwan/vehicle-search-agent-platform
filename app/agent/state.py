from typing_extensions import TypedDict

from app.schemas.document_search import (
    DocumentSearchResponse,
)
from app.schemas.query_plan import QueryPlan
from app.schemas.vehicle_search import (
    VehicleSearchResponse,
)


class AgentState(TypedDict, total=False):
    """
    Mutable state for one vehicle-search workflow execution.

    Only values that evolve during workflow execution belong here.
    """

    query: str

    plan: QueryPlan

    structured_results: VehicleSearchResponse

    document_results: DocumentSearchResponse