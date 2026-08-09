from app.config import settings
from app.schemas.context import (
    CitationRecord,
    CitationType,
    ContextPackage,
    ContextStats,
)
from app.schemas.document_search import (
    DocumentSearchResponse,
)
from app.schemas.vehicle_search import (
    VehicleSearchResponse,
)
from decimal import Decimal


class ContextBuilderService:
    """
    Builds a bounded, deterministic evidence package from
    structured and unstructured retrieval results.

    No LLM is involved in this step.
    """

    def build(
        self,
        *,
        structured_results: (
            VehicleSearchResponse | None
        ),
        document_results: (
            DocumentSearchResponse | None
        ),
    ) -> ContextPackage:
        blocks: list[str] = []
        citations: list[CitationRecord] = []

        total_chars = 0
        budget_exhausted = False
        truncated_chunks = 0

        vehicle_candidates = (
            len(structured_results.items)
            if structured_results is not None
            else 0
        )

        document_candidates = (
            len(document_results.items)
            if document_results is not None
            else 0
        )

        vehicles_included = 0
        document_chunks_included = 0

        # ---------------------------------
        # Structured vehicle evidence
        # ---------------------------------

        if structured_results is not None:
            for vehicle in structured_results.items[
                : settings.context_max_vehicles
            ]:
                citation = (
                    f"[vehicle:{vehicle.id}]"
                )

                block = self._vehicle_block(
                    vehicle=vehicle,
                    citation=citation,
                )

                if (
                    total_chars + len(block)
                    > settings.context_max_chars
                ):
                    budget_exhausted = True
                    break

                blocks.append(block)

                citations.append(
                    CitationRecord(
                        citation=citation,
                        source_type=(
                            CitationType.VEHICLE
                        ),
                        vehicle_id=vehicle.id,
                        title=(
                            f"{vehicle.make} "
                            f"{vehicle.model}"
                        ),
                    )
                )

                total_chars += len(block)
                vehicles_included += 1

        # ---------------------------------
        # Unstructured document evidence
        # ---------------------------------

        if (
            document_results is not None
            and not budget_exhausted
        ):
            seen_chunks: set[object] = set()

            for item in document_results.items:
                if (
                    document_chunks_included
                    >= settings
                    .context_max_document_chunks
                ):
                    break

                if item.chunk_id in seen_chunks:
                    continue

                seen_chunks.add(item.chunk_id)

                content = item.content.strip()

                was_truncated = False

                if (
                    len(content)
                    > settings.context_max_chunk_chars
                ):
                    content = (
                        content[
                            : settings.context_max_chunk_chars
                        ].rstrip()
                        + "..."
                    )

                    was_truncated = True

                citation = (
                    f"[document:{item.document_id}"
                    f"#chunk_{item.chunk_index}]"
                )

                block = self._document_block(
                    citation=citation,
                    title=item.title,
                    document_type=(
                        item.document_type
                    ),
                    content=content,
                )

                if (
                    total_chars + len(block)
                    > settings.context_max_chars
                ):
                    budget_exhausted = True
                    break

                blocks.append(block)

                citations.append(
                    CitationRecord(
                        citation=citation,
                        source_type=(
                            CitationType.DOCUMENT
                        ),
                        document_id=(
                            item.document_id
                        ),
                        chunk_id=item.chunk_id,
                        chunk_index=(
                            item.chunk_index
                        ),
                        title=item.title,
                    )
                )

                total_chars += len(block)
                document_chunks_included += 1

                if was_truncated:
                    truncated_chunks += 1

        context_text = "\n\n".join(blocks)

        return ContextPackage(
            text=context_text,
            citations=citations,
            has_evidence=bool(blocks),
            stats=ContextStats(
                vehicle_candidates=(
                    vehicle_candidates
                ),
                vehicles_included=(
                    vehicles_included
                ),
                document_candidates=(
                    document_candidates
                ),
                document_chunks_included=(
                    document_chunks_included
                ),
                total_characters=(
                    len(context_text)
                ),
                truncated_document_chunks=(
                    truncated_chunks
                ),
                budget_exhausted=(
                    budget_exhausted
                ),
            ),
        )

    @staticmethod
    def _vehicle_block(
        *,
        vehicle,
        citation: str,
    ) -> str:
        equipment = ", ".join(
            vehicle.equipment
        )

        rating = (
            str(vehicle.dealer.rating)
            if vehicle.dealer.rating is not None
            else "unknown"
        )

        price_eur = (
            Decimal(vehicle.price.amount_minor)
            / Decimal(100)
        )

        return (
            "<vehicle_evidence>\n"
            f"CITATION: {citation}\n"
            f"VEHICLE_ID: {vehicle.id}\n"
            f"MAKE: {vehicle.make}\n"
            f"MODEL: {vehicle.model}\n"
            f"VARIANT: {vehicle.variant or 'unknown'}\n"
            f"PRICE_EUR: {price_eur:.2f}\n"
            f"YEAR: {vehicle.year}\n"
            f"MILEAGE_KM: {vehicle.mileage_km}\n"
            f"FUEL_TYPE: {vehicle.fuel_type}\n"
            f"TRANSMISSION: "
            f"{vehicle.transmission}\n"
            f"BODY_TYPE: {vehicle.body_type}\n"
            f"POWER_KW: "
            f"{vehicle.power_kw or 'unknown'}\n"
            f"EQUIPMENT: {equipment}\n"
            f"DEALER_ID: {vehicle.dealer.id}\n"
            f"DEALER_NAME: "
            f"{vehicle.dealer.name}\n"
            f"DEALER_CITY: "
            f"{vehicle.dealer.city}\n"
            f"DEALER_RATING: {rating}\n"
            f"DEALER_VERIFIED: "
            f"{vehicle.dealer.is_verified}\n"
            f"DEALER_WARRANTY_MONTHS: "
            f"{vehicle.dealer.warranty_months}\n"
            "</vehicle_evidence>"
        )

    @staticmethod
    def _document_block(
        *,
        citation: str,
        title: str,
        document_type: str,
        content: str,
    ) -> str:
        return (
            "<document_evidence>\n"
            f"CITATION: {citation}\n"
            f"TITLE: {title}\n"
            f"DOCUMENT_TYPE: {document_type}\n"
            "CONTENT_BEGIN\n"
            f"{content}\n"
            "CONTENT_END\n"
            "</document_evidence>"
        )