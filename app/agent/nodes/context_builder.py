from langgraph.runtime import Runtime
from app.agent.context import (
    AgentRuntimeContext,
)
from app.agent.state import AgentState
from app.services.context_builder import (
    ContextBuilderService,
)
from app.observability.nodes import (
    observed_stage,
)


@observed_stage("build_context")
async def build_context(
    state: AgentState,
    runtime: Runtime[AgentRuntimeContext],
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