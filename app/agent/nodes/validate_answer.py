from langgraph.runtime import Runtime

from app.agent.context import (
    AgentRuntimeContext,
)
from app.agent.state import AgentState


async def validate_answer(
    state: AgentState,
    runtime: Runtime[AgentRuntimeContext],
) -> dict:

    final_answer = (
        await runtime.context
        .answer_validator.finalize(
            query=state["query"],
            generated=(
                state["generated_answer"]
            ),
            context=state["context"],
        )
    )

    return {
        "final_answer": final_answer,
    }