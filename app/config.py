from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vehicle Search Agent Platform"
    app_env: str = "development"

    database_url: str
    db_pool_size: int = 5
    db_max_overflow: int = 5

    aws_region: str = "eu-central-1"
    aws_profile: str | None = None
    bedrock_embedding_model_id: str = (
        "amazon.titan-embed-text-v2:0"
    )

    bedrock_planner_model_id: str = (
        "eu.amazon.nova-lite-v1:0"
    )

    bedrock_planner_max_tokens: int = 3000

    hybrid_candidate_limit: int = 15
    hybrid_default_result_limit: int = 5
    rrf_k: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
