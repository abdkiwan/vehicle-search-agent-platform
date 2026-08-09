from enum import Enum

from pydantic import BaseModel, Field


class AnswerStatus(str, Enum):
    ANSWERED = "answered"

    INSUFFICIENT_EVIDENCE = (
        "insufficient_evidence"
    )

    UNSUPPORTED = "unsupported"

    VALIDATION_FAILED = (
        "validation_failed"
    )


class GeneratedAnswer(BaseModel):
    status: AnswerStatus

    answer: str = Field(
        min_length=1,
        max_length=4500,
    )

    citations_used: list[str] = Field(
        default_factory=list,
        max_length=20,
    )


class CitationValidationResult(BaseModel):
    passed: bool

    citations_used: list[str] = Field(
        default_factory=list
    )

    invalid_citations: list[str] = Field(
        default_factory=list
    )

    undeclared_citations: list[str] = Field(
        default_factory=list
    )

    missing_from_text: list[str] = Field(
        default_factory=list
    )


class GroundingValidationResult(BaseModel):
    evaluated: bool = False

    grounding_score: float | None = None
    relevance_score: float | None = None

    grounded: bool | None = None
    relevant: bool | None = None

    passed: bool = False


class AnswerValidationResult(BaseModel):
    passed: bool

    citation_validation: (
        CitationValidationResult
    )

    grounding_validation: (
        GroundingValidationResult
    )

    issues: list[str] = Field(
        default_factory=list
    )


class FinalAnswer(BaseModel):
    status: AnswerStatus

    answer: str

    citations: list[str] = Field(
        default_factory=list
    )

    validation: AnswerValidationResult


class SearchAnswerResponse(BaseModel):
    query: str
    answer: FinalAnswer