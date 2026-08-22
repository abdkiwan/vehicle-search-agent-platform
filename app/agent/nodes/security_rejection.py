from app.agent.state import AgentState
from langgraph.runtime import Runtime
from app.agent.context import (
    AgentRuntimeContext,
)
from app.schemas.answer import (
    AnswerStatus,
    AnswerValidationResult,
    CitationValidationResult,
    FinalAnswer,
    GroundingValidationResult,
)
from app.observability.nodes import (
    observed_stage,
)


@observed_stage("reject_security_request")
async def reject_security_request(
    state: AgentState,
    runtime: Runtime[AgentRuntimeContext],
) -> dict:

    return {
        "final_answer": FinalAnswer(
            status=(
                AnswerStatus.SECURITY_BLOCKED
            ),
            answer=(
                "I can't process this request "
                "because it was rejected by the "
                "input security policy."
            ),
            citations=[],
            validation=(
                AnswerValidationResult(
                    passed=False,
                    citation_validation=(
                        CitationValidationResult(
                            passed=True,
                            citations_used=[],
                            invalid_citations=[],
                            undeclared_citations=[],
                            missing_from_text=[],
                        )
                    ),
                    grounding_validation=(
                        GroundingValidationResult(
                            evaluated=False,
                            passed=True,
                        )
                    ),
                    issues=[
                        (
                            "Request rejected by "
                            "prompt-injection "
                            "protection."
                        )
                    ],
                )
            ),
        )
    }