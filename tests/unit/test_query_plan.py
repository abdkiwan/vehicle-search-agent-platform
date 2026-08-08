from app.schemas.query_plan import (
    DocumentScope,
    PlannerOutput,
    SearchRoute,
)
from app.schemas.vehicle_search import (
    VehicleSort,
)
from app.services.query_planner import (
    QueryPlannerService,
)


def test_hybrid_plan_mapping():
    output = PlannerOutput(
        route=SearchRoute.HYBRID,
        makes=["Volkswagen"],
        models=["Golf"],
        max_price_eur=20000,
        max_mileage_km=80000,
        fuel_types=[],
        transmissions=[],
        body_types=[],
        equipment_all=[],
        verified_dealer_only=False,
        vehicle_sort_by=(
            VehicleSort.PRICE_ASC
        ),
        document_query=(
            "dealer used vehicle warranty"
        ),
        document_types=[
            "dealer_policy"
        ],
        document_scope=(
            DocumentScope.MATCHED_DEALERS
        ),
        language="en",
        result_limit=5,
        routing_reason=(
            "Vehicle filters and dealer "
            "warranty evidence are required."
        ),
    )

    plan = (
        QueryPlannerService
        ._build_query_plan(
            output,
            original_query="test query",
        )
    )

    assert (
        plan.route
        == SearchRoute.HYBRID
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
        plan.document_scope
        == DocumentScope.MATCHED_DEALERS
    )

    assert (
        plan.document_search.query
        == "dealer used vehicle warranty"
    )