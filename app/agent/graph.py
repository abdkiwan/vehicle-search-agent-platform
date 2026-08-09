from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agent.context import AgentRuntimeContext
from app.agent.nodes.context_builder import (
    build_context,
)
from app.agent.nodes.document_search import (
    document_search,
)
from app.agent.nodes.planning import (
    plan_query,
)
from app.agent.nodes.structured_search import (
    structured_search,
)
from app.agent.nodes.generate_answer import (
    generate_answer,
)
from app.agent.nodes.validate_answer import (
    validate_answer,
)
from app.agent.routing import (
    route_after_planning,
    route_after_structured_search,
)
from app.agent.state import AgentState


def build_vehicle_search_graph():
    builder = StateGraph(
        state_schema=AgentState,
        context_schema=AgentRuntimeContext,
    )

    builder.add_node(
        "plan_query",
        plan_query,
    )

    builder.add_node(
        "structured_search",
        structured_search,
    )

    builder.add_node(
        "document_search",
        document_search,
    )

    builder.add_node(
        "build_context",
        build_context,
    )

    builder.add_node(
        "generate_answer",
        generate_answer,
    )

    builder.add_node(
        "validate_answer",
        validate_answer,
    )

    builder.add_edge(
        START,
        "plan_query",
    )

    builder.add_conditional_edges(
        "plan_query",
        route_after_planning,
        {
            "structured": (
                "structured_search"
            ),
            "documents": (
                "document_search"
            ),
            "unsupported": (
                "build_context"
            ),
        },
    )

    builder.add_conditional_edges(
        "structured_search",
        route_after_structured_search,
        {
            "documents": (
                "document_search"
            ),
            "context": (
                "build_context"
            ),
        },
    )

    builder.add_edge(
        "document_search",
        "build_context",
    )

    builder.add_edge(
        "build_context",
        "generate_answer",
    )

    builder.add_edge(
        "generate_answer",
        "validate_answer",
    )

    builder.add_edge(
        "validate_answer",
        END,
    )

    return builder.compile()


vehicle_search_graph = (
    build_vehicle_search_graph()
)