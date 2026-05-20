import os
import cv2
import numpy as np

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB
MAX_DURATION_SECONDS = 30


class VideoTooLargeError(Exception):
    pass


class VideoDurationError(Exception):
    pass


def extract_frames(video_path: str, max_frames: int = 60) -> list[np.ndarray]:
    if os.path.getsize(video_path) > MAX_FILE_SIZE_BYTES:
        raise VideoTooLargeError("Video exceeds 50MB limit")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        if duration > MAX_DURATION_SECONDS:
            raise VideoDurationError(f"Video exceeds {MAX_DURATION_SECONDS}s limit")

        step = max(1, total_frames // max_frames)
        frames = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % step == 0:
                frames.append(frame)
            frame_idx += 1
    finally:
        cap.release()

    return frames[:max_frames]
