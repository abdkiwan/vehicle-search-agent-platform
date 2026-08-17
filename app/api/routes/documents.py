import logging

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.schemas.security import (
    AuthenticatedPrincipal,
)
from app.security.auth import (
    get_current_principal,
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
    principal:
        AuthenticatedPrincipal
        = Depends(
            get_current_principal
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
            roles=principal.roles,
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