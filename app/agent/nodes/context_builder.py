from app.agent.state import AgentState
from app.services.context_builder import (
    ContextBuilderService,
)


async def build_context(
    state: AgentState,
) -> dict:
    """
    Build deterministic, bounded context from
    retrieved evidence.
    """

    builder = ContextBuilderService()

    context = builder.build(
        structured_results=state.get(
            "structured_results"
        ),
        document_results=state.get(
            "document_results"
        ),
    )

    return {
        "context": context,
    }