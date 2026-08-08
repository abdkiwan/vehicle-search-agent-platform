from typing import Literal

from app.agent.state import AgentState
from app.schemas.query_plan import SearchRoute


def route_after_planning(
    state: AgentState,
) -> Literal[
    "structured",
    "documents",
    "unsupported",
]:
    """
    Decide which retrieval branch should start
    after query planning.
    """

    route = state["plan"].route

    if route in {
        SearchRoute.STRUCTURED,
        SearchRoute.HYBRID,
    }:
        return "structured"

    if route == SearchRoute.UNSTRUCTURED:
        return "documents"

    return "unsupported"


def route_after_structured_search(
    state: AgentState,
) -> Literal[
    "documents",
    "context",
]:
    if (
        state["plan"].route
        == SearchRoute.HYBRID
    ):
        return "documents"

    return "context"