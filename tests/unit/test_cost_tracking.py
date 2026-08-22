from app.observability.costs import (
    calculate_token_cost,
)


def test_token_cost_calculation():
    cost = calculate_token_cost(
        input_tokens=1_000_000,
        output_tokens=500_000,
        input_usd_per_million=1.0,
        output_usd_per_million=2.0,
    )

    assert cost == 2.0


def test_cost_is_none_when_rates_missing():
    cost = calculate_token_cost(
        input_tokens=1000,
        output_tokens=100,
        input_usd_per_million=None,
        output_usd_per_million=None,
    )

    assert cost is None