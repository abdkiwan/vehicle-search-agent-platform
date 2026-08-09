import pytest
from httpx import (
    ASGITransport,
    AsyncClient,
)

from app.main import app


@pytest.mark.asyncio
@pytest.mark.integration
async def test_grounded_vehicle_answer():
    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/search/answer",
            headers={
                "X-User-Role": "customer",
            },
            json={
                "query": (
                    "Find Volkswagen Golf cars "
                    "under 20000 euros with less "
                    "than 80000 km."
                )
            },
        )

    assert response.status_code == 200

    payload = response.json()

    answer = payload["answer"]

    assert answer["status"] == "answered"

    assert (
        answer["validation"]["passed"]
        is True
    )

    assert (
        answer["validation"]
        ["citation_validation"]
        ["passed"]
        is True
    )

    assert (
        answer["validation"]
        ["grounding_validation"]
        ["passed"]
        is True
    )

    assert len(
        answer["citations"]
    ) > 0