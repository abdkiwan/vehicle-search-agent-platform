from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.context import (
    AgentRuntimeContext,
)
from app.agent.graph import (
    vehicle_search_graph,
)
from app.retrieval.embeddings import (
    BedrockEmbeddingService,
)
from app.schemas.document_search import (
    UserRole,
)
from app.schemas.query_plan import (
    UnifiedSearchResponse,
)
from app.services.query_planner import (
    QueryPlannerService,
)
from app.services.answer_generator import (
    GroundedAnswerService,
)
from app.services.answer_validator import (
    AnswerValidationService,
)


class VehicleSearchWorkflow:
    def __init__(
        self,
        *,
        session: AsyncSession,
        role: UserRole,
    ) -> None:
        self._context = AgentRuntimeContext(
            session=session,
            role=role,
            query_planner=(
                QueryPlannerService()
            ),
            embeddings=(
                BedrockEmbeddingService()
            ),
            answer_generator=(
                GroundedAnswerService()
            ),
            answer_validator=(
                AnswerValidationService()
            ),
        )

    async def execute(
        self,
        query: str,
    ) -> UnifiedSearchResponse:
        result = (
            await vehicle_search_graph.ainvoke(
                {
                    "query": query,
                },
                context=self._context,
            )
        )

        return UnifiedSearchResponse(
            query=query,
            plan=result["plan"],
            structured_results=result.get(
                "structured_results"
            ),
            document_results=result.get(
                "document_results"
            ),
            context=result.get(
                "context"
            ),
            answer=result.get(
                "final_answer"
            )
        )