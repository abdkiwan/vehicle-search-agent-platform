from app.agent.routing import (
    route_after_context_security,
    route_after_input_security,
)
from app.schemas.security import (
    PromptSecurityResult,
    PromptSecuritySource,
)


def test_safe_input_continues_to_planner():
    state = {
        "input_security":
            PromptSecurityResult(
                allowed=True,
                source=(
                    PromptSecuritySource
                    .USER_INPUT
                ),
                action="NONE",
            )
    }

    assert (
        route_after_input_security(
            state
        )
        == "plan"
    )


def test_prompt_attack_is_blocked():
    state = {
        "input_security":
            PromptSecurityResult(
                allowed=False,
                source=(
                    PromptSecuritySource
                    .USER_INPUT
                ),
                action=(
                    "GUARDRAIL_INTERVENED"
                ),
                prompt_attack_detected=True,
                confidence="HIGH",
            )
    }

    assert (
        route_after_input_security(
            state
        )
        == "blocked"
    )


def test_safe_context_reaches_generator():
    state = {
        "context_security":
            PromptSecurityResult(
                allowed=True,
                source=(
                    PromptSecuritySource
                    .RETRIEVED_CONTEXT
                ),
                action="NONE",
            )
    }

    assert (
        route_after_context_security(
            state
        )
        == "generate"
    )


def test_malicious_context_is_blocked():
    state = {
        "context_security":
            PromptSecurityResult(
                allowed=False,
                source=(
                    PromptSecuritySource
                    .RETRIEVED_CONTEXT
                ),
                action=(
                    "GUARDRAIL_INTERVENED"
                ),
                prompt_attack_detected=True,
            )
    }

    assert (
        route_after_context_security(
            state
        )
        == "blocked"
    )