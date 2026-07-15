import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from services.biomechanics.base import BiomechanicsResult
from services.video_processor import VideoTooLargeError, VideoDurationError
from services.pose_estimator import NoPersonDetectedError

client = TestClient(app)

MOCK_RESULT = BiomechanicsResult(
    technique="shooting_driven",
    scores={"plant_foot_position": 80, "knee_over_ball": 75, "hip_rotation": 70,
            "body_lean": 85, "follow_through": 72},
    flags=[],
    overall_score=76,
)

MOCK_PASSING_RESULT = BiomechanicsResult(
    technique="passing_short",
    scores={"body_shape": 88, "head_position": 79, "plant_foot_position": 81, "weight_transfer": 74},
    flags=[],
    overall_score=80,
)


def _post(temp_video_path, technique="shooting_driven", kicking_foot="right"):
    with open(temp_video_path, "rb") as f:
        return client.post(
            "/analyze",
            data={"technique": technique, "kicking_foot": kicking_foot},
            files={"video": ("test.mp4", f, "video/mp4")},
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
    assert "flags" in data
    assert "technique" in data
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


def test_analyze_returns_400_when_video_too_large(temp_video_path):
    with patch("routers.analyze.extract_frames", side_effect=VideoTooLargeError("too big")):
        response = _post(temp_video_path)
    assert response.status_code == 400


def test_analyze_returns_400_when_video_too_long(temp_video_path):
    with patch("routers.analyze.extract_frames", side_effect=VideoDurationError("too long")):
        response = _post(temp_video_path)
    assert response.status_code == 400


def test_analyze_returns_400_when_video_unreadable(temp_video_path):
    # extract_frames raises a bare ValueError on an unopenable/corrupt file.
    with patch("routers.analyze.extract_frames", side_effect=ValueError("Could not open video file")):
        response = _post(temp_video_path)
    assert response.status_code == 400


def test_analyze_returns_422_when_no_person_detected(temp_video_path):
    with (
        patch("routers.analyze.extract_frames", return_value=[None] * 10),
        patch("routers.analyze.estimate_poses", side_effect=NoPersonDetectedError("no person")),
    ):
        response = _post(temp_video_path)
    assert response.status_code == 422


def test_analyze_returns_422_for_invalid_kicking_foot(temp_video_path):
    response = _post(temp_video_path, kicking_foot="middle")
    assert response.status_code == 422


def test_analyze_routes_passing_technique(temp_video_path):
    # TECHNIQUE_ANALYZERS captures analyzer refs at import, so patch the dict entry itself
    # (patching routers.analyze.analyze_passing would not change the dispatch table).
    mock_passing = MagicMock(return_value=MOCK_PASSING_RESULT)
    with (
        patch("routers.analyze.extract_frames", return_value=[None] * 10),
        patch("routers.analyze.estimate_poses", return_value=[{}] * 10),
        patch.dict("routers.analyze.TECHNIQUE_ANALYZERS", {"passing_short": mock_passing}),
        patch("routers.analyze.find_contact_frame_idx", return_value=5),
        patch("routers.analyze.generate_feedback", return_value="Nice pass."),
        patch("routers.analyze.get_annotated_frames", return_value=["base64abc"]),
    ):
        response = _post(temp_video_path, technique="passing_short")
    assert response.status_code == 200
    assert mock_passing.called
    assert response.json()["technique"] == "passing_short"
