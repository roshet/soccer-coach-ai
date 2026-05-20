import pytest
import numpy as np
from services.video_processor import extract_frames, VideoTooLargeError


def test_extract_frames_returns_frames(temp_video_path):
    frames = extract_frames(temp_video_path)
    assert len(frames) > 0
    assert isinstance(frames[0], np.ndarray)
    assert frames[0].shape == (480, 640, 3)


def test_extract_frames_limits_count(temp_video_path):
    frames = extract_frames(temp_video_path, max_frames=10)
    assert len(frames) <= 10


def test_extract_frames_rejects_large_file(tmp_path):
    large_file = tmp_path / "big.mp4"
    large_file.write_bytes(b"0" * (51 * 1024 * 1024))  # 51MB
    with pytest.raises(VideoTooLargeError):
        extract_frames(str(large_file))
