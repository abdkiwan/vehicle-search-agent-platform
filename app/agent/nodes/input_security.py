from langgraph.runtime import Runtime

from app.agent.context import (
    AgentRuntimeContext,
)
from app.agent.state import AgentState
from app.schemas.security import (
    PromptSecuritySource,
)


async def check_input_security(
    state: AgentState,
    runtime: Runtime[AgentRuntimeContext],
) -> dict:

    result = (
        await runtime.context
        .prompt_security.assess(
            text=state["query"],
            source=(
                PromptSecuritySource.USER_INPUT
            ),
        )
    )

    return {
        "input_security": result,
    }