import numpy as np
from .base import BiomechanicsResult


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
        hip_angle = abs(float(np.degrees(np.arctan2(
            lm["right_hip"].y - lm["left_hip"].y,
            lm["right_hip"].x - lm["left_hip"].x,
        ))))
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
        lean = float(np.degrees(np.arctan2(smx - hmx, hmy - smy)))
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
        scores["follow_through"] = 70

    overall = int(sum(scores.values()) / len(scores))
    return BiomechanicsResult(
        technique="shooting_driven",
        scores=scores,
        flags=flags,
        overall_score=overall,
    )
