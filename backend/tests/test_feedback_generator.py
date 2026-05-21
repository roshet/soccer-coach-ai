import pytest
from unittest.mock import MagicMock, patch
from services.feedback_generator import generate_feedback
from services.biomechanics.base import BiomechanicsResult

SAMPLE_RESULT = BiomechanicsResult(
    technique="shooting_driven",
    scores={
        "plant_foot_position": 58,
        "knee_over_ball": 82,
        "hip_rotation": 71,
        "body_lean": 90,
        "follow_through": 65,
    },
    flags=["Plant foot too far from ball", "Follow-through cuts off early"],
    overall_score=73,
)


def test_generate_feedback_returns_string():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Great shot mechanics. Work on your plant foot.")]
    mock_client.messages.create.return_value = mock_message

    result = generate_feedback(SAMPLE_RESULT, client=mock_client)
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_feedback_calls_claude_with_technique_context():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Your technique analysis...")]
    mock_client.messages.create.return_value = mock_message

    generate_feedback(SAMPLE_RESULT, client=mock_client)

    call_kwargs = mock_client.messages.create.call_args
    prompt_text = str(call_kwargs)
    assert "shooting" in prompt_text.lower() or "73" in prompt_text


def test_generate_feedback_returns_none_on_api_error():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("API timeout")

    result = generate_feedback(SAMPLE_RESULT, client=mock_client)
    assert result is None  # Caller handles None as 206 partial response
