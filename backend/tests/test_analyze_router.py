import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from services.biomechanics.base import BiomechanicsResult

client = TestClient(app)

MOCK_RESULT = BiomechanicsResult(
    technique="shooting_driven",
    scores={"plant_foot_position": 80, "knee_over_ball": 75, "hip_rotation": 70,
            "body_lean": 85, "follow_through": 72},
    flags=[],
    overall_score=76,
)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_returns_200_with_valid_input(temp_video_path):
    with (
        patch("routers.analyze.extract_frames", return_value=[None] * 10),
        patch("routers.analyze.estimate_poses", return_value=[{}] * 10),
        patch("routers.analyze.analyze_shooting", return_value=MOCK_RESULT),
        patch("routers.analyze.find_contact_frame_idx", return_value=5),
        patch("routers.analyze.generate_feedback", return_value="Great technique!"),
        patch("routers.analyze.get_annotated_frames", return_value=["base64abc"]),
    ):
        with open(temp_video_path, "rb") as f:
            response = client.post(
                "/analyze",
                data={"technique": "shooting_driven", "kicking_foot": "right"},
                files={"video": ("test.mp4", f, "video/mp4")},
            )
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "scores" in data
    assert "coaching_report" in data
    assert "annotated_frames" in data


def test_analyze_returns_206_when_llm_fails(temp_video_path):
    with (
        patch("routers.analyze.extract_frames", return_value=[None] * 10),
        patch("routers.analyze.estimate_poses", return_value=[{}] * 10),
        patch("routers.analyze.analyze_shooting", return_value=MOCK_RESULT),
        patch("routers.analyze.find_contact_frame_idx", return_value=5),
        patch("routers.analyze.generate_feedback", return_value=None),
        patch("routers.analyze.get_annotated_frames", return_value=["base64abc"]),
    ):
        with open(temp_video_path, "rb") as f:
            response = client.post(
                "/analyze",
                data={"technique": "shooting_driven", "kicking_foot": "right"},
                files={"video": ("test.mp4", f, "video/mp4")},
            )
    assert response.status_code == 206


def test_analyze_returns_422_for_invalid_technique(temp_video_path):
    with open(temp_video_path, "rb") as f:
        response = client.post(
            "/analyze",
            data={"technique": "invalid_technique", "kicking_foot": "right"},
            files={"video": ("test.mp4", f, "video/mp4")},
        )
    assert response.status_code == 422
