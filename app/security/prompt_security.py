import asyncio

import boto3

from app.config import settings
from app.schemas.security import (
    PromptSecurityResult,
    PromptSecuritySource,
)


class PromptSecurityError(RuntimeError):
    pass


class PromptInjectionService:
    def __init__(self) -> None:
        session = boto3.Session(
            profile_name=settings.aws_profile,
            region_name=settings.aws_region,
        )
        self._client = session.client(
            "bedrock-runtime"
        )

    def _assess_sync(
        self,
        *,
        text: str,
        source: PromptSecuritySource,
    ) -> PromptSecurityResult:

        response = (
            self._client.apply_guardrail(
                guardrailIdentifier=(
                    settings
                    .bedrock_security_guardrail_id
                ),
                guardrailVersion=(
                    settings
                    .bedrock_security_guardrail_version
                ),
                source="INPUT",
                outputScope="FULL",
                content=[
                    {
                        "text": {
                            "text": text,
                        }
                    }
                ],
            )
        )

        prompt_attack_detected = False
        confidence = None

        for assessment in response.get(
            "assessments",
            [],
        ):
            policy = assessment.get(
                "contentPolicy",
                {},
            )

            for item in policy.get(
                "filters",
                [],
            ):
                if (
                    item.get("type")
                    != "PROMPT_ATTACK"
                ):
                    continue

                confidence = item.get(
                    "confidence"
                )

                if (
                    item.get("action")
                    == "BLOCKED"
                ):
                    prompt_attack_detected = (
                        True
                    )

        action = response.get(
            "action",
            "NONE",
        )

        blocked = (
            action
            == "GUARDRAIL_INTERVENED"
            or prompt_attack_detected
        )

        return PromptSecurityResult(
            allowed=not blocked,
            source=source,
            action=action,
            prompt_attack_detected=(
                prompt_attack_detected
            ),
            confidence=confidence,
        )

    async def assess(
        self,
        *,
        text: str,
        source: PromptSecuritySource,
    ) -> PromptSecurityResult:

        if not text.strip():
            return PromptSecurityResult(
                allowed=True,
                source=source,
                action="SKIPPED",
            )

        return await asyncio.to_thread(
            self._assess_sync,
            text=text,
            source=source,
        )