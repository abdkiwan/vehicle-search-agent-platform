import pytest

from app.schemas.query_plan import (
    DocumentScope,
    SearchRoute,
)
from app.services.query_planner import (
    QueryPlannerService,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_structured_query_plan():
    planner = QueryPlannerService()

    plan = await planner.plan(
        "Find Volkswagen Golf cars "
        "under 20000 euros with less "
        "than 80000 km."
    )

    assert (
        plan.route
        == SearchRoute.STRUCTURED
    )

    assert (
        plan.vehicle_search.makes
        == ["Volkswagen"]
    )

    assert (
        plan.vehicle_search.models
        == ["Golf"]
    )

    assert (
        plan.vehicle_search.max_price_eur
        == 20000
    )

    assert (
        plan.vehicle_search.max_mileage_km
        == 80000
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_document_query_plan():
    planner = QueryPlannerService()

    plan = await planner.plan(
        "Can I return a vehicle after "
        "signing the purchase contract?"
    )

    assert (
        plan.route
        == SearchRoute.UNSTRUCTURED
    )

    assert plan.document_search is not None
    assert plan.vehicle_search is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hybrid_query_plan():
    planner = QueryPlannerService()

    plan = await planner.plan(
        "Find Volkswagen Golf cars "
        "under 20000 euros and tell me "
        "which dealers provide a warranty."
    )

    assert (
        plan.route
        == SearchRoute.HYBRID
    )

    assert plan.vehicle_search is not None
    assert plan.document_search is not None

    assert (
        plan.document_scope
        == DocumentScope.MATCHED_DEALERS
    )