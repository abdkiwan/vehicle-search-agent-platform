from uuid import UUID

from app.schemas.answer import (
    AnswerStatus,
    GeneratedAnswer,
)
from app.schemas.context import (
    CitationRecord,
    CitationType,
    ContextPackage,
    ContextStats,
)
from app.services.answer_validator import (
    CitationValidator,
)


VEHICLE_ID = UUID(
    "20000000-0000-0000-0000-000000000001"
)

VALID_CITATION = (
    f"[vehicle:{VEHICLE_ID}]"
)


def make_context():
    return ContextPackage(
        text=(
            "<vehicle_evidence>\n"
            f"CITATION: {VALID_CITATION}\n"
            "MAKE: Volkswagen\n"
            "MODEL: Golf\n"
            "PRICE_EUR: 18990.00\n"
            "</vehicle_evidence>"
        ),
        citations=[
            CitationRecord(
                citation=VALID_CITATION,
                source_type=(
                    CitationType.VEHICLE
                ),
                vehicle_id=VEHICLE_ID,
                title="Volkswagen Golf",
            )
        ],
        stats=ContextStats(
            vehicle_candidates=1,
            vehicles_included=1,
            total_characters=100,
        ),
        has_evidence=True,
    )


def test_valid_citation_passes():
    validator = CitationValidator()

    generated = GeneratedAnswer(
        status=AnswerStatus.ANSWERED,
        answer=(
            "The Golf costs €18,990 "
            f"{VALID_CITATION}"
        ),
        citations_used=[
            VALID_CITATION
        ],
    )

    result = validator.validate(
        answer=generated,
        context=make_context(),
    )

    assert result.passed is True


def test_fake_citation_is_rejected():
    validator = CitationValidator()

    fake = (
        "[vehicle:"
        "99999999-9999-9999-9999-999999999999]"
    )

    generated = GeneratedAnswer(
        status=AnswerStatus.ANSWERED,
        answer=f"The car costs €10. {fake}",
        citations_used=[fake],
    )

    result = validator.validate(
        answer=generated,
        context=make_context(),
    )

    assert result.passed is False
    assert fake in result.invalid_citations


def test_answered_response_requires_citation():
    validator = CitationValidator()

    generated = GeneratedAnswer(
        status=AnswerStatus.ANSWERED,
        answer="The Golf costs €18,990.",
        citations_used=[],
    )

    result = validator.validate(
        answer=generated,
        context=make_context(),
    )

    assert result.passed is False