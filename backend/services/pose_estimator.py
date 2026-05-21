import cv2
import numpy as np
import mediapipe as mp
import base64

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

LANDMARK_NAMES = {
    0: "nose",
    11: "left_shoulder",
    12: "right_shoulder",
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
    29: "left_heel",
    30: "right_heel",
    31: "left_foot_index",
    32: "right_foot_index",
}

VISIBILITY_THRESHOLD = 0.5


class NoPersonDetectedError(Exception):
    pass


def landmarks_to_dict(pose_landmarks) -> dict:
    result = {}
    for idx, name in LANDMARK_NAMES.items():
        lm = pose_landmarks.landmark[idx]
        if lm.visibility >= VISIBILITY_THRESHOLD:
            result[name] = lm
    return result


def estimate_poses(frames: list[np.ndarray]) -> list[dict]:
    results = []
    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        for frame in frames:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)
            if result.pose_landmarks is None:
                results.append({})
            else:
                results.append(landmarks_to_dict(result.pose_landmarks))

    non_empty = [r for r in results if r]
    if not non_empty:
        raise NoPersonDetectedError(
            "No player detected — ensure the player is clearly visible throughout the video"
        )
    return results


def annotate_frame(frame: np.ndarray, pose_landmarks) -> str:
    annotated = frame.copy()
    mp_drawing.draw_landmarks(
        annotated,
        pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing.DrawingSpec(
            color=(0, 255, 0), thickness=2, circle_radius=3
        ),
        connection_drawing_spec=mp_drawing.DrawingSpec(
            color=(0, 255, 0), thickness=2
        ),
    )
    _, buffer = cv2.imencode(".jpg", annotated)
    return base64.b64encode(buffer).decode("utf-8")
