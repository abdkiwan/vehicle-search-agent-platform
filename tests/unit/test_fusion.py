from uuid import uuid4

from app.repositories.document_repository import (
    DocumentCandidate,
)
from app.retrieval.fusion import (
    reciprocal_rank_fusion,
)


def candidate(
    *,
    chunk_id,
    title: str,
) -> DocumentCandidate:
    return DocumentCandidate(
        chunk_id=chunk_id,
        document_id=uuid4(),
        title=title,
        document_type="help_center",
        dealer_id=None,
        vehicle_id=None,
        chunk_index=0,
        content="test",
    )


def test_rrf_rewards_results_found_by_both_retrievers():
    shared_id = uuid4()

    keyword_only = candidate(
        chunk_id=uuid4(),
        title="keyword",
    )

    shared = candidate(
        chunk_id=shared_id,
        title="shared",
    )

    vector_only = candidate(
        chunk_id=uuid4(),
        title="vector",
    )

    results = reciprocal_rank_fusion(
        keyword_results=[
            keyword_only,
            shared,
        ],
        vector_results=[
            shared,
            vector_only,
        ],
        limit=3,
    )

    assert results[0].candidate.chunk_id == (
        shared_id
    )