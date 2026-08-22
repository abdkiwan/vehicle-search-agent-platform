from langgraph.runtime import Runtime

from app.agent.context import (
    AgentRuntimeContext,
)
from app.agent.state import AgentState
from app.schemas.security import (
    PromptSecurityResult,
    PromptSecuritySource,
)
from app.observability.nodes import (
    observed_stage,
)


@observed_stage("check_context_security")
async def check_context_security(
    state: AgentState,
    runtime: Runtime[AgentRuntimeContext],
) -> dict:

    document_results = state.get(
        "document_results"
    )

    # Structured database fields are produced
    # by our own deterministic application.
    # Prompt-attack assessment matters mainly
    # for retrieved free-text documents.
    if (
        document_results is None
        or not document_results.items
    ):
        return {
            "context_security":
                PromptSecurityResult(
                    allowed=True,
                    source=(
                        PromptSecuritySource
                        .RETRIEVED_CONTEXT
                    ),
                    action="SKIPPED",
                )
        }

    context = state["context"]

    result = (
        await runtime.context
        .prompt_security.assess(
            text=context.text,
            source=(
                PromptSecuritySource
                .RETRIEVED_CONTEXT
            ),
        )
    )

    return {
        "context_security": result,
    }