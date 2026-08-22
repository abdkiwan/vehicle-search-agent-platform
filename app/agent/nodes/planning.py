from langgraph.runtime import Runtime

from app.agent.context import AgentRuntimeContext
from app.agent.state import AgentState
from app.observability.nodes import (
    observed_stage,
)


@observed_stage("plan_query")
async def plan_query(
    state: AgentState,
    runtime: Runtime[AgentRuntimeContext],
) -> dict:
    """
    Convert the natural-language request into a validated QueryPlan.
    """

    query = state["query"]

    plan = await runtime.context.query_planner.plan(
        query
    )

    return {
        "plan": plan,
    }