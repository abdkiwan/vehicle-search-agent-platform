from app.config import settings
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.retrieval.embeddings import (
    BedrockEmbeddingService,
)
from app.retrieval.fusion import (
    reciprocal_rank_fusion,
)
from app.schemas.document_search import (
    DocumentSearchItem,
    DocumentSearchRequest,
    DocumentSearchResponse,
    RetrievalScores,
    UserRole,
)


class DocumentSearchService:
    def __init__(
        self,
        repository: DocumentRepository,
        embeddings: BedrockEmbeddingService,
    ) -> None:
        self._repository = repository
        self._embeddings = embeddings

    async def search(
        self,
        request: DocumentSearchRequest,
        roles: list[UserRole],
    ) -> DocumentSearchResponse:
        query_embedding = (
            await self._embeddings.embed(
                request.query
            )
        )

        keyword_results = (
            await self._repository.keyword_search(
                request=request,
                roles=roles,
                candidate_limit=(
                    settings.hybrid_candidate_limit
                ),
            )
        )

        vector_results = (
            await self._repository.vector_search(
                request=request,
                roles=roles,
                query_embedding=query_embedding,
                candidate_limit=(
                    settings.hybrid_candidate_limit
                ),
            )
        )

        fused_results = reciprocal_rank_fusion(
            keyword_results,
            vector_results,
            k=settings.rrf_k,
            limit=request.limit,
        )

        items = []

        for result in fused_results:
            candidate = result.candidate

            items.append(
                DocumentSearchItem(
                    chunk_id=candidate.chunk_id,
                    document_id=(
                        candidate.document_id
                    ),
                    citation=(
                        f"document:"
                        f"{candidate.document_id}"
                        f"#chunk_"
                        f"{candidate.chunk_index}"
                    ),
                    title=candidate.title,
                    document_type=(
                        candidate.document_type
                    ),
                    dealer_id=candidate.dealer_id,
                    vehicle_id=candidate.vehicle_id,
                    chunk_index=(
                        candidate.chunk_index
                    ),
                    content=candidate.content,
                    scores=RetrievalScores(
                        keyword_rank=(
                            result.keyword_rank
                        ),
                        keyword_score=(
                            candidate.keyword_score
                        ),
                        vector_rank=(
                            result.vector_rank
                        ),
                        vector_similarity=(
                            candidate.vector_similarity
                        ),
                        rrf_score=(
                            result.rrf_score
                        ),
                    ),
                )
            )

        return DocumentSearchResponse(
            query=request.query,
            items=items,
            returned=len(items),
        )