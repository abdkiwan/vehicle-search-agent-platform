from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class CitationType(str, Enum):
    VEHICLE = "vehicle"
    DOCUMENT = "document"


class CitationRecord(BaseModel):
    citation: str
    source_type: CitationType

    vehicle_id: UUID | None = None

    document_id: UUID | None = None
    chunk_id: UUID | None = None
    chunk_index: int | None = None

    title: str | None = None


class ContextStats(BaseModel):
    vehicle_candidates: int = 0
    vehicles_included: int = 0

    document_candidates: int = 0
    document_chunks_included: int = 0

    total_characters: int = 0

    truncated_document_chunks: int = 0

    budget_exhausted: bool = False


class ContextPackage(BaseModel):
    text: str

    citations: list[CitationRecord] = Field(
        default_factory=list
    )

    stats: ContextStats

    has_evidence: bool