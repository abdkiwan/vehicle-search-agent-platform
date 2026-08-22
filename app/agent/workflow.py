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
from app.cache.redis_cache import (
    get_redis_cache,
)
from app.observability.context import (
    get_request_id,
)
from app.observability.telemetry import (
    RunTelemetry,
)

import logging

logger = logging.getLogger(
    __name__
)

class VehicleSearchWorkflow:
    def __init__(
        self,
        *,
        session: AsyncSession,
        principal: AuthenticatedPrincipal,
    ) -> None:

        telemetry = RunTelemetry(
            request_id=get_request_id()
        )

        cache = get_redis_cache()

        self._telemetry = telemetry

        self._context = (
            AgentRuntimeContext(
                session=session,

                principal=principal,

                query_planner=(
                    QueryPlannerService(
                        cache=cache,
                        telemetry=telemetry,
                    )
                ),

                embeddings=(
                    BedrockEmbeddingService(
                        cache=cache,
                        telemetry=telemetry,
                    )
                ),

                answer_generator=(
                    GroundedAnswerService(
                        telemetry=telemetry
                    )
                ),

                answer_validator=(
                    AnswerValidationService()
                ),

                prompt_security=(
                    PromptInjectionService()
                ),

                telemetry=telemetry,
            )
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

        telemetry = (
            self._telemetry.snapshot()
        )

        logger.info(
            "agent_run_complete",
            extra={
                "event_data": {
                    "route": (
                        result.get("plan").route
                        if result.get("plan")
                        else None
                    ),
                    "answer_status": (
                        result.get(
                            "final_answer"
                        ).status
                        if result.get(
                            "final_answer"
                        )
                        else None
                    ),
                    "total_latency_ms": (
                        telemetry
                        .total_latency_ms
                    ),
                    "total_tokens": (
                        telemetry.total_tokens
                    ),
                    "estimated_cost_usd": (
                        telemetry
                        .estimated_cost_usd
                    ),
                    "cache_hits": (
                        telemetry.cache.hits
                    ),
                    "cache_misses": (
                        telemetry.cache.misses
                    ),
                    "cache_errors": (
                        telemetry.cache.errors
                    ),
                }
            },
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

            telemetry=telemetry,
        )