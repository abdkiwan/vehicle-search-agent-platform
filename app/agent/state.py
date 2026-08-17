from typing_extensions import TypedDict

from app.schemas.answer import (
    FinalAnswer,
    GeneratedAnswer,
)
from app.schemas.context import ContextPackage
from app.schemas.document_search import (
    DocumentSearchResponse,
)
from app.schemas.query_plan import QueryPlan
from app.schemas.vehicle_search import (
    VehicleSearchResponse,
)
from app.schemas.security import (
    PromptSecurityResult,
)


class AgentState(TypedDict, total=False):
    """
    Mutable state for one vehicle-search workflow execution.

    Only values that evolve during workflow execution belong here.
    """

    query: str

    input_security: PromptSecurityResult

    plan: QueryPlan

    structured_results: VehicleSearchResponse

    document_results: DocumentSearchResponse

    context: ContextPackage

    context_security: PromptSecurityResult

    generated_answer: GeneratedAnswer

    final_answer: FinalAnswer