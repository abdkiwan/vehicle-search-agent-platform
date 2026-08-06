from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.vehicle_search import (
    DealerSummary,
    Money,
    VehicleSearchItem,
    VehicleSearchRequest,
    VehicleSearchResponse,
)


class VehicleSearchService:
    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    async def search(
        self,
        filters: VehicleSearchRequest,
    ) -> VehicleSearchResponse:
        result = await self._repository.search(filters)

        items = [
            VehicleSearchItem(
                id=row.vehicle.id,
                make=row.vehicle.make,
                model=row.vehicle.model,
                variant=row.vehicle.variant,
                price=Money(
                    amount_minor=row.vehicle.price_eur_cents,
                ),
                year=row.vehicle.year,
                mileage_km=row.vehicle.mileage_km,
                fuel_type=row.vehicle.fuel_type,
                transmission=row.vehicle.transmission,
                body_type=row.vehicle.body_type,
                power_kw=row.vehicle.power_kw,
                color=row.vehicle.color,
                equipment=list(row.vehicle.equipment or []),
                description=row.vehicle.description,
                dealer=DealerSummary(
                    id=row.dealer.id,
                    name=row.dealer.name,
                    city=row.dealer.city,
                    rating=(
                        float(row.dealer.rating)
                        if row.dealer.rating is not None
                        else None
                    ),
                    is_verified=row.dealer.is_verified,
                    warranty_months=row.dealer.warranty_months,
                ),
            )
            for row in result.rows
        ]

        return VehicleSearchResponse(
            items=items,
            returned=len(items),
            limit=filters.limit,
            offset=filters.offset,
            has_more=result.has_more,
            applied_filters=filters,
        )
