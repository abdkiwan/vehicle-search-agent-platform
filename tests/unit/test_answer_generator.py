from unittest.mock import MagicMock, patch

from app.schemas.context import (
    ContextPackage,
    ContextStats,
)
from app.services.answer_generator import (
    GroundedAnswerService,
)


def _make_context(*, text: str) -> ContextPackage:
    return ContextPackage(
        text=text,
        citations=[],
        stats=ContextStats(),
        has_evidence=bool(text.strip()),
    )


def _make_service(
    mock_client: MagicMock,
) -> GroundedAnswerService:
    with patch(
        "app.services.answer_generator.boto3.Session"
    ) as mock_session:
        mock_session.return_value.client.return_value = (
            mock_client
        )
        return GroundedAnswerService()


def test_init_uses_aws_profile_and_region():
    mock_client = MagicMock()

    with patch(
        "app.services.answer_generator.boto3.Session"
    ) as mock_session:
        mock_session.return_value.client.return_value = (
            mock_client
        )
        with patch(
            "app.services.answer_generator.settings"
        ) as mock_settings:
            mock_settings.aws_profile = "personal"
            mock_settings.aws_region = "eu-central-1"

            service = GroundedAnswerService()

    mock_session.assert_called_once_with(
        profile_name="personal",
        region_name="eu-central-1",
    )
    mock_session.return_value.client.assert_called_once_with(
        "bedrock-runtime"
    )
    assert service._client is mock_client


def test_invoke_model_builds_user_message_without_feedback():
    mock_client = MagicMock()
    mock_client.converse.return_value = {"output": {}}
    service = _make_service(mock_client)

    service._invoke_model(
        query="What is the mileage?",
        context=_make_context(
            text="mileage is 62000 km"
        ),
        validation_feedback=None,
    )

    kwargs = mock_client.converse.call_args.kwargs
    user_text = (
        kwargs["messages"][0]["content"][0]["text"]
    )
    system_text = kwargs["system"][0]["text"]

    assert "<user_query>" in user_text
    assert "What is the mileage?" in user_text
    assert "mileage is 62000 km" in user_text
    assert "Validation error:" not in system_text


def test_invoke_model_appends_validation_feedback():
    mock_client = MagicMock()
    mock_client.converse.return_value = {"output": {}}
    service = _make_service(mock_client)

    service._invoke_model(
        query="What is the price?",
        context=_make_context(text="price is 18990"),
        validation_feedback="Missing citations.",
    )

    kwargs = mock_client.converse.call_args.kwargs
    user_text = (
        kwargs["messages"][0]["content"][0]["text"]
    )
    system_text = kwargs["system"][0]["text"]

    assert "What is the price?" in user_text
    assert "price is 18990" in user_text
    assert "Missing citations." in system_text
    assert "Validation error:" in system_text
