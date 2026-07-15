import pytest
from unittest.mock import MagicMock
from services.biomechanics.shooting import analyze_shooting, find_contact_frame_idx, _horizontal_tilt_deg
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


def forward_lean_frame():
    """Right-footed forward lean, player shooting toward +x: shoulders and the kicking foot
    are on the +x side of the hips (hip midpoint x ≈ 0.45)."""
    frame = good_shooting_frame()
    frame["left_shoulder"] = make_landmark(0.38, 0.25)   # shoulders shifted forward (+x)
    frame["right_shoulder"] = make_landmark(0.58, 0.25)
    frame["right_ankle"] = make_landmark(0.48, 0.80)     # kicking foot forward (+x of hips)
    return frame


def forward_lean_facing_left_frame():
    """Same physical forward lean as forward_lean_frame, but the player shoots toward −x:
    shoulders and the kicking foot are on the −x side of the hips. Must score identically."""
    frame = good_shooting_frame()
    frame["left_shoulder"] = make_landmark(0.32, 0.25)   # shoulders shifted forward (−x)
    frame["right_shoulder"] = make_landmark(0.52, 0.25)
    frame["right_ankle"] = make_landmark(0.42, 0.80)     # kicking foot forward (−x of hips)
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


def test_analyze_shooting_populates_checkpoints():
    frames = [good_shooting_frame()]
    result = analyze_shooting(frames, kicking_foot="right", contact_frame_idx=0)
    assert len(result.checkpoints) == 5
    assert all(hasattr(cp, "name") and hasattr(cp, "score") for cp in result.checkpoints)


def test_horizontal_tilt_is_orientation_invariant():
    """Pins the arctan2 tilt bug directly: the same line tilt reads the same whether the
    two points are arranged left→right or right→left across image-x, and a level line ~0°."""
    left, right = make_landmark(0.37, 0.45), make_landmark(0.53, 0.47)
    flipped_left, flipped_right = make_landmark(0.63, 0.45), make_landmark(0.47, 0.47)  # x → 1-x
    assert abs(_horizontal_tilt_deg(left, right) - _horizontal_tilt_deg(flipped_left, flipped_right)) < 1e-9
    assert _horizontal_tilt_deg(make_landmark(0.6, 0.5), make_landmark(0.4, 0.5)) < 1e-6


def test_hip_rotation_orientation_invariant():
    """A player whose hip line is flipped across image-x (facing the other way) must get the
    same hip_rotation score. Before the fix this scored 0 with a spurious flag."""
    frame_a = good_shooting_frame()
    frame_b = good_shooting_frame()
    frame_b["left_hip"] = make_landmark(1.0 - frame_a["left_hip"].x, frame_a["left_hip"].y)
    frame_b["right_hip"] = make_landmark(1.0 - frame_a["right_hip"].x, frame_a["right_hip"].y)
    a = analyze_shooting([frame_a], kicking_foot="right", contact_frame_idx=0)
    b = analyze_shooting([frame_b], kicking_foot="right", contact_frame_idx=0)
    assert a.scores["hip_rotation"] == b.scores["hip_rotation"]


def test_body_lean_orientation_invariant():
    """A forward lean must score identically whether the player shoots toward +x or −x.
    Pins the lean-sign bug where a −x-facing player's forward lean read as 'leaning back'."""
    facing_right = analyze_shooting([forward_lean_frame()], kicking_foot="right", contact_frame_idx=0)
    facing_left = analyze_shooting([forward_lean_facing_left_frame()], kicking_foot="right", contact_frame_idx=0)
    assert facing_right.scores["body_lean"] == facing_left.scores["body_lean"]
    # The forward lean itself should land in the ideal band and not be flagged as leaning back.
    assert facing_left.scores["body_lean"] >= 90
    assert not any("leaning back" in f.lower() for f in facing_left.flags)
