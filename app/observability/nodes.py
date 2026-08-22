from functools import wraps


def observed_stage(
    name: str,
):
    def decorator(
        function,
    ):
        @wraps(function)
        async def wrapper(
            state,
            runtime,
        ):
            with (
                runtime.context
                .telemetry
                .stage(name)
            ):
                return await function(
                    state,
                    runtime,
                )

        return wrapper

    return decorator