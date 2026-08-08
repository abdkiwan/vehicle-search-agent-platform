import pytest
from httpx import (
    ASGITransport,
    AsyncClient,
)

from app.main import app


@pytest.mark.asyncio
@pytest.mark.integration
async def test_structured_workflow():
    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/search/retrieve",
            headers={
                "X-User-Role": "customer",
            },
            json={
                "query": (
                    "Find Volkswagen Golf cars "
                    "under 20000 euros with less "
                    "than 80000 km."
                ),
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["plan"]["route"]
        == "structured"
    )

    assert (
        payload["structured_results"]
        is not None
    )

    assert (
        payload["document_results"]
        is None
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_unstructured_workflow():
    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/search/retrieve",
            headers={
                "X-User-Role": "customer",
            },
            json={
                "query": (
                    "Can I return a vehicle "
                    "after signing the purchase "
                    "contract?"
                ),
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["plan"]["route"]
        == "unstructured"
    )

    assert (
        payload["structured_results"]
        is None
    )

    assert (
        payload["document_results"]
        is not None
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hybrid_workflow():
    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/search/retrieve",
            headers={
                "X-User-Role": "customer",
            },
            json={
                "query": (
                    "Find Volkswagen Golf cars "
                    "under 20000 euros and tell me "
                    "which dealers provide a warranty."
                ),
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["plan"]["route"]
        == "hybrid"
    )

    assert (
        payload["structured_results"]
        is not None
    )

    assert (
        payload["document_results"]
        is not None
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_unsupported_workflow():
    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/search/retrieve",
            headers={
                "X-User-Role": "customer",
            },
            json={
                "query": (
                    "What is the weather tomorrow?"
                ),
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["plan"]["route"]
        == "unsupported"
    )

    assert (
        payload["structured_results"]
        is None
    )

    assert (
        payload["document_results"]
        is None
    )