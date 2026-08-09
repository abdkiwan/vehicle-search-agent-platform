from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.embeddings import (
    BedrockEmbeddingService,
)
from app.schemas.document_search import UserRole
from app.services.answer_generator import (
    GroundedAnswerService,
)
from app.services.answer_validator import (
    AnswerValidationService,
)
from app.services.query_planner import (
    QueryPlannerService,
)


@dataclass(frozen=True)
class AgentRuntimeContext:
    """
    Immutable dependencies available during one graph execution.
    """

    session: AsyncSession
    
    role: UserRole

    query_planner: QueryPlannerService

    embeddings: BedrockEmbeddingService

    answer_generator: GroundedAnswerService

    answer_validator: AnswerValidationService