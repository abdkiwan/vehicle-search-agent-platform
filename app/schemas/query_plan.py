from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.document_search import DocumentSearchRequest
from app.schemas.vehicle_search import (
    VehicleSearchRequest,
    VehicleSort,
)
from app.schemas.context import ContextPackage

class SearchRoute(str, Enum):
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    HYBRID = "hybrid"
    UNSUPPORTED = "unsupported"


class DocumentScope(str, Enum):
    GLOBAL = "global"
    MATCHED_DEALERS = "matched_dealers"
    MATCHED_VEHICLES = "matched_vehicles"


class NaturalLanguageSearchRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=2000,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class PlannerOutput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    route: SearchRoute

    makes: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    models: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    min_price_eur: Decimal | None = Field(
        default=None,
        ge=0,
    )

    max_price_eur: Decimal | None = Field(
        default=None,
        ge=0,
    )

    min_year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
    )

    max_year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
    )

    max_mileage_km: int | None = Field(
        default=None,
        ge=0,
    )

    fuel_types: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    transmissions: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    body_types: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    min_power_kw: int | None = Field(
        default=None,
        ge=1,
    )

    equipment_all: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    verified_dealer_only: bool = False

    min_dealer_rating: float | None = Field(
        default=None,
        ge=0,
        le=5,
    )

    vehicle_sort_by: VehicleSort = (
        VehicleSort.PRICE_ASC
    )

    document_query: str = ""

    document_types: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    document_scope: DocumentScope = (
        DocumentScope.GLOBAL
    )

    language: str = "en"

    result_limit: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    routing_reason: str


class QueryPlan(BaseModel):
    route: SearchRoute

    vehicle_search: (
        VehicleSearchRequest | None
    ) = None

    document_search: (
        DocumentSearchRequest | None
    ) = None

    document_scope: DocumentScope = (
        DocumentScope.GLOBAL
    )

    routing_reason: str


class UnifiedSearchResponse(BaseModel):
    query: str
    plan: QueryPlan
    structured_results: object | None = None
    document_results: object | None = None
    context: ContextPackage | None = None