import asyncio
import json

import boto3

from app.config import settings


class BedrockEmbeddingService:
    def __init__(self) -> None:
        session = boto3.Session(
            profile_name=settings.aws_profile,
            region_name=settings.aws_region,
        )
        self._client = session.client("bedrock-runtime")

    def _embed_sync(
        self,
        text: str,
    ) -> list[float]:
        response = self._client.invoke_model(
            modelId=settings.bedrock_embedding_model_id,
            contentType="application/json",
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

        embedding = payload["embedding"]

        if len(embedding) != 1024:
            raise ValueError(
                f"Unexpected embedding dimension: "
                f"{len(embedding)}"
            )

        return embedding

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        return await asyncio.to_thread(
            self._embed_sync,
            text,
        )