import logging

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_role
from app.db import get_db_session
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.retrieval.embeddings import (
    BedrockEmbeddingService,
)
from app.schemas.document_search import (
    DocumentSearchRequest,
    DocumentSearchResponse,
    UserRole,
)
from app.services.document_search import (
    DocumentSearchService,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"],
)


@router.post(
    "/search",
    response_model=DocumentSearchResponse,
)
async def search_documents(
    request: DocumentSearchRequest,
    role: UserRole = Depends(
        get_current_role
    ),
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> DocumentSearchResponse:
    service = DocumentSearchService(
        repository=DocumentRepository(
            session
        ),
        embeddings=BedrockEmbeddingService(),
    )

    try:
        return await service.search(
            request=request,
            role=role,
        )

    except ClientError as exc:
        logger.exception(
            "Bedrock embedding request failed"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Document search is temporarily "
                "unavailable"
            ),
        ) from exc

    except SQLAlchemyError as exc:
        logger.exception(
            "Document retrieval failed"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Document search is temporarily "
                "unavailable"
            ),
        ) from exc