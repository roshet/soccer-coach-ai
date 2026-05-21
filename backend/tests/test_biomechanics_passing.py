import pytest
from unittest.mock import MagicMock
from services.biomechanics.passing import analyze_passing
from services.biomechanics.base import BiomechanicsResult


def make_landmark(x, y, z=0.0, visibility=0.9):
    lm = MagicMock()
    lm.x = x
    lm.y = y
    lm.z = z
    lm.visibility = visibility
    return lm


def good_passing_frame():
    """Landmarks representing ideal right-foot short pass."""
    return {
        "nose": make_landmark(0.45, 0.15),
        "left_shoulder": make_landmark(0.35, 0.25),
        "right_shoulder": make_landmark(0.55, 0.25),
        "left_hip": make_landmark(0.38, 0.45),
        "right_hip": make_landmark(0.52, 0.45),   # level hips for passing
        "left_knee": make_landmark(0.38, 0.62),
        "right_knee": make_landmark(0.52, 0.62),
        "left_ankle": make_landmark(0.38, 0.80),
        "right_ankle": make_landmark(0.50, 0.80),
    }


def leaning_back_frame():
    """Landmarks with player leaning back."""
    frame = good_passing_frame()
    frame["left_shoulder"] = make_landmark(0.25, 0.25)   # shoulders behind hips
    frame["right_shoulder"] = make_landmark(0.45, 0.25)
    return frame


def test_analyze_passing_returns_result():
    frames = [good_passing_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert isinstance(result, BiomechanicsResult)
    assert result.technique == "passing_short"
    assert 0 <= result.overall_score <= 100


def test_analyze_passing_good_form_scores_high():
    frames = [good_passing_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert result.overall_score >= 65


def test_analyze_passing_leaning_back_scores_low():
    frames = [leaning_back_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert result.scores["head_position"] < 60 or result.scores["body_shape"] < 60


def test_analyze_passing_returns_flags_on_poor_form():
    frames = [leaning_back_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert len(result.flags) > 0


def test_analyze_passing_populates_checkpoints():
    frames = [good_passing_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert len(result.checkpoints) == 4
    assert all(hasattr(cp, "name") and hasattr(cp, "score") for cp in result.checkpoints)
