import asyncio
import json

import boto3

from app.cache.redis_cache import (
    RedisCache,
)
from app.config import settings
from app.observability.costs import (
    estimate_embedding_cost,
)
from app.observability.telemetry import (
    RunTelemetry,
)


class BedrockEmbeddingService:
    def __init__(
        self,
        *,
        cache: RedisCache | None = None,
        telemetry: RunTelemetry | None = None,
    ) -> None:

        self._client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
        )

        self._cache = cache
        self._telemetry = telemetry

    def _embed_sync(
        self,
        text: str,
    ) -> list[float]:

        response = self._client.invoke_model(
            modelId=(
                settings
                .bedrock_embedding_model_id
            ),
            contentType=(
                "application/json"
            ),
            accept="application/json",
            body=json.dumps(
                {
                    "inputText": text,
                    "dimensions": 1024,
                    "normalize": True,
                }
            ),
        )

        payload = json.loads(
            response["body"].read()
        )

        embedding = payload[
            "embedding"
        ]

        if len(embedding) != 1024:
            raise ValueError(
                "Unexpected embedding "
                f"dimension: {len(embedding)}"
            )

        input_tokens = int(
            payload.get(
                "inputTextTokenCount",
                0,
            )
        )

        if self._telemetry:
            self._telemetry.record_model_usage(
                operation=(
                    "query_embedding"
                ),
                model_id=(
                    settings
                    .bedrock_embedding_model_id
                ),
                input_tokens=(
                    input_tokens
                ),
                output_tokens=0,
                estimated_cost_usd=(
                    estimate_embedding_cost(
                        input_tokens=(
                            input_tokens
                        )
                    )
                ),
            )

        return embedding

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        normalized_text = " ".join(
            text.split()
        )

        cache_key = None

        if self._cache is not None:
            cache_key = (
                self._cache.build_key(
                    "embedding",
                    {
                        "text": (
                            normalized_text
                        ),
                        "model": (
                            settings
                            .bedrock_embedding_model_id
                        ),
                        "dimensions": 1024,
                        "normalize": True,
                    },
                    version=(
                        settings
                        .cache_key_version
                    ),
                )
            )

            cached = (
                await self._cache.get_json(
                    cache_key,
                    telemetry=self._telemetry,
                )
            )

            if (
                isinstance(
                    cached,
                    list,
                )
                and len(cached) == 1024
            ):
                return [
                    float(value)
                    for value in cached
                ]

        embedding = await asyncio.to_thread(
            self._embed_sync,
            normalized_text,
        )

        if (
            self._cache is not None
            and cache_key is not None
        ):
            await self._cache.set_json(
                cache_key,
                embedding,
                ttl_seconds=(
                    settings
                    .embedding_cache_ttl_seconds
                ),
                telemetry=self._telemetry,
            )

        return embedding