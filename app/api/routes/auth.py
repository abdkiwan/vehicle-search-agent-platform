from fastapi import (
    APIRouter,
    Depends,
)

from app.schemas.security import (
    AuthenticatedPrincipal,
)
from app.security.auth import (
    get_current_principal,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@router.get(
    "/me",
    response_model=AuthenticatedPrincipal,
)
async def get_me(
    principal:
        AuthenticatedPrincipal
        = Depends(
            get_current_principal
        ),
) -> AuthenticatedPrincipal:

    return principal