from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.document_search import UserRole


class AuthenticatedPrincipal(BaseModel):
    subject: str

    username: str | None = None

    client_id: str

    roles: list[UserRole] = Field(
        default_factory=list
    )


class PromptSecuritySource(str, Enum):
    USER_INPUT = "user_input"

    RETRIEVED_CONTEXT = (
        "retrieved_context"
    )


class PromptSecurityResult(BaseModel):
    allowed: bool

    source: PromptSecuritySource

    action: str

    prompt_attack_detected: bool = False

    confidence: str | None = None