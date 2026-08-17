from app.agent.state import AgentState
from app.schemas.answer import (
    AnswerStatus,
    AnswerValidationResult,
    CitationValidationResult,
    FinalAnswer,
    GroundingValidationResult,
)


async def reject_security_request(
    state: AgentState,
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