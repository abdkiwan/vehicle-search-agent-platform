from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Annotated, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


PriceEur = Annotated[
    Decimal,
    Field(ge=0, max_digits=10, decimal_places=2),
]


class VehicleSort(str, Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    MILEAGE_ASC = "mileage_asc"
    YEAR_DESC = "year_desc"
    NEWEST = "newest"


class VehicleSearchRequest(BaseModel):
    makes: list[str] = Field(default_factory=list, max_length=10)
    models: list[str] = Field(default_factory=list, max_length=10)

    min_price_eur: PriceEur | None = None
    max_price_eur: PriceEur | None = None

    min_year: int | None = Field(default=None, ge=1900, le=2100)
    max_year: int | None = Field(default=None, ge=1900, le=2100)
    max_mileage_km: int | None = Field(default=None, ge=0)

    fuel_types: list[str] = Field(default_factory=list, max_length=10)
    transmissions: list[str] = Field(default_factory=list, max_length=10)
    body_types: list[str] = Field(default_factory=list, max_length=10)

    min_power_kw: int | None = Field(default=None, ge=1)
    equipment_all: list[str] = Field(default_factory=list, max_length=20)

    dealer_ids: list[UUID] = Field(default_factory=list, max_length=20)
    verified_dealer_only: bool = False
    min_dealer_rating: float | None = Field(default=None, ge=0, le=5)

    sort_by: VehicleSort = VehicleSort.PRICE_ASC
    limit: int = Field(default=10, ge=1, le=20)
    offset: int = Field(default=0, ge=0, le=1000)

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "makes",
        "models",
        "fuel_types",
        "transmissions",
        "body_types",
        "equipment_all",
    )
    @classmethod
    def clean_string_lists(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for value in values:
            normalized = value.strip()
            key = normalized.casefold()

            if normalized and key not in seen:
                cleaned.append(normalized)
                seen.add(key)

        return cleaned

    @model_validator(mode="after")
    def validate_ranges(self) -> Self:
        if (
            self.min_price_eur is not None
            and self.max_price_eur is not None
            and self.min_price_eur > self.max_price_eur
        ):
            raise ValueError(
                "min_price_eur must not exceed max_price_eur"
            )

        if (
            self.min_year is not None
            and self.max_year is not None
            and self.min_year > self.max_year
        ):
            raise ValueError("min_year must not exceed max_year")

        return self

    @staticmethod
    def euros_to_cents(value: Decimal | None) -> int | None:
        if value is None:
            return None

        return int(
            (value * 100).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )


class Money(BaseModel):
    amount_minor: int
    currency: str = "EUR"


class DealerSummary(BaseModel):
    id: UUID
    name: str
    city: str
    rating: float | None
    is_verified: bool
    warranty_months: int


class VehicleSearchItem(BaseModel):
    id: UUID
    make: str
    model: str
    variant: str | None
    price: Money
    year: int
    mileage_km: int
    fuel_type: str
    transmission: str
    body_type: str
    power_kw: int | None
    color: str | None
    equipment: list[str]
    description: str | None
    dealer: DealerSummary


class VehicleSearchResponse(BaseModel):
    items: list[VehicleSearchItem]
    returned: int
    limit: int
    offset: int
    has_more: bool
    applied_filters: VehicleSearchRequest
