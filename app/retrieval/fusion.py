from dataclasses import dataclass, replace

from app.repositories.document_repository import (
    DocumentCandidate,
)


@dataclass(frozen=True)
class FusedCandidate:
    candidate: DocumentCandidate

    rrf_score: float

    keyword_rank: int | None
    vector_rank: int | None


def reciprocal_rank_fusion(
    keyword_results: list[DocumentCandidate],
    vector_results: list[DocumentCandidate],
    *,
    k: int = 60,
    limit: int = 5,
) -> list[FusedCandidate]:
    scores: dict[object, float] = {}
    candidates: dict[
        object,
        DocumentCandidate,
    ] = {}

    keyword_ranks: dict[object, int] = {}
    vector_ranks: dict[object, int] = {}

    for rank, candidate in enumerate(
        keyword_results,
        start=1,
    ):
        chunk_id = candidate.chunk_id

        scores[chunk_id] = (
            scores.get(chunk_id, 0.0)
            + 1.0 / (k + rank)
        )

        keyword_ranks[chunk_id] = rank
        candidates[chunk_id] = candidate

    for rank, candidate in enumerate(
        vector_results,
        start=1,
    ):
        chunk_id = candidate.chunk_id

        scores[chunk_id] = (
            scores.get(chunk_id, 0.0)
            + 1.0 / (k + rank)
        )

        vector_ranks[chunk_id] = rank

        existing = candidates.get(chunk_id)

        if existing is None:
            candidates[chunk_id] = candidate
        else:
            candidates[chunk_id] = replace(
                existing,
                vector_similarity=(
                    candidate.vector_similarity
                ),
            )

    ordered_ids = sorted(
        scores,
        key=lambda chunk_id: (
            -scores[chunk_id],
            str(chunk_id),
        ),
    )

    return [
        FusedCandidate(
            candidate=candidates[chunk_id],
            rrf_score=scores[chunk_id],
            keyword_rank=keyword_ranks.get(
                chunk_id
            ),
            vector_rank=vector_ranks.get(
                chunk_id
            ),
        )
        for chunk_id in ordered_ids[:limit]
    ]