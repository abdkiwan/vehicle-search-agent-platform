from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import Lock
from time import perf_counter

from app.schemas.telemetry import (
    CacheMetrics,
    ModelUsageMetric,
    TelemetrySummary,
)


@dataclass
class RunTelemetry:
    request_id: str

    _started_at: float = field(
        default_factory=perf_counter,
        init=False,
    )

    _stage_latency_ms: dict[str, float] = field(
        default_factory=dict,
        init=False,
    )

    _model_calls: list[ModelUsageMetric] = field(
        default_factory=list,
        init=False,
    )

    _cache_hits: int = field(
        default=0,
        init=False,
    )

    _cache_misses: int = field(
        default=0,
        init=False,
    )

    _cache_errors: int = field(
        default=0,
        init=False,
    )

    _lock: Lock = field(
        default_factory=Lock,
        init=False,
        repr=False,
    )

    @contextmanager
    def stage(
        self,
        name: str,
    ):
        started = perf_counter()

        try:
            yield

        finally:
            duration_ms = (
                perf_counter()
                - started
            ) * 1000

            with self._lock:
                previous = (
                    self._stage_latency_ms
                    .get(
                        name,
                        0.0,
                    )
                )

                self._stage_latency_ms[
                    name
                ] = (
                    previous
                    + duration_ms
                )

    def record_model_usage(
        self,
        *,
        operation: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost_usd:
            float | None,
    ) -> None:

        metric = ModelUsageMetric(
            operation=operation,
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=(
                input_tokens
                + output_tokens
            ),
            estimated_cost_usd=(
                estimated_cost_usd
            ),
        )

        with self._lock:
            self._model_calls.append(
                metric
            )

    def record_cache_hit(
        self,
    ) -> None:
        with self._lock:
            self._cache_hits += 1

    def record_cache_miss(
        self,
    ) -> None:
        with self._lock:
            self._cache_misses += 1

    def record_cache_error(
        self,
    ) -> None:
        with self._lock:
            self._cache_errors += 1

    def snapshot(
        self,
    ) -> TelemetrySummary:

        with self._lock:
            model_calls = list(
                self._model_calls
            )

            stage_latency = {
                key: round(
                    value,
                    2,
                )
                for key, value
                in self
                ._stage_latency_ms
                .items()
            }

            cache = CacheMetrics(
                hits=self._cache_hits,
                misses=self._cache_misses,
                errors=self._cache_errors,
            )

        total_input = sum(
            item.input_tokens
            for item in model_calls
        )

        total_output = sum(
            item.output_tokens
            for item in model_calls
        )

        known_costs = [
            item.estimated_cost_usd
            for item in model_calls
            if (
                item.estimated_cost_usd
                is not None
            )
        ]

        if (
            model_calls
            and len(known_costs)
            == len(model_calls)
        ):
            estimated_cost = round(
                sum(known_costs),
                10,
            )

            cost_complete = True

        elif not model_calls:
            estimated_cost = 0.0
            cost_complete = True

        else:
            estimated_cost = (
                round(
                    sum(known_costs),
                    10,
                )
                if known_costs
                else None
            )

            cost_complete = False

        total_latency_ms = (
            perf_counter()
            - self._started_at
        ) * 1000

        return TelemetrySummary(
            request_id=self.request_id,

            total_latency_ms=round(
                total_latency_ms,
                2,
            ),

            stage_latency_ms=(
                stage_latency
            ),

            model_calls=model_calls,

            total_input_tokens=(
                total_input
            ),

            total_output_tokens=(
                total_output
            ),

            total_tokens=(
                total_input
                + total_output
            ),

            estimated_cost_usd=(
                estimated_cost
            ),

            cost_estimation_complete=(
                cost_complete
            ),

            cache=cache,
        )