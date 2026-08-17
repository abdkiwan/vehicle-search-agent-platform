import pytest

from app.main import app
from app.schemas.document_search import (
    UserRole,
)
from app.schemas.security import (
    AuthenticatedPrincipal,
)
from app.security.auth import (
    get_current_principal,
)


@pytest.fixture(autouse=True)
def override_authentication():
    principal = AuthenticatedPrincipal(
        subject="integration-test-user",
        username="integration@example.com",
        client_id="integration-test-client",
        roles=[
            UserRole.CUSTOMER,
        ],
    )

    app.dependency_overrides[
        get_current_principal
    ] = lambda: principal

    yield

    app.dependency_overrides.pop(
        get_current_principal,
        None,
    )