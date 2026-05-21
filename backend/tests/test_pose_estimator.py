import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from services.pose_estimator import estimate_poses, landmarks_to_dict, NoPersonDetectedError


def make_mock_landmark(x, y, z=0.0, visibility=0.9):
    lm = MagicMock()
    lm.x = x
    lm.y = y
    lm.z = z
    lm.visibility = visibility
    return lm


def make_mock_pose_result():
    landmarks = [make_mock_landmark(0.5, 0.5) for _ in range(33)]
    landmarks[27] = make_mock_landmark(0.3, 0.8)  # left_ankle
    landmarks[28] = make_mock_landmark(0.6, 0.8)  # right_ankle
    landmarks[25] = make_mock_landmark(0.3, 0.6)  # left_knee
    landmarks[26] = make_mock_landmark(0.6, 0.6)  # right_knee
    landmarks[23] = make_mock_landmark(0.35, 0.45)  # left_hip
    landmarks[24] = make_mock_landmark(0.55, 0.45)  # right_hip
    result = MagicMock()
    result.pose_landmarks = MagicMock()
    result.pose_landmarks.landmark = landmarks
    return result


def test_landmarks_to_dict_returns_named_landmarks():
    mock_result = make_mock_pose_result()
    d = landmarks_to_dict(mock_result.pose_landmarks)
    assert "left_ankle" in d
    assert "right_ankle" in d
    assert "left_knee" in d
    assert "right_knee" in d
    assert "left_hip" in d
    assert "right_hip" in d


def test_landmarks_to_dict_excludes_low_visibility():
    mock_result = make_mock_pose_result()
    mock_result.pose_landmarks.landmark[27].visibility = 0.3  # left_ankle low vis
    d = landmarks_to_dict(mock_result.pose_landmarks)
    assert "left_ankle" not in d


def test_estimate_poses_returns_list_of_dicts():
    frames = [np.zeros((480, 640, 3), dtype=np.uint8)]
    mock_pose_result = make_mock_pose_result()

    with patch("services.pose_estimator.mp_pose") as mock_mp:
        mock_mp.Pose.return_value.__enter__.return_value.process.return_value = mock_pose_result
        result = estimate_poses(frames)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)


def test_estimate_poses_raises_when_no_person_detected():
    frames = [np.zeros((480, 640, 3), dtype=np.uint8)]
    empty_result = MagicMock()
    empty_result.pose_landmarks = None

    with patch("services.pose_estimator.mp_pose") as mock_mp:
        mock_mp.Pose.return_value.__enter__.return_value.process.return_value = empty_result
        with pytest.raises(NoPersonDetectedError):
            estimate_poses(frames)
