from app.agent.routing import (
    route_after_planning,
    route_after_structured_search,
)
from app.schemas.query_plan import (
    DocumentScope,
    QueryPlan,
    SearchRoute,
)


def make_plan(
    route: SearchRoute,
) -> QueryPlan:
    return QueryPlan(
        route=route,
        vehicle_search=None,
        document_search=None,
        document_scope=(
            DocumentScope.GLOBAL
        ),
        routing_reason="test",
    )


def test_structured_route_starts_vehicle_search():
    state = {
        "query": "test",
        "plan": make_plan(
            SearchRoute.STRUCTURED
        ),
    }

    assert (
        route_after_planning(state)
        == "structured"
    )


def test_unstructured_route_starts_documents():
    state = {
        "query": "test",
        "plan": make_plan(
            SearchRoute.UNSTRUCTURED
        ),
    }

    assert (
        route_after_planning(state)
        == "documents"
    )


def test_hybrid_route_starts_structured_search():
    state = {
        "query": "test",
        "plan": make_plan(
            SearchRoute.HYBRID
        ),
    }

    assert (
        route_after_planning(state)
        == "structured"
    )


def test_unsupported_route_stops():
    state = {
        "query": "test",
        "plan": make_plan(
            SearchRoute.UNSUPPORTED
        ),
    }

    assert (
        route_after_planning(state)
        == "unsupported"
    )


def test_hybrid_continues_to_documents():
    state = {
        "query": "test",
        "plan": make_plan(
            SearchRoute.HYBRID
        ),
    }

    assert (
        route_after_structured_search(
            state
        )
        == "documents"
    )


def test_structured_stops_after_vehicle_search():
    state = {
        "query": "test",
        "plan": make_plan(
            SearchRoute.STRUCTURED
        ),
    }

    assert (
        route_after_structured_search(
            state
        )
        == "end"
    )