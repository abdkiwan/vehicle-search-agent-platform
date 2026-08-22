from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.embeddings import (
    BedrockEmbeddingService,
)
from app.schemas.security import (
    AuthenticatedPrincipal,
)
from app.security.prompt_security import (
    PromptInjectionService,
)
from app.services.answer_generator import (
    GroundedAnswerService,
)
from app.services.answer_validator import (
    AnswerValidationService,
)
from app.services.query_planner import (
    QueryPlannerService,
)
from app.observability.telemetry import (
    RunTelemetry,
)


@dataclass(frozen=True)
class AgentRuntimeContext:
    session: AsyncSession

    principal: AuthenticatedPrincipal

    query_planner: QueryPlannerService

    embeddings: BedrockEmbeddingService

    answer_generator: GroundedAnswerService

    answer_validator: AnswerValidationService

    prompt_security: PromptInjectionService

    telemetry: RunTelemetry