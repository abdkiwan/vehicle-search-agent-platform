from pydantic import BaseModel, Field


class ModelUsageMetric(BaseModel):
    operation: str

    model_id: str

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    estimated_cost_usd: float | None = None


class CacheMetrics(BaseModel):
    hits: int = 0
    misses: int = 0
    errors: int = 0


class TelemetrySummary(BaseModel):
    request_id: str

    total_latency_ms: float

    stage_latency_ms: dict[str, float] = Field(
        default_factory=dict
    )

    model_calls: list[ModelUsageMetric] = Field(
        default_factory=list
    )

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0

    estimated_cost_usd: float | None = None

    cost_estimation_complete: bool = False

    cache: CacheMetrics