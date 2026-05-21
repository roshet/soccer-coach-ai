import pytest
from unittest.mock import MagicMock
from services.biomechanics.shooting import analyze_shooting, find_contact_frame_idx
from services.biomechanics.base import BiomechanicsResult


def make_landmark(x, y, z=0.0, visibility=0.9):
    lm = MagicMock()
    lm.x = x
    lm.y = y
    lm.z = z
    lm.visibility = visibility
    return lm


def good_shooting_frame():
    """Landmarks representing ideal right-foot driven shot."""
    return {
        "left_shoulder": make_landmark(0.35, 0.25),
        "right_shoulder": make_landmark(0.55, 0.25),
        "left_hip": make_landmark(0.37, 0.45),
        "right_hip": make_landmark(0.53, 0.47),  # slight hip rotation
        "left_knee": make_landmark(0.37, 0.62),   # plant knee
        "right_knee": make_landmark(0.52, 0.62),  # kicking knee over ankle
        "left_ankle": make_landmark(0.37, 0.80),  # plant ankle
        "right_ankle": make_landmark(0.47, 0.80), # kicking ankle near plant
    }


def bad_plant_foot_frame():
    """Landmarks with plant foot too far from kicking foot."""
    frame = good_shooting_frame()
    frame["left_ankle"] = make_landmark(0.10, 0.80)  # too far left
    return frame


def test_analyze_shooting_returns_result():
    frames = [good_shooting_frame()]
    result = analyze_shooting(frames, kicking_foot="right", contact_frame_idx=0)
    assert isinstance(result, BiomechanicsResult)
    assert result.technique == "shooting_driven"
    assert 0 <= result.overall_score <= 100


def test_analyze_shooting_good_form_scores_high():
    frames = [good_shooting_frame()]
    result = analyze_shooting(frames, kicking_foot="right", contact_frame_idx=0)
    assert result.overall_score >= 70


def test_analyze_shooting_bad_plant_foot_scores_low_on_checkpoint():
    frames = [bad_plant_foot_frame()]
    result = analyze_shooting(frames, kicking_foot="right", contact_frame_idx=0)
    assert result.scores["plant_foot_position"] < 60


def test_analyze_shooting_bad_plant_foot_includes_flag():
    frames = [bad_plant_foot_frame()]
    result = analyze_shooting(frames, kicking_foot="right", contact_frame_idx=0)
    assert any("plant foot" in flag.lower() for flag in result.flags)


def test_find_contact_frame_idx_returns_int():
    frames = [good_shooting_frame(), good_shooting_frame(), good_shooting_frame()]
    idx = find_contact_frame_idx(frames, "right")
    assert isinstance(idx, int)
    assert 0 <= idx < len(frames)
