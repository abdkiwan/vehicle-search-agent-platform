from decimal import Decimal
from uuid import UUID

from app.schemas.document_search import (
    DocumentSearchItem,
    DocumentSearchResponse,
    RetrievalScores,
)
from app.schemas.vehicle_search import (
    DealerSummary,
    Money,
    VehicleSearchItem,
    VehicleSearchResponse,
)
from app.services.context_builder import (
    ContextBuilderService,
)


VEHICLE_ID = UUID(
    "20000000-0000-0000-0000-000000000001"
)

DEALER_ID = UUID(
    "10000000-0000-0000-0000-000000000001"
)

DOCUMENT_ID = UUID(
    "30000000-0000-0000-0000-000000000001"
)

CHUNK_ID = UUID(
    "40000000-0000-0000-0000-000000000001"
)


def make_vehicle_results():
    vehicle = VehicleSearchItem(
        id=VEHICLE_ID,
        make="Volkswagen",
        model="Golf",
        variant="1.5 TSI Life",
        price=Money(
            amount_minor=1899000,
        ),
        year=2021,
        mileage_km=62000,
        fuel_type="petrol",
        transmission="automatic",
        body_type="hatchback",
        power_kw=110,
        color="black",
        equipment=[
            "navigation",
            "heated seats",
        ],
        description=(
            "This should not be copied "
            "into structured context."
        ),
        dealer=DealerSummary(
            id=DEALER_ID,
            name="AutoHaus Berlin",
            city="Berlin",
            rating=4.7,
            is_verified=True,
            warranty_months=24,
        ),
    )

    return VehicleSearchResponse(
        items=[vehicle],
        returned=1,
        limit=5,
        offset=0,
        has_more=False,
        applied_filters={},
    )


def make_document_results():
    item = DocumentSearchItem(
        chunk_id=CHUNK_ID,
        document_id=DOCUMENT_ID,
        citation=(
            f"document:{DOCUMENT_ID}#chunk_0"
        ),
        title=(
            "Vehicle Return and "
            "Cancellation Policy"
        ),
        document_type="help_center",
        dealer_id=None,
        vehicle_id=None,
        chunk_index=0,
        content=(
            "Customers may have cancellation "
            "rights under the conditions "
            "described in this policy."
        ),
        scores=RetrievalScores(
            keyword_rank=1,
            keyword_score=0.9,
            vector_rank=1,
            vector_similarity=0.88,
            rrf_score=0.03,
        ),
    )

    return DocumentSearchResponse(
        query="return policy",
        items=[item],
        returned=1,
    )


def test_context_contains_stable_vehicle_citation():
    builder = ContextBuilderService()

    result = builder.build(
        structured_results=(
            make_vehicle_results()
        ),
        document_results=None,
    )

    expected = (
        f"[vehicle:{VEHICLE_ID}]"
    )

    assert expected in result.text

    assert result.citations[0].citation == (
        expected
    )


def test_vehicle_description_is_not_duplicated():
    builder = ContextBuilderService()

    result = builder.build(
        structured_results=(
            make_vehicle_results()
        ),
        document_results=None,
    )

    assert (
        "This should not be copied"
        not in result.text
    )


def test_document_citation_is_stable():
    builder = ContextBuilderService()

    result = builder.build(
        structured_results=None,
        document_results=(
            make_document_results()
        ),
    )

    expected = (
        f"[document:{DOCUMENT_ID}"
        "#chunk_0]"
    )

    assert expected in result.text

    assert (
        result.citations[0].citation
        == expected
    )


def test_context_contains_both_source_types():
    builder = ContextBuilderService()

    result = builder.build(
        structured_results=(
            make_vehicle_results()
        ),
        document_results=(
            make_document_results()
        ),
    )

    source_types = {
        citation.source_type
        for citation in result.citations
    }

    assert "vehicle" in source_types
    assert "document" in source_types