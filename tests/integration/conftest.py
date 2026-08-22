import pytest
import pytest_asyncio

from app.cache.redis_cache import (
    get_redis_cache,
)
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
    """
    Integration tests exercise the application pipeline,
    not Cognito itself.

    Real Cognito authentication is tested separately with
    live smoke tests.
    """

    principal = AuthenticatedPrincipal(
        subject="integration-test-user",
        username="integration@example.com",
        client_id="integration-test-client",
        roles=[
            UserRole.CUSTOMER,
        ],
    )

    async def get_test_principal():
        return principal

    app.dependency_overrides[
        get_current_principal
    ] = get_test_principal

    yield

    app.dependency_overrides.pop(
        get_current_principal,
        None,
    )


@pytest_asyncio.fixture(autouse=True)
async def isolate_redis_cache():
    """
    Redis asyncio connections are tied to the event loop
    in which they are used.

    pytest may create a new event loop for each async test,
    while get_redis_cache() is process-global because it is
    protected by @lru_cache.

    Give every integration test its own RedisCache instance
    and close it before that test's event loop disappears.
    """

    # Remove any Redis singleton left by an earlier test.
    get_redis_cache.cache_clear()

    # Create the cache object that this test will use.
    cache = get_redis_cache()

    yield

    # Close connections while we are still running inside
    # this test's event loop.
    await cache.close()

    # Do not allow the next test to reuse this instance.
    get_redis_cache.cache_clear()