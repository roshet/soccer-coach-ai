import os
import tempfile
import numpy as np
import cv2
import pytest


@pytest.fixture
def temp_video_path():
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        path = f.name
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, 30, (640, 480))
    for _ in range(60):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(frame, (320, 240), 50, (255, 255, 255), -1)
        writer.write(frame)
    writer.release()
    yield path
    os.unlink(path)
