from typing import Annotated

from fastapi import Header, HTTPException

from app.schemas.document_search import UserRole


async def get_current_role(
    x_user_role: Annotated[
        str | None,
        Header(alias="X-User-Role"),
    ] = None,
) -> UserRole:
    value = x_user_role or "customer"

    try:
        return UserRole(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Unsupported user role",
        ) from exc