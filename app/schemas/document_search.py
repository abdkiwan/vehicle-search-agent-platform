from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserRole(str, Enum):
    CUSTOMER = "customer"
    DEALER = "dealer"
    SUPPORT = "support"
    ADMIN = "admin"


class DocumentSearchRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=1000,
    )

    document_types: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    dealer_ids: list[UUID] = Field(
        default_factory=list,
        max_length=20,
    )

    vehicle_ids: list[UUID] = Field(
        default_factory=list,
        max_length=20,
    )

    language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    model_config = ConfigDict(extra="forbid")


class RetrievalScores(BaseModel):
    keyword_rank: int | None = None
    keyword_score: float | None = None

    vector_rank: int | None = None
    vector_similarity: float | None = None

    rrf_score: float


class DocumentSearchItem(BaseModel):
    chunk_id: UUID
    document_id: UUID

    citation: str

    title: str
    document_type: str

    dealer_id: UUID | None
    vehicle_id: UUID | None

    chunk_index: int
    content: str

    scores: RetrievalScores


class DocumentSearchResponse(BaseModel):
    query: str
    items: list[DocumentSearchItem]
    returned: int