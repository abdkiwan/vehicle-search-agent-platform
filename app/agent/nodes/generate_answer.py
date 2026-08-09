from langgraph.runtime import Runtime

from app.agent.context import (
    AgentRuntimeContext,
)
from app.agent.state import AgentState


async def generate_answer(
    state: AgentState,
    runtime: Runtime[AgentRuntimeContext],
) -> dict:

    generated = (
        await runtime.context
        .answer_generator.generate(
            query=state["query"],
            route=state["plan"].route,
            context=state["context"],
        )
    )

    return {
        "generated_answer": generated,
    }