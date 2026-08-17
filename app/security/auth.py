import asyncio
from functools import lru_cache
from typing import Callable

import jwt
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt import PyJWKClient
from jwt.exceptions import (
    InvalidTokenError,
)

from app.config import settings
from app.schemas.document_search import (
    UserRole,
)
from app.schemas.security import (
    AuthenticatedPrincipal,
)


class AuthenticationError(RuntimeError):
    pass


bearer_scheme = HTTPBearer(
    auto_error=False
)


class CognitoTokenVerifier:
    def __init__(self) -> None:
        self._issuer = (
            f"https://cognito-idp."
            f"{settings.aws_region}"
            f".amazonaws.com/"
            f"{settings.cognito_user_pool_id}"
        )

        self._jwks_url = (
            f"{self._issuer}"
            "/.well-known/jwks.json"
        )

        self._jwks_client = PyJWKClient(
            self._jwks_url,
            cache_keys=True,
        )

    @staticmethod
    def _principal_from_claims(
        claims: dict,
    ) -> AuthenticatedPrincipal:
        raw_groups = claims.get(
            "cognito:groups",
            [],
        )

        if not isinstance(
            raw_groups,
            list,
        ):
            raw_groups = []

        roles: list[UserRole] = []

        for group in raw_groups:
            try:
                role = UserRole(group)
            except ValueError:
                continue

            if role not in roles:
                roles.append(role)

        return AuthenticatedPrincipal(
            subject=claims["sub"],
            username=(
                claims.get("username")
                or claims.get(
                    "cognito:username"
                )
            ),
            client_id=claims["client_id"],
            roles=roles,
        )

    def _verify_sync(
        self,
        token: str,
    ) -> AuthenticatedPrincipal:

        signing_key = (
            self._jwks_client
            .get_signing_key_from_jwt(
                token
            )
        )

        claims = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=[
                "RS256",
            ],
            issuer=self._issuer,
            options={
                # Cognito access tokens use
                # client_id instead of ID-token aud
                # for app-client verification.
                "verify_aud": False,
                "require": [
                    "exp",
                    "iss",
                    "sub",
                    "token_use",
                    "client_id",
                ],
            },
        )

        if (
            claims.get("token_use")
            != "access"
        ):
            raise AuthenticationError(
                "Only Cognito access tokens "
                "are accepted."
            )

        if (
            claims.get("client_id")
            != settings.cognito_app_client_id
        ):
            raise AuthenticationError(
                "Access token was issued for "
                "a different app client."
            )

        raw_groups = claims.get(
            "cognito:groups",
            [],
        )

        if not isinstance(
            raw_groups,
            list,
        ):
            raw_groups = []

        roles: list[UserRole] = []

        for group in raw_groups:
            try:
                role = UserRole(group)
            except ValueError:
                continue

            if role not in roles:
                roles.append(role)

        return self._principal_from_claims(
            claims
        )

    async def verify(
        self,
        token: str,
    ) -> AuthenticatedPrincipal:
        return await asyncio.to_thread(
            self._verify_sync,
            token,
        )


@lru_cache
def get_token_verifier(
) -> CognitoTokenVerifier:
    return CognitoTokenVerifier()


async def get_current_principal(
    credentials:
        HTTPAuthorizationCredentials | None
        = Depends(bearer_scheme),
) -> AuthenticatedPrincipal:

    if credentials is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication required.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if (
        credentials.scheme.lower()
        != "bearer"
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Bearer authentication required."
            ),
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    verifier = get_token_verifier()

    try:
        principal = await verifier.verify(
            credentials.credentials
        )

    except Exception as exc:
        # Do not expose JWT validation details.
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Invalid or expired token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from exc

    if not principal.roles:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Authenticated user has "
                "no application role."
            ),
        )

    return principal


def require_roles(
    *allowed_roles: UserRole,
) -> Callable:

    allowed = set(
        allowed_roles
    )

    async def dependency(
        principal:
            AuthenticatedPrincipal
            = Depends(
                get_current_principal
            ),
    ) -> AuthenticatedPrincipal:

        if not (
            set(principal.roles)
            & allowed
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "Insufficient permissions."
                ),
            )

        return principal

    return dependency