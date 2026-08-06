from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dealer import Dealer
from app.models.vehicle import Vehicle
from app.schemas.vehicle_search import (
    VehicleSearchRequest,
    VehicleSort,
)


@dataclass(frozen=True)
class VehicleDealerRow:
    vehicle: Vehicle
    dealer: Dealer


@dataclass(frozen=True)
class VehicleRepositoryResult:
    rows: list[VehicleDealerRow]
    has_more: bool


class VehicleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(
        self,
        filters: VehicleSearchRequest,
    ) -> VehicleRepositoryResult:
        statement = (
            select(Vehicle, Dealer)
            .join(Dealer, Dealer.id == Vehicle.dealer_id)
            .where(Vehicle.status == "active")
        )

        if filters.makes:
            statement = statement.where(
                func.lower(Vehicle.make).in_(
                    [value.lower() for value in filters.makes]
                )
            )

        if filters.models:
            statement = statement.where(
                func.lower(Vehicle.model).in_(
                    [value.lower() for value in filters.models]
                )
            )

        min_price_cents = filters.euros_to_cents(
            filters.min_price_eur
        )
        max_price_cents = filters.euros_to_cents(
            filters.max_price_eur
        )

        if min_price_cents is not None:
            statement = statement.where(
                Vehicle.price_eur_cents >= min_price_cents
            )

        if max_price_cents is not None:
            statement = statement.where(
                Vehicle.price_eur_cents <= max_price_cents
            )

        if filters.min_year is not None:
            statement = statement.where(
                Vehicle.year >= filters.min_year
            )

        if filters.max_year is not None:
            statement = statement.where(
                Vehicle.year <= filters.max_year
            )

        if filters.max_mileage_km is not None:
            statement = statement.where(
                Vehicle.mileage_km <= filters.max_mileage_km
            )

        if filters.fuel_types:
            statement = statement.where(
                func.lower(Vehicle.fuel_type).in_(
                    [value.lower() for value in filters.fuel_types]
                )
            )

        if filters.transmissions:
            statement = statement.where(
                func.lower(Vehicle.transmission).in_(
                    [value.lower() for value in filters.transmissions]
                )
            )

        if filters.body_types:
            statement = statement.where(
                func.lower(Vehicle.body_type).in_(
                    [value.lower() for value in filters.body_types]
                )
            )

        if filters.min_power_kw is not None:
            statement = statement.where(
                Vehicle.power_kw >= filters.min_power_kw
            )

        if filters.equipment_all:
            statement = statement.where(
                Vehicle.equipment.contains(filters.equipment_all)
            )

        if filters.dealer_ids:
            statement = statement.where(
                Dealer.id.in_(filters.dealer_ids)
            )

        if filters.verified_dealer_only:
            statement = statement.where(
                Dealer.is_verified.is_(True)
            )

        if filters.min_dealer_rating is not None:
            statement = statement.where(
                Dealer.rating >= filters.min_dealer_rating
            )

        sort_columns = {
            VehicleSort.PRICE_ASC: (
                Vehicle.price_eur_cents.asc(),
            ),
            VehicleSort.PRICE_DESC: (
                Vehicle.price_eur_cents.desc(),
            ),
            VehicleSort.MILEAGE_ASC: (
                Vehicle.mileage_km.asc(),
            ),
            VehicleSort.YEAR_DESC: (
                Vehicle.year.desc(),
                Vehicle.mileage_km.asc(),
            ),
            VehicleSort.NEWEST: (
                Vehicle.created_at.desc(),
            ),
        }

        statement = statement.order_by(
            *sort_columns[filters.sort_by],
            Vehicle.id.asc(),
        )

        statement = statement.offset(filters.offset).limit(
            filters.limit + 1
        )

        result = await self._session.execute(statement)
        raw_rows = result.all()

        has_more = len(raw_rows) > filters.limit
        raw_rows = raw_rows[: filters.limit]

        return VehicleRepositoryResult(
            rows=[
                VehicleDealerRow(
                    vehicle=vehicle,
                    dealer=dealer,
                )
                for vehicle, dealer in raw_rows
            ],
            has_more=has_more,
        )
