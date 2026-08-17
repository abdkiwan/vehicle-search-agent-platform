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
from app.schemas.security import (
    AuthenticatedPrincipal,
)
from app.security.prompt_security import (
    PromptInjectionService,
)


class VehicleSearchWorkflow:
    def __init__(
        self,
        *,
        session: AsyncSession,
        principal: AuthenticatedPrincipal,
    ) -> None:

        self._context = AgentRuntimeContext(
            session=session,
            principal=principal,

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

            prompt_security=(
                PromptInjectionService()
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

            plan=result.get(
                "plan"
            ),

            structured_results=result.get(
                "structured_results"
            ),

            document_results=result.get(
                "document_results"
            ),

            context=result.get(
                "context"
            ),

            input_security=result.get(
                "input_security"
            ),

            context_security=result.get(
                "context_security"
            ),

            answer=result.get(
                "final_answer"
            ),
        )