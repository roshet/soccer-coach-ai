import pytest
import cv2
import numpy as np
from services.video_processor import extract_frames, VideoTooLargeError, VideoDurationError


def test_extract_frames_returns_frames(temp_video_path):
    frames = extract_frames(temp_video_path)
    assert len(frames) > 0
    assert isinstance(frames[0], np.ndarray)
    assert frames[0].shape == (480, 640, 3)


def test_extract_frames_limits_count(temp_video_path):
    frames = extract_frames(temp_video_path, max_frames=10)
    assert len(frames) == 10


def test_extract_frames_rejects_large_file(tmp_path):
    large_file = tmp_path / "big.mp4"
    large_file.write_bytes(b"0" * (51 * 1024 * 1024))  # 51MB
    with pytest.raises(VideoTooLargeError):
        extract_frames(str(large_file))


def test_extract_frames_rejects_long_video(tmp_path):
    path = str(tmp_path / "long.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, 30, (64, 64))
    for _ in range(1000):  # ~33 seconds at 30fps
        writer.write(np.zeros((64, 64, 3), dtype=np.uint8))
    writer.release()
    with pytest.raises(VideoDurationError):
        extract_frames(path)
