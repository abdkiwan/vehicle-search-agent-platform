import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_golf_filters_return_expected_vehicles() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/vehicles/search",
            json={
                "makes": ["Volkswagen"],
                "models": ["Golf"],
                "max_price_eur": 20000,
                "max_mileage_km": 80000,
                "sort_by": "price_asc",
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["returned"] == 2

    assert [item["id"] for item in payload["items"]] == [
        "20000000-0000-0000-0000-000000000001",
        "20000000-0000-0000-0000-000000000002",
    ]


@pytest.mark.asyncio
async def test_equipment_filter_requires_all_items() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/vehicles/search",
            json={
                "equipment_all": [
                    "navigation",
                    "heated seats",
                ],
                "limit": 20,
            },
        )

    assert response.status_code == 200

    for item in response.json()["items"]:
        assert "navigation" in item["equipment"]
        assert "heated seats" in item["equipment"]


@pytest.mark.asyncio
async def test_invalid_price_range_is_rejected() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/vehicles/search",
            json={
                "min_price_eur": 30000,
                "max_price_eur": 20000,
            },
        )

    assert response.status_code == 422