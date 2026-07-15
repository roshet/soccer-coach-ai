import numpy as np
from .base import BiomechanicsResult, CheckpointScore


def find_contact_frame_idx(landmarks_per_frame: list[dict], kicking_foot: str) -> int:
    ankle_key = f"{kicking_foot}_ankle"
    max_velocity = 0.0
    contact_idx = len(landmarks_per_frame) // 2

    for i in range(1, len(landmarks_per_frame)):
        prev = landmarks_per_frame[i - 1]
        curr = landmarks_per_frame[i]
        if ankle_key in prev and ankle_key in curr:
            dx = curr[ankle_key].x - prev[ankle_key].x
            dy = curr[ankle_key].y - prev[ankle_key].y
            velocity = (dx ** 2 + dy ** 2) ** 0.5
            if velocity > max_velocity:
                max_velocity = velocity
                contact_idx = i

    return contact_idx


def _score_range(value: float, ideal_min: float, ideal_max: float, penalty_rate: float = 400) -> int:
    if ideal_min <= value <= ideal_max:
        return 100
    deviation = max(value - ideal_max, ideal_min - value)
    return max(0, int(100 - deviation * penalty_rate))


def _horizontal_tilt_deg(p_left, p_right) -> float:
    """Absolute tilt of the left→right line from horizontal, in [0, 90] degrees.

    Orientation-independent: a level line reads ~0° regardless of which side sits at the
    smaller image-x. (A raw abs(arctan2) returns ~180° for a level line when p_right.x <
    p_left.x, which mis-scored players facing one way — see find in audit.)
    """
    angle = abs(float(np.degrees(np.arctan2(p_right.y - p_left.y, p_right.x - p_left.x))))
    return angle if angle <= 90 else 180.0 - angle


def analyze_shooting(
    landmarks_per_frame: list[dict],
    kicking_foot: str,
    contact_frame_idx: int,
) -> BiomechanicsResult:
    lm = landmarks_per_frame[contact_frame_idx]
    plant_foot = "right" if kicking_foot == "left" else "left"

    scores = {}
    flags = []

    # 1. Plant foot lateral distance (normalized coords: ideal 0.05–0.15)
    if f"{plant_foot}_ankle" in lm and f"{kicking_foot}_ankle" in lm:
        lateral = abs(lm[f"{plant_foot}_ankle"].x - lm[f"{kicking_foot}_ankle"].x)
        plant_score = _score_range(lateral, 0.05, 0.15)
        if lateral < 0.05:
            flags.append("Plant foot too close to kicking foot — risks loss of balance")
        elif lateral > 0.15:
            flags.append("Plant foot too far from ball — reduces power transfer")
        scores["plant_foot_position"] = plant_score
    else:
        scores["plant_foot_position"] = 50

    # 2. Kicking knee over kicking ankle at contact (ideal delta x < 0.05)
    if f"{kicking_foot}_knee" in lm and f"{kicking_foot}_ankle" in lm:
        knee_delta = abs(lm[f"{kicking_foot}_knee"].x - lm[f"{kicking_foot}_ankle"].x)
        knee_score = _score_range(knee_delta, 0.0, 0.05, penalty_rate=600)
        if knee_delta > 0.05:
            flags.append("Knee not over ball at contact — reduces accuracy and power")
        scores["knee_over_ball"] = knee_score
    else:
        scores["knee_over_ball"] = 50

    # 3. Hip rotation (angle of hip line to horizontal; ideal 10–30°)
    if "left_hip" in lm and "right_hip" in lm:
        hip_angle = _horizontal_tilt_deg(lm["left_hip"], lm["right_hip"])
        hip_score = _score_range(hip_angle, 10.0, 30.0, penalty_rate=3)
        if hip_angle < 10:
            flags.append("Insufficient hip rotation — more rotation generates more power")
        elif hip_angle > 30:
            flags.append("Excessive hip rotation at contact — reduces accuracy")
        scores["hip_rotation"] = hip_score
    else:
        scores["hip_rotation"] = 50

    # 4. Body lean (shoulder midpoint ahead of hip midpoint; ideal 5–15°)
    if all(k in lm for k in ["left_shoulder", "right_shoulder", "left_hip", "right_hip"]):
        smx = (lm["left_shoulder"].x + lm["right_shoulder"].x) / 2
        smy = (lm["left_shoulder"].y + lm["right_shoulder"].y) / 2
        hmx = (lm["left_hip"].x + lm["right_hip"].x) / 2
        hmy = (lm["left_hip"].y + lm["right_hip"].y) / 2
        # "Forward" is orientation-dependent: at contact the kicking foot is forward, so use
        # the kicking ankle's side of the hips as the forward direction. Without this, a correct
        # forward lean by a player facing −x reads as negative and is falsely flagged "leaning back".
        if f"{kicking_foot}_ankle" in lm:
            forward_sign = 1.0 if lm[f"{kicking_foot}_ankle"].x >= hmx else -1.0
        else:
            forward_sign = 1.0
        lean = float(np.degrees(np.arctan2((smx - hmx) * forward_sign, hmy - smy)))
        lean_score = _score_range(lean, 5.0, 15.0, penalty_rate=5)
        if lean < 5:
            flags.append("Leaning back at contact — ball will go high")
        elif lean > 15:
            flags.append("Excessive forward lean — reduces shot power")
        scores["body_lean"] = lean_score
    else:
        scores["body_lean"] = 50

    # 5. Follow-through (kicking foot continues upward after contact)
    ankle_key = f"{kicking_foot}_ankle"
    post_frames = landmarks_per_frame[contact_frame_idx: contact_frame_idx + 4]
    y_positions = [f[ankle_key].y for f in post_frames if ankle_key in f]
    if len(y_positions) >= 2 and y_positions[-1] < y_positions[0]:
        scores["follow_through"] = 90
    elif len(y_positions) >= 2:
        scores["follow_through"] = 50
        flags.append("Follow-through cuts off early — reduces power and accuracy")
    else:
        scores["follow_through"] = 50

    overall = int(sum(scores.values()) / len(scores))

    # Build per-checkpoint flag lookup (each checkpoint gets its own flag if one applies)
    checkpoint_flags: dict[str, str] = {}
    for flag in flags:
        if "plant foot" in flag.lower():
            checkpoint_flags["plant_foot_position"] = flag
        elif "knee" in flag.lower():
            checkpoint_flags["knee_over_ball"] = flag
        elif "hip" in flag.lower():
            checkpoint_flags["hip_rotation"] = flag
        elif "lean" in flag.lower() or "leaning" in flag.lower():
            checkpoint_flags["body_lean"] = flag
        elif "follow" in flag.lower():
            checkpoint_flags["follow_through"] = flag

    checkpoints = [
        CheckpointScore(name=k, score=v, flag=checkpoint_flags.get(k))
        for k, v in scores.items()
    ]

    return BiomechanicsResult(
        technique="shooting_driven",
        scores=scores,
        flags=flags,
        overall_score=overall,
        checkpoints=checkpoints,
    )
