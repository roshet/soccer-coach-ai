import pytest
from unittest.mock import MagicMock
from services.biomechanics.passing import analyze_passing
from services.biomechanics.shooting import _horizontal_tilt_deg
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


def head_up_frame():
    """Landmarks with the player's head up (nose well above the shoulder line) — eyes off
    the ball. This is a real passing fault the head_position checkpoint should catch."""
    frame = good_passing_frame()
    frame["nose"] = make_landmark(0.45, 0.02)   # nose raised well above shoulders (y ~0.25)
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


def test_analyze_passing_head_up_scores_low():
    frames = [head_up_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert result.scores["head_position"] < 60


def test_analyze_passing_good_head_position_scores_high_no_flag():
    """A2 regression: a head-down pose must be reachable/high, not always flagged 'head up'."""
    result = analyze_passing([good_passing_frame()], kicking_foot="right", contact_frame_idx=0)
    assert result.scores["head_position"] >= 90
    assert not any("head up" in f.lower() for f in result.flags)


def test_analyze_passing_returns_flags_on_poor_form():
    frames = [head_up_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert len(result.flags) > 0


def test_body_shape_orientation_invariant():
    """Hips tilted by the same amount must score the same whether the hip line runs
    left→right or right→left across image-x. Pins the arctan2 tilt bug in passing."""
    frame_a = good_passing_frame()
    frame_a["right_hip"] = make_landmark(0.52, 0.50)   # introduce a real hip tilt
    frame_b = good_passing_frame()
    frame_b["left_hip"] = make_landmark(1.0 - frame_a["left_hip"].x, frame_a["left_hip"].y)
    frame_b["right_hip"] = make_landmark(1.0 - frame_a["right_hip"].x, frame_a["right_hip"].y)
    a = analyze_passing([frame_a], kicking_foot="right", contact_frame_idx=0)
    b = analyze_passing([frame_b], kicking_foot="right", contact_frame_idx=0)
    assert a.scores["body_shape"] == b.scores["body_shape"]


def test_analyze_passing_populates_checkpoints():
    frames = [good_passing_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert len(result.checkpoints) == 4
    assert all(hasattr(cp, "name") and hasattr(cp, "score") for cp in result.checkpoints)
