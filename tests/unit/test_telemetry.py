from app.observability.telemetry import (
    RunTelemetry,
)


def test_model_usage_is_accumulated():
    telemetry = RunTelemetry(
        request_id="request-123"
    )

    telemetry.record_model_usage(
        operation="planner",
        model_id="model-a",
        input_tokens=100,
        output_tokens=20,
        estimated_cost_usd=0.001,
    )

    telemetry.record_model_usage(
        operation="answer",
        model_id="model-b",
        input_tokens=300,
        output_tokens=80,
        estimated_cost_usd=0.005,
    )

    result = telemetry.snapshot()

    assert (
        result.total_input_tokens
        == 400
    )

    assert (
        result.total_output_tokens
        == 100
    )

    assert (
        result.total_tokens
        == 500
    )

    assert (
        result.estimated_cost_usd
        == 0.006
    )

    assert (
        result.cost_estimation_complete
        is True
    )


def test_cache_metrics_are_accumulated():
    telemetry = RunTelemetry(
        request_id="request-123"
    )

    telemetry.record_cache_hit()
    telemetry.record_cache_hit()

    telemetry.record_cache_miss()

    telemetry.record_cache_error()

    result = telemetry.snapshot()

    assert result.cache.hits == 2
    assert result.cache.misses == 1
    assert result.cache.errors == 1