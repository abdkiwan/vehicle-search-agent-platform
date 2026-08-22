from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vehicle Search Agent Platform"
    app_env: str = "development"

    database_url: str
    db_pool_size: int = 5
    db_max_overflow: int = 5

    aws_region: str = "eu-central-1"
    aws_profile: str = "personal"
    bedrock_embedding_model_id: str = (
        "amazon.titan-embed-text-v2:0"
    )

    bedrock_planner_model_id: str = (
        "eu.amazon.nova-lite-v1:0"
    )

    bedrock_planner_max_tokens: int = 800

    hybrid_candidate_limit: int = 15
    hybrid_default_result_limit: int = 5
    rrf_k: int = 60

    context_max_vehicles: int = 8
    context_max_document_chunks: int = 5
    context_max_chars: int = 14000
    context_max_chunk_chars: int = 1600

    bedrock_answer_model_id: str = (
        "eu.amazon.nova-pro-v1:0"
    )
    bedrock_answer_max_tokens: int = 900

    bedrock_grounding_guardrail_id: str
    bedrock_grounding_guardrail_version: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cognito_user_pool_id: str
    cognito_app_client_id: str

    bedrock_security_guardrail_id: str
    bedrock_security_guardrail_version: str

    cache_enabled: bool = True

    redis_url: str = (
        "redis://localhost:6379/0"
    )

    redis_socket_timeout_seconds: float = 0.5

    planner_cache_ttl_seconds: int = 3600

    embedding_cache_ttl_seconds: int = 86400

    cache_key_version: str = "v1"

    planner_prompt_version: str = "v1"

    bedrock_nova_lite_input_usd_per_million_tokens: (
        float | None
    ) = None

    bedrock_nova_lite_output_usd_per_million_tokens: (
        float | None
    ) = None

    bedrock_nova_pro_input_usd_per_million_tokens: (
        float | None
    ) = None

    bedrock_nova_pro_output_usd_per_million_tokens: (
        float | None
    ) = None

    bedrock_titan_embed_input_usd_per_million_tokens: (
        float | None
    ) = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
