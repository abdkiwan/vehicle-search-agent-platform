import asyncio
import re

import boto3

from app.config import settings
from app.schemas.answer import (
    AnswerStatus,
    AnswerValidationResult,
    CitationValidationResult,
    FinalAnswer,
    GeneratedAnswer,
    GroundingValidationResult,
)
from app.schemas.context import ContextPackage

CITATION_PATTERN = re.compile(
    r"\[(?:vehicle|document):[^\]]+\]"
)


class CitationValidator:
    def validate(
        self,
        *,
        answer: GeneratedAnswer,
        context: ContextPackage,
    ) -> CitationValidationResult:

        allowed = {
            citation.citation
            for citation in context.citations
        }

        declared = set(
            answer.citations_used
        )

        found_in_text = set(
            CITATION_PATTERN.findall(
                answer.answer
            )
        )

        # A citation is dangerous only if the model
        # invented one that was not in the context.
        invalid = sorted(
            found_in_text - allowed
        )

        undeclared = sorted(
            found_in_text - declared
        )

        missing_from_text = sorted(
            declared - found_in_text
        )

        passed = not invalid

        # A factual answer must contain at least
        # one real inline citation.
        if (
            answer.status
            == AnswerStatus.ANSWERED
            and not found_in_text
        ):
            passed = False

        return CitationValidationResult(
            passed=passed,
            citations_used=sorted(
                found_in_text
            ),
            invalid_citations=invalid,
            undeclared_citations=undeclared,
            missing_from_text=(
                missing_from_text
            ),
        )
        
class BedrockGroundingValidator:
    def __init__(self) -> None:
        session = boto3.Session(
            profile_name=settings.aws_profile,
            region_name=settings.aws_region,
        )
        self._client = session.client(
            "bedrock-runtime"
        )

    def _validate_sync(
        self,
        *,
        query: str,
        context: ContextPackage,
        answer: str,
    ) -> GroundingValidationResult:

        response = self._client.apply_guardrail(
            guardrailIdentifier=(
                settings
                .bedrock_grounding_guardrail_id
            ),
            guardrailVersion=(
                settings
                .bedrock_grounding_guardrail_version
            ),
            source="OUTPUT",
            outputScope="FULL",
            content=[
                {
                    "text": {
                        "text": context.text,
                        "qualifiers": [
                            "grounding_source"
                        ],
                    }
                },
                {
                    "text": {
                        "text": query[:1000],
                        "qualifiers": [
                            "query"
                        ],
                    }
                },
                {
                    "text": {
                        "text": answer[:5000],
                        "qualifiers": [
                            "guard_content"
                        ],
                    }
                },
            ],
        )

        grounding_score = None
        relevance_score = None

        grounding_detected = None
        relevance_detected = None

        for assessment in response.get(
            "assessments",
            [],
        ):
            policy = assessment.get(
                "contextualGroundingPolicy",
                {},
            )

            for item in policy.get(
                "filters",
                [],
            ):
                filter_type = item.get(
                    "type"
                )

                if filter_type == "GROUNDING":
                    grounding_score = item.get(
                        "score"
                    )

                    grounding_detected = (
                        item.get(
                            "detected",
                            False,
                        )
                    )

                elif filter_type == "RELEVANCE":
                    relevance_score = item.get(
                        "score"
                    )

                    relevance_detected = (
                        item.get(
                            "detected",
                            False,
                        )
                    )

        evaluated = (
            grounding_score is not None
            and relevance_score is not None
        )

        if not evaluated:
            return GroundingValidationResult(
                evaluated=False,
                passed=False,
            )

        grounded = not bool(
            grounding_detected
        )

        relevant = not bool(
            relevance_detected
        )

        return GroundingValidationResult(
            evaluated=True,
            grounding_score=(
                grounding_score
            ),
            relevance_score=(
                relevance_score
            ),
            grounded=grounded,
            relevant=relevant,
            passed=(
                grounded and relevant
            ),
        )

    async def validate(
        self,
        *,
        query: str,
        context: ContextPackage,
        answer: str,
    ) -> GroundingValidationResult:

        return await asyncio.to_thread(
            self._validate_sync,
            query=query,
            context=context,
            answer=answer,
        )

class AnswerValidationService:
    def __init__(self) -> None:
        self._citation_validator = (
            CitationValidator()
        )

        self._grounding_validator = (
            BedrockGroundingValidator()
        )

    async def finalize(
        self,
        *,
        query: str,
        generated: GeneratedAnswer,
        context: ContextPackage,
    ) -> FinalAnswer:

        # ---------------------------------
        # No factual answer was generated.
        # ---------------------------------

        if (
            generated.status
            != AnswerStatus.ANSWERED
        ):
            citation_result = (
                self._citation_validator
                .validate(
                    answer=generated,
                    context=context,
                )
            )

            return FinalAnswer(
                status=generated.status,
                answer=generated.answer,
                citations=[],
                validation=(
                    AnswerValidationResult(
                        passed=True,
                        citation_validation=(
                            citation_result
                        ),
                        grounding_validation=(
                            GroundingValidationResult(
                                evaluated=False,
                                passed=True,
                            )
                        ),
                        issues=[],
                    )
                ),
            )

        # ---------------------------------
        # Citation validation
        # ---------------------------------

        citation_result = (
            self._citation_validator.validate(
                answer=generated,
                context=context,
            )
        )

        if not citation_result.passed:
            return self._failed_answer(
                citation_result=(
                    citation_result
                ),
                grounding_result=(
                    GroundingValidationResult(
                        evaluated=False,
                        passed=False,
                    )
                ),
                issues=[
                    "Generated answer contained "
                    "invalid or inconsistent "
                    "citations."
                ],
            )

        # ---------------------------------
        # Semantic grounding validation
        # ---------------------------------

        grounding_result = (
            await self._grounding_validator
            .validate(
                query=query,
                context=context,
                answer=generated.answer,
            )
        )

        if not grounding_result.passed:
            return self._failed_answer(
                citation_result=(
                    citation_result
                ),
                grounding_result=(
                    grounding_result
                ),
                issues=[
                    "Generated answer did not "
                    "pass contextual grounding "
                    "validation."
                ],
            )

        # ---------------------------------
        # Valid answer
        # ---------------------------------

        return FinalAnswer(
            status=AnswerStatus.ANSWERED,
            answer=generated.answer,
            citations=(
                citation_result
                .citations_used
            ),
            validation=(
                AnswerValidationResult(
                    passed=True,
                    citation_validation=(
                        citation_result
                    ),
                    grounding_validation=(
                        grounding_result
                    ),
                    issues=[],
                )
            ),
        )

    @staticmethod
    def _failed_answer(
        *,
        citation_result:
            CitationValidationResult,
        grounding_result:
            GroundingValidationResult,
        issues: list[str],
    ) -> FinalAnswer:

        return FinalAnswer(
            status=(
                AnswerStatus
                .VALIDATION_FAILED
            ),
            answer=(
                "I found potentially relevant "
                "information, but I couldn't "
                "verify a sufficiently grounded "
                "answer from the retrieved "
                "evidence."
            ),
            citations=[],
            validation=(
                AnswerValidationResult(
                    passed=False,
                    citation_validation=(
                        citation_result
                    ),
                    grounding_validation=(
                        grounding_result
                    ),
                    issues=issues,
                )
            ),
        )