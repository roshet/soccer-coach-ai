import numpy as np
from .base import BiomechanicsResult, CheckpointScore
from .shooting import find_contact_frame_idx, _score_range


def analyze_passing(
    landmarks_per_frame: list[dict],
    kicking_foot: str,
    contact_frame_idx: int,
) -> BiomechanicsResult:
    lm = landmarks_per_frame[contact_frame_idx]
    plant_foot = "right" if kicking_foot == "left" else "left"

    scores = {}
    flags = []

    # 1. Body shape — hips level (small angle to horizontal; ideal 0–10°)
    if "left_hip" in lm and "right_hip" in lm:
        hip_angle = abs(float(np.degrees(np.arctan2(
            lm["right_hip"].y - lm["left_hip"].y,
            lm["right_hip"].x - lm["left_hip"].x,
        ))))
        body_score = _score_range(hip_angle, 0.0, 10.0, penalty_rate=4)
        if hip_angle > 10:
            flags.append("Hips not square to target — reduces passing accuracy")
        scores["body_shape"] = body_score
    else:
        scores["body_shape"] = 50

    # 2. Head position — nose y should be lower than shoulder midpoint y (head over ball)
    if "nose" in lm and "left_shoulder" in lm and "right_shoulder" in lm:
        shoulder_mid_y = (lm["left_shoulder"].y + lm["right_shoulder"].y) / 2
        head_delta = lm["nose"].y - shoulder_mid_y  # positive = nose below shoulders (good)
        head_score = _score_range(head_delta, 0.05, 0.25, penalty_rate=300)
        if head_delta < 0.05:
            flags.append("Head up at contact — keep eyes on the ball for accuracy")
        scores["head_position"] = head_score
    else:
        scores["head_position"] = 50

    # 3. Plant foot positioning (ideal lateral distance 0.04–0.12)
    if f"{plant_foot}_ankle" in lm and f"{kicking_foot}_ankle" in lm:
        lateral = abs(lm[f"{plant_foot}_ankle"].x - lm[f"{kicking_foot}_ankle"].x)
        plant_score = _score_range(lateral, 0.04, 0.12, penalty_rate=500)
        if lateral > 0.12:
            flags.append("Plant foot too far from ball — reduces control and direction")
        elif lateral < 0.04:
            flags.append("Plant foot too close — risks loss of balance")
        scores["plant_foot_position"] = plant_score
    else:
        scores["plant_foot_position"] = 50

    # 4. Weight transfer — plant ankle should be stable (minimal movement in surrounding frames)
    plant_ankle_key = f"{plant_foot}_ankle"
    surrounding = landmarks_per_frame[
        max(0, contact_frame_idx - 2): contact_frame_idx + 3
    ]
    plant_positions = [f[plant_ankle_key].x for f in surrounding if plant_ankle_key in f]
    if len(plant_positions) >= 2:
        movement = max(plant_positions) - min(plant_positions)
        weight_score = _score_range(movement, 0.0, 0.02, penalty_rate=2000)
        if movement > 0.02:
            flags.append("Unstable plant foot — transfer weight fully onto plant leg before contact")
        scores["weight_transfer"] = weight_score
    else:
        scores["weight_transfer"] = 50

    overall = int(sum(scores.values()) / len(scores))

    # Build per-checkpoint flag lookup
    checkpoint_flags: dict[str, str] = {}
    for flag in flags:
        if "hip" in flag.lower():
            checkpoint_flags["body_shape"] = flag
        elif "head" in flag.lower() or "eyes" in flag.lower():
            checkpoint_flags["head_position"] = flag
        elif "plant foot" in flag.lower():
            checkpoint_flags["plant_foot_position"] = flag
        elif "unstable" in flag.lower() or "weight" in flag.lower():
            checkpoint_flags["weight_transfer"] = flag

    checkpoints = [
        CheckpointScore(name=k, score=v, flag=checkpoint_flags.get(k))
        for k, v in scores.items()
    ]

    return BiomechanicsResult(
        technique="passing_short",
        scores=scores,
        flags=flags,
        overall_score=overall,
        checkpoints=checkpoints,
    )
