from app.config import settings


def calculate_token_cost(
    *,
    input_tokens: int,
    output_tokens: int,
    input_usd_per_million:
        float | None,
    output_usd_per_million:
        float | None,
) -> float | None:

    if (
        input_usd_per_million is None
        or output_usd_per_million is None
    ):
        return None

    cost = (
        input_tokens
        / 1_000_000
        * input_usd_per_million
    )

    cost += (
        output_tokens
        / 1_000_000
        * output_usd_per_million
    )

    return round(
        cost,
        10,
    )


def estimate_converse_cost(
    *,
    model_id: str,
    input_tokens: int,
    output_tokens: int,
) -> float | None:

    if "nova-lite" in model_id:
        return calculate_token_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_usd_per_million=(
                settings
                .bedrock_nova_lite_input_usd_per_million_tokens
            ),
            output_usd_per_million=(
                settings
                .bedrock_nova_lite_output_usd_per_million_tokens
            ),
        )

    if "nova-pro" in model_id:
        return calculate_token_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_usd_per_million=(
                settings
                .bedrock_nova_pro_input_usd_per_million_tokens
            ),
            output_usd_per_million=(
                settings
                .bedrock_nova_pro_output_usd_per_million_tokens
            ),
        )

    return None


def estimate_embedding_cost(
    *,
    input_tokens: int,
) -> float | None:

    rate = (
        settings
        .bedrock_titan_embed_input_usd_per_million_tokens
    )

    if rate is None:
        return None

    return round(
        input_tokens
        / 1_000_000
        * rate,
        10,
    )