from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.repositories.document_repository import (
    DocumentRepository,
)
from app.repositories.vehicle_repository import (
    VehicleRepository,
)
from app.retrieval.embeddings import (
    BedrockEmbeddingService,
)
from app.schemas.document_search import (
    DocumentSearchResponse,
    UserRole,
)
from app.schemas.query_plan import (
    DocumentScope,
    QueryPlan,
    SearchRoute,
    UnifiedSearchResponse,
)
from app.services.document_search import (
    DocumentSearchService,
)
from app.services.vehicle_search import (
    VehicleSearchService,
)


class SearchRouterService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._vehicle_search = (
            VehicleSearchService(
                VehicleRepository(session)
            )
        )

        self._document_search = (
            DocumentSearchService(
                repository=DocumentRepository(
                    session
                ),
                embeddings=(
                    BedrockEmbeddingService()
                ),
            )
        )

    async def execute(
        self,
        *,
        original_query: str,
        plan: QueryPlan,
        role: UserRole,
    ) -> UnifiedSearchResponse:
        structured_results = None
        document_results = None

        if plan.route == SearchRoute.UNSUPPORTED:
            return UnifiedSearchResponse(
                query=original_query,
                plan=plan,
            )

        if plan.route in {
            SearchRoute.STRUCTURED,
            SearchRoute.HYBRID,
        }:
            if plan.vehicle_search is None:
                raise ValueError(
                    "Vehicle search plan missing"
                )

            structured_results = (
                await self._vehicle_search.search(
                    plan.vehicle_search
                )
            )

        if plan.route in {
            SearchRoute.UNSTRUCTURED,
            SearchRoute.HYBRID,
        }:
            if plan.document_search is None:
                raise ValueError(
                    "Document search plan missing"
                )

            document_request = (
                plan.document_search
            )

            if (
                plan.route
                == SearchRoute.HYBRID
                and structured_results
                is not None
            ):
                if (
                    plan.document_scope
                    == DocumentScope
                    .MATCHED_DEALERS
                ):
                    dealer_ids = list(
                        {
                            item.dealer.id
                            for item
                            in structured_results.items
                        }
                    )

                    if not dealer_ids:
                        document_results = (
                            DocumentSearchResponse(
                                query=(
                                    document_request
                                    .query
                                ),
                                items=[],
                                returned=0,
                            )
                        )

                        return UnifiedSearchResponse(
                            query=original_query,
                            plan=plan,
                            structured_results=(
                                structured_results
                            ),
                            document_results=(
                                document_results
                            ),
                        )

                    document_request = (
                        document_request.model_copy(
                            update={
                                "dealer_ids": (
                                    dealer_ids
                                )
                            }
                        )
                    )

                elif (
                    plan.document_scope
                    == DocumentScope
                    .MATCHED_VEHICLES
                ):
                    vehicle_ids = [
                        item.id
                        for item
                        in structured_results.items
                    ]

                    if not vehicle_ids:
                        document_results = (
                            DocumentSearchResponse(
                                query=(
                                    document_request
                                    .query
                                ),
                                items=[],
                                returned=0,
                            )
                        )

                        return UnifiedSearchResponse(
                            query=original_query,
                            plan=plan,
                            structured_results=(
                                structured_results
                            ),
                            document_results=(
                                document_results
                            ),
                        )

                    document_request = (
                        document_request.model_copy(
                            update={
                                "vehicle_ids": (
                                    vehicle_ids
                                )
                            }
                        )
                    )

            document_results = (
                await self._document_search.search(
                    request=document_request,
                    role=role,
                )
            )

        return UnifiedSearchResponse(
            query=original_query,
            plan=plan,
            structured_results=(
                structured_results
            ),
            document_results=(
                document_results
            ),
        )