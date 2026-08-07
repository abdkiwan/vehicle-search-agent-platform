from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk
from app.schemas.document_search import (
    DocumentSearchRequest,
    UserRole,
)


@dataclass(frozen=True)
class DocumentCandidate:
    chunk_id: UUID
    document_id: UUID

    title: str
    document_type: str

    dealer_id: UUID | None
    vehicle_id: UUID | None

    chunk_index: int
    content: str

    keyword_score: float | None = None
    vector_similarity: float | None = None


class DocumentRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def keyword_search(
        self,
        request: DocumentSearchRequest,
        role: UserRole,
        candidate_limit: int,
    ) -> list[DocumentCandidate]:
        query = func.websearch_to_tsquery(
            "english",
            request.query,
        )

        rank = func.ts_rank_cd(
            DocumentChunk.content_tsv,
            query,
        ).label("keyword_score")

        statement = (
            select(
                DocumentChunk,
                Document,
                rank,
            )
            .join(
                Document,
                Document.id
                == DocumentChunk.document_id,
            )
            .where(
                DocumentChunk.content_tsv.op("@@")(
                    query
                )
            )
            .where(
                Document.allowed_roles.any(
                    role.value
                )
            )
            .where(
                Document.language
                == request.language
            )
        )

        if request.document_types:
            statement = statement.where(
                Document.document_type.in_(
                    request.document_types
                )
            )

        if request.dealer_ids:
            statement = statement.where(
                Document.dealer_id.in_(
                    request.dealer_ids
                )
            )

        if request.vehicle_ids:
            statement = statement.where(
                Document.vehicle_id.in_(
                    request.vehicle_ids
                )
            )

        statement = (
            statement
            .order_by(
                rank.desc(),
                DocumentChunk.id.asc(),
            )
            .limit(candidate_limit)
        )

        result = await self._session.execute(
            statement
        )

        candidates: list[DocumentCandidate] = []

        for chunk, document, score in result.all():
            candidates.append(
                DocumentCandidate(
                    chunk_id=chunk.id,
                    document_id=document.id,
                    title=document.title,
                    document_type=(
                        document.document_type
                    ),
                    dealer_id=document.dealer_id,
                    vehicle_id=document.vehicle_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    keyword_score=float(score),
                )
            )

        return candidates

    async def vector_search(
        self,
        request: DocumentSearchRequest,
        role: UserRole,
        query_embedding: list[float],
        candidate_limit: int,
    ) -> list[DocumentCandidate]:
        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        ).label("distance")

        statement = (
            select(
                DocumentChunk,
                Document,
                distance,
            )
            .join(
                Document,
                Document.id
                == DocumentChunk.document_id,
            )
            .where(
                Document.allowed_roles.any(
                    role.value
                )
            )
            .where(
                Document.language
                == request.language
            )
        )

        if request.document_types:
            statement = statement.where(
                Document.document_type.in_(
                    request.document_types
                )
            )

        if request.dealer_ids:
            statement = statement.where(
                Document.dealer_id.in_(
                    request.dealer_ids
                )
            )

        if request.vehicle_ids:
            statement = statement.where(
                Document.vehicle_id.in_(
                    request.vehicle_ids
                )
            )

        statement = (
            statement
            .order_by(
                distance.asc(),
                DocumentChunk.id.asc(),
            )
            .limit(candidate_limit)
        )

        result = await self._session.execute(
            statement
        )

        candidates: list[DocumentCandidate] = []

        for chunk, document, distance_value in result.all():
            candidates.append(
                DocumentCandidate(
                    chunk_id=chunk.id,
                    document_id=document.id,
                    title=document.title,
                    document_type=(
                        document.document_type
                    ),
                    dealer_id=document.dealer_id,
                    vehicle_id=document.vehicle_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    vector_similarity=(
                        1.0 - float(distance_value)
                    ),
                )
            )

        return candidates