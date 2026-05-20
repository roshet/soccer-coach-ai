# AI Soccer Coach — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web app where soccer players upload a short video of their technique and receive AI-powered biomechanical analysis and professional coaching feedback.

**Architecture:** FastAPI Python backend handles video processing (OpenCV), pose estimation (MediaPipe), biomechanics scoring (NumPy), and coaching feedback (Claude API). Next.js 14 frontend handles upload, technique selection, and results display. Results are passed between pages via sessionStorage.

**Tech Stack:** Python 3.11, FastAPI, MediaPipe 0.10, OpenCV, NumPy, Anthropic SDK, Next.js 14 (App Router), TailwindCSS, Vercel (frontend), Railway (backend)

---

## File Structure

```
CSProject/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── routers/
│   │   └── analyze.py
│   ├── services/
│   │   ├── video_processor.py
│   │   ├── pose_estimator.py
│   │   ├── feedback_generator.py
│   │   └── biomechanics/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── shooting.py
│   │       └── passing.py
│   └── tests/
│       ├── conftest.py
│       ├── test_video_processor.py
│       ├── test_pose_estimator.py
│       ├── test_biomechanics_shooting.py
│       ├── test_biomechanics_passing.py
│       ├── test_feedback_generator.py
│       └── test_analyze_router.py
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── results/
│   │       └── page.tsx
│   ├── components/
│   │   ├── VideoUpload.tsx
│   │   ├── TechniqueSelector.tsx
│   │   ├── ScoreCard.tsx
│   │   ├── AnnotatedFrames.tsx
│   │   └── CoachingReport.tsx
│   └── lib/
│       └── api.ts
└── docs/
    └── superpowers/
        ├── specs/
        │   └── 2026-05-20-ai-soccer-coach-design.md
        └── plans/
            └── 2026-05-20-ai-soccer-coach.md
```

---

## Task 1: Backend Project Setup

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/main.py`
- Create: `backend/routers/__init__.py`
- Create: `backend/services/__init__.py`
- Create: `backend/services/biomechanics/__init__.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Create directory structure**

```bash
cd CSProject
mkdir -p backend/routers backend/services/biomechanics backend/tests
touch backend/routers/__init__.py backend/services/__init__.py
touch backend/services/biomechanics/__init__.py backend/tests/__init__.py
```

- [ ] **Step 2: Create `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12
mediapipe==0.10.14
opencv-python-headless==4.10.0.84
numpy==1.26.4
anthropic==0.40.0
python-dotenv==1.0.1
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
```

- [ ] **Step 3: Create `backend/.env.example`**

```
ANTHROPIC_API_KEY=your_key_here
```

- [ ] **Step 4: Create `backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers.analyze import router as analyze_router

load_dotenv()

app = FastAPI(title="AI Soccer Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Create `backend/tests/conftest.py`**

```python
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
        # Draw a simple figure to give MediaPipe something to work with
        cv2.circle(frame, (320, 240), 50, (255, 255, 255), -1)
        writer.write(frame)
    writer.release()
    yield path
    os.unlink(path)
```

- [ ] **Step 6: Install dependencies and verify**

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python -c "import fastapi, mediapipe, cv2, anthropic; print('All dependencies OK')"
```

Expected: `All dependencies OK`

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: scaffold backend project structure"
```

---

## Task 2: Video Processor Service

**Files:**
- Create: `backend/services/video_processor.py`
- Create: `backend/tests/test_video_processor.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_video_processor.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_video_processor.py -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'services.video_processor'`

- [ ] **Step 3: Implement `backend/services/video_processor.py`**

```python
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
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    if duration > MAX_DURATION_SECONDS:
        cap.release()
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

    cap.release()
    return frames
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_video_processor.py -v
```

Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/services/video_processor.py backend/tests/test_video_processor.py
git commit -m "feat: add video processor service"
```

---

## Task 3: Pose Estimator Service

**Files:**
- Create: `backend/services/pose_estimator.py`
- Create: `backend/tests/test_pose_estimator.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_pose_estimator.py`:

```python
import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from services.pose_estimator import estimate_poses, landmarks_to_dict, NoPersonDetectedError


def make_mock_landmark(x, y, z=0.0, visibility=0.9):
    lm = MagicMock()
    lm.x = x
    lm.y = y
    lm.z = z
    lm.visibility = visibility
    return lm


def make_mock_pose_result():
    landmarks = [make_mock_landmark(0.5, 0.5) for _ in range(33)]
    # Set key landmarks to realistic values
    landmarks[27] = make_mock_landmark(0.3, 0.8)  # left_ankle
    landmarks[28] = make_mock_landmark(0.6, 0.8)  # right_ankle
    landmarks[25] = make_mock_landmark(0.3, 0.6)  # left_knee
    landmarks[26] = make_mock_landmark(0.6, 0.6)  # right_knee
    landmarks[23] = make_mock_landmark(0.35, 0.45)  # left_hip
    landmarks[24] = make_mock_landmark(0.55, 0.45)  # right_hip
    result = MagicMock()
    result.pose_landmarks = MagicMock()
    result.pose_landmarks.landmark = landmarks
    return result


def test_landmarks_to_dict_returns_named_landmarks():
    mock_result = make_mock_pose_result()
    d = landmarks_to_dict(mock_result.pose_landmarks)
    assert "left_ankle" in d
    assert "right_ankle" in d
    assert "left_knee" in d
    assert "right_knee" in d
    assert "left_hip" in d
    assert "right_hip" in d


def test_landmarks_to_dict_excludes_low_visibility():
    mock_result = make_mock_pose_result()
    mock_result.pose_landmarks.landmark[27].visibility = 0.3  # left_ankle low vis
    d = landmarks_to_dict(mock_result.pose_landmarks)
    assert "left_ankle" not in d


def test_estimate_poses_returns_list_of_dicts():
    frames = [np.zeros((480, 640, 3), dtype=np.uint8)]
    mock_pose_result = make_mock_pose_result()

    with patch("services.pose_estimator.mp_pose") as mock_mp:
        mock_mp.Pose.return_value.__enter__.return_value.process.return_value = mock_pose_result
        result = estimate_poses(frames)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)


def test_estimate_poses_raises_when_no_person_detected():
    frames = [np.zeros((480, 640, 3), dtype=np.uint8)]
    empty_result = MagicMock()
    empty_result.pose_landmarks = None

    with patch("services.pose_estimator.mp_pose") as mock_mp:
        mock_mp.Pose.return_value.__enter__.return_value.process.return_value = empty_result
        with pytest.raises(NoPersonDetectedError):
            estimate_poses(frames)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_pose_estimator.py -v
```

Expected: `FAILED` — `ModuleNotFoundError`

- [ ] **Step 3: Implement `backend/services/pose_estimator.py`**

```python
import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
import base64

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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_pose_estimator.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/services/pose_estimator.py backend/tests/test_pose_estimator.py
git commit -m "feat: add pose estimator service"
```

---

## Task 4: Biomechanics Base Classes

**Files:**
- Create: `backend/services/biomechanics/base.py`

- [ ] **Step 1: Create `backend/services/biomechanics/base.py`**

No test needed — this is a pure data definition. Verify by importing it.

```python
from dataclasses import dataclass, field


@dataclass
class CheckpointScore:
    name: str
    score: int          # 0-100
    flag: str | None    # Human-readable issue description, or None if passing


@dataclass
class BiomechanicsResult:
    technique: str
    scores: dict[str, int]
    flags: list[str]
    overall_score: int
    checkpoints: list[CheckpointScore] = field(default_factory=list)
```

- [ ] **Step 2: Verify import works**

```bash
python -c "from services.biomechanics.base import BiomechanicsResult, CheckpointScore; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/services/biomechanics/base.py
git commit -m "feat: add biomechanics base dataclasses"
```

---

## Task 5: Shooting Analyzer

**Files:**
- Create: `backend/services/biomechanics/shooting.py`
- Create: `backend/tests/test_biomechanics_shooting.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_biomechanics_shooting.py`:

```python
import pytest
from unittest.mock import MagicMock
from services.biomechanics.shooting import analyze_shooting, find_contact_frame_idx
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_biomechanics_shooting.py -v
```

Expected: `FAILED` — `ModuleNotFoundError`

- [ ] **Step 3: Implement `backend/services/biomechanics/shooting.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_biomechanics_shooting.py -v
```

Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/services/biomechanics/shooting.py backend/tests/test_biomechanics_shooting.py
git commit -m "feat: add shooting biomechanics analyzer"
```

---

## Task 6: Passing Analyzer

**Files:**
- Create: `backend/services/biomechanics/passing.py`
- Create: `backend/tests/test_biomechanics_passing.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_biomechanics_passing.py`:

```python
import pytest
from unittest.mock import MagicMock
from services.biomechanics.passing import analyze_passing
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


def leaning_back_frame():
    """Landmarks with player leaning back."""
    frame = good_passing_frame()
    frame["left_shoulder"] = make_landmark(0.25, 0.25)   # shoulders behind hips
    frame["right_shoulder"] = make_landmark(0.45, 0.25)
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


def test_analyze_passing_leaning_back_scores_low():
    frames = [leaning_back_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert result.scores["head_position"] < 60 or result.scores["body_shape"] < 60


def test_analyze_passing_returns_flags_on_poor_form():
    frames = [leaning_back_frame()]
    result = analyze_passing(frames, kicking_foot="right", contact_frame_idx=0)
    assert len(result.flags) > 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_biomechanics_passing.py -v
```

Expected: `FAILED` — `ModuleNotFoundError`

- [ ] **Step 3: Implement `backend/services/biomechanics/passing.py`**

```python
import numpy as np
from .base import BiomechanicsResult
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
        scores["weight_transfer"] = 70

    overall = int(sum(scores.values()) / len(scores))
    return BiomechanicsResult(
        technique="passing_short",
        scores=scores,
        flags=flags,
        overall_score=overall,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_biomechanics_passing.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/services/biomechanics/passing.py backend/tests/test_biomechanics_passing.py
git commit -m "feat: add passing biomechanics analyzer"
```

---

## Task 7: Claude Feedback Generator

**Files:**
- Create: `backend/services/feedback_generator.py`
- Create: `backend/tests/test_feedback_generator.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_feedback_generator.py`:

```python
import pytest
from unittest.mock import MagicMock, patch
from services.feedback_generator import generate_feedback
from services.biomechanics.base import BiomechanicsResult

SAMPLE_RESULT = BiomechanicsResult(
    technique="shooting_driven",
    scores={
        "plant_foot_position": 58,
        "knee_over_ball": 82,
        "hip_rotation": 71,
        "body_lean": 90,
        "follow_through": 65,
    },
    flags=["Plant foot too far from ball", "Follow-through cuts off early"],
    overall_score=73,
)


def test_generate_feedback_returns_string():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Great shot mechanics. Work on your plant foot.")]
    mock_client.messages.create.return_value = mock_message

    result = generate_feedback(SAMPLE_RESULT, client=mock_client)
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_feedback_calls_claude_with_technique_context():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Your technique analysis...")]
    mock_client.messages.create.return_value = mock_message

    generate_feedback(SAMPLE_RESULT, client=mock_client)

    call_kwargs = mock_client.messages.create.call_args
    messages = call_kwargs[1]["messages"] if call_kwargs[1] else call_kwargs[0][0]
    # Verify technique and scores are included in the prompt
    prompt_text = str(call_kwargs)
    assert "shooting" in prompt_text.lower() or "73" in prompt_text


def test_generate_feedback_returns_fallback_on_api_error():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("API timeout")

    result = generate_feedback(SAMPLE_RESULT, client=mock_client)
    assert result is None  # Caller handles None as 206 partial response
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_feedback_generator.py -v
```

Expected: `FAILED` — `ModuleNotFoundError`

- [ ] **Step 3: Implement `backend/services/feedback_generator.py`**

```python
import os
import anthropic
from services.biomechanics.base import BiomechanicsResult

TECHNIQUE_LABELS = {
    "shooting_driven": "driven shot",
    "passing_short": "short pass",
}

SYSTEM_PROMPT = """You are an elite UEFA Pro-licensed soccer coach with 20 years of experience 
coaching professional and academy players. You provide precise, actionable biomechanical feedback 
based on pose analysis data. Reference how professional players (Messi, Ronaldo, De Bruyne) 
execute the same techniques. Be specific, encouraging, and professional. 
Respond in 300-400 words. Structure your response as: 
1. Overall assessment (2-3 sentences)
2. Key strengths (2-3 bullet points) 
3. Priority improvements (2-3 bullet points with specific cues)
4. One drill recommendation"""


def _build_prompt(result: BiomechanicsResult) -> str:
    technique_label = TECHNIQUE_LABELS.get(result.technique, result.technique)
    score_lines = "\n".join(
        f"  - {k.replace('_', ' ').title()}: {v}/100"
        for k, v in result.scores.items()
    )
    flag_lines = "\n".join(f"  - {f}" for f in result.flags) if result.flags else "  - None"

    return f"""Biomechanical analysis for technique: {technique_label}
Overall score: {result.overall_score}/100

Checkpoint scores:
{score_lines}

Issues detected:
{flag_lines}

Please provide professional coaching feedback based on this analysis."""


def generate_feedback(
    result: BiomechanicsResult,
    client: anthropic.Anthropic | None = None,
) -> str | None:
    if client is None:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_prompt(result)}],
        )
        return message.content[0].text
    except Exception:
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_feedback_generator.py -v
```

Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/services/feedback_generator.py backend/tests/test_feedback_generator.py
git commit -m "feat: add Claude feedback generator"
```

---

## Task 8: FastAPI Analyze Router

**Files:**
- Create: `backend/routers/analyze.py`
- Create: `backend/tests/test_analyze_router.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_analyze_router.py`:

```python
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from services.biomechanics.base import BiomechanicsResult

client = TestClient(app)

MOCK_RESULT = BiomechanicsResult(
    technique="shooting_driven",
    scores={"plant_foot_position": 80, "knee_over_ball": 75, "hip_rotation": 70,
            "body_lean": 85, "follow_through": 72},
    flags=[],
    overall_score=76,
)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_returns_200_with_valid_input(temp_video_path):
    with (
        patch("routers.analyze.extract_frames", return_value=[None] * 10),
        patch("routers.analyze.estimate_poses", return_value=[{}] * 10),
        patch("routers.analyze.analyze_shooting", return_value=MOCK_RESULT),
        patch("routers.analyze.find_contact_frame_idx", return_value=5),
        patch("routers.analyze.generate_feedback", return_value="Great technique!"),
        patch("routers.analyze.get_annotated_frames", return_value=["base64abc"]),
    ):
        with open(temp_video_path, "rb") as f:
            response = client.post(
                "/analyze",
                data={"technique": "shooting_driven", "kicking_foot": "right"},
                files={"video": ("test.mp4", f, "video/mp4")},
            )
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "scores" in data
    assert "coaching_report" in data
    assert "annotated_frames" in data


def test_analyze_returns_206_when_llm_fails(temp_video_path):
    with (
        patch("routers.analyze.extract_frames", return_value=[None] * 10),
        patch("routers.analyze.estimate_poses", return_value=[{}] * 10),
        patch("routers.analyze.analyze_shooting", return_value=MOCK_RESULT),
        patch("routers.analyze.find_contact_frame_idx", return_value=5),
        patch("routers.analyze.generate_feedback", return_value=None),
        patch("routers.analyze.get_annotated_frames", return_value=["base64abc"]),
    ):
        with open(temp_video_path, "rb") as f:
            response = client.post(
                "/analyze",
                data={"technique": "shooting_driven", "kicking_foot": "right"},
                files={"video": ("test.mp4", f, "video/mp4")},
            )
    assert response.status_code == 206


def test_analyze_returns_422_for_invalid_technique(temp_video_path):
    with open(temp_video_path, "rb") as f:
        response = client.post(
            "/analyze",
            data={"technique": "invalid_technique", "kicking_foot": "right"},
            files={"video": ("test.mp4", f, "video/mp4")},
        )
    assert response.status_code == 422
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_analyze_router.py -v
```

Expected: `FAILED` — router not yet created

- [ ] **Step 3: Implement `backend/routers/analyze.py`**

```python
import os
import tempfile
from typing import Literal
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from services.video_processor import extract_frames, VideoTooLargeError, VideoDurationError
from services.pose_estimator import estimate_poses, NoPersonDetectedError, annotate_frame
from services.biomechanics.shooting import analyze_shooting, find_contact_frame_idx
from services.biomechanics.passing import analyze_passing
from services.feedback_generator import generate_feedback

import cv2

router = APIRouter()

TECHNIQUE_ANALYZERS = {
    "shooting_driven": analyze_shooting,
    "passing_short": analyze_passing,
}


def get_annotated_frames(
    frames: list, landmarks_per_frame: list, contact_frame_idx: int
) -> list[str]:
    annotated = []
    indices = [
        max(0, contact_frame_idx - 5),
        contact_frame_idx,
        min(len(frames) - 1, contact_frame_idx + 5),
    ]
    seen = set()
    with __import__("mediapipe").solutions.pose.Pose(
        static_image_mode=True, model_complexity=1
    ) as pose:
        for idx in indices:
            if idx in seen or frames[idx] is None:
                continue
            seen.add(idx)
            import cv2 as _cv2
            rgb = _cv2.cvtColor(frames[idx], _cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)
            if result.pose_landmarks:
                annotated.append(annotate_frame(frames[idx], result.pose_landmarks))
    return annotated


@router.post("/analyze")
async def analyze(
    video: UploadFile = File(...),
    technique: str = Form(...),
    kicking_foot: Literal["left", "right"] = Form(...),
):
    if technique not in TECHNIQUE_ANALYZERS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported technique '{technique}'. Choose from: {list(TECHNIQUE_ANALYZERS)}",
        )

    with tempfile.NamedTemporaryFile(
        suffix=os.path.splitext(video.filename or ".mp4")[1], delete=False
    ) as tmp:
        tmp.write(await video.read())
        tmp_path = tmp.name

    try:
        frames = extract_frames(tmp_path)
    except VideoTooLargeError:
        os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail="Video exceeds 50MB limit")
    except VideoDurationError:
        os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail="Video exceeds 30-second limit")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    try:
        landmarks_per_frame = estimate_poses(frames)
    except NoPersonDetectedError as e:
        raise HTTPException(status_code=422, detail=str(e))

    contact_idx = find_contact_frame_idx(landmarks_per_frame, kicking_foot)
    analyzer = TECHNIQUE_ANALYZERS[technique]
    result = analyzer(landmarks_per_frame, kicking_foot=kicking_foot, contact_frame_idx=contact_idx)

    coaching_report = generate_feedback(result)
    annotated_frames = get_annotated_frames(frames, landmarks_per_frame, contact_idx)

    status_code = 200 if coaching_report is not None else 206
    return JSONResponse(
        status_code=status_code,
        content={
            "overall_score": result.overall_score,
            "scores": result.scores,
            "flags": result.flags,
            "technique": result.technique,
            "coaching_report": coaching_report,
            "annotated_frames": annotated_frames,
        },
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_analyze_router.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Run all backend tests**

```bash
pytest tests/ -v
```

Expected: All tests PASSED

- [ ] **Step 6: Commit**

```bash
git add backend/routers/analyze.py backend/tests/test_analyze_router.py
git commit -m "feat: add FastAPI analyze router"
```

---

## Task 9: Frontend Project Setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/next.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/lib/api.ts`
- Create: `frontend/app/layout.tsx`

- [ ] **Step 1: Scaffold Next.js project**

```bash
cd CSProject
npx create-next-app@14 frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

When prompted, accept all defaults.

- [ ] **Step 2: Verify dev server runs**

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` — should show the Next.js default page.
Press Ctrl+C to stop.

- [ ] **Step 3: Create `frontend/lib/api.ts`**

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface AnalysisResult {
  overall_score: number;
  scores: Record<string, number>;
  flags: string[];
  technique: string;
  coaching_report: string | null;
  annotated_frames: string[];
}

export async function analyzeVideo(
  video: File,
  technique: string,
  kickingFoot: "left" | "right"
): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("video", video);
  form.append("technique", technique);
  form.append("kicking_foot", kickingFoot);

  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    body: form,
  });

  if (!res.ok && res.status !== 206) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail ?? `Server error ${res.status}`);
  }

  return res.json();
}
```

- [ ] **Step 4: Create `frontend/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Soccer Coach",
  description: "Professional biomechanical technique analysis powered by AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-950 text-white min-h-screen`}>
        <header className="border-b border-gray-800 px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center gap-3">
            <span className="text-2xl">⚽</span>
            <h1 className="text-xl font-bold">AI Soccer Coach</h1>
            <span className="ml-auto text-sm text-gray-400">Professional Technique Analysis</span>
          </div>
        </header>
        <main className="max-w-4xl mx-auto px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
```

- [ ] **Step 5: Commit**

```bash
cd CSProject
git add frontend/
git commit -m "feat: scaffold Next.js frontend"
```

---

## Task 10: Frontend Upload Page

**Files:**
- Create: `frontend/components/VideoUpload.tsx`
- Create: `frontend/components/TechniqueSelector.tsx`
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: Create `frontend/components/TechniqueSelector.tsx`**

```tsx
export const TECHNIQUES = [
  { value: "shooting_driven", label: "Shooting — Driven Shot" },
  { value: "passing_short", label: "Passing — Short Pass" },
] as const;

export type TechniqueValue = (typeof TECHNIQUES)[number]["value"];

interface Props {
  value: TechniqueValue | "";
  onChange: (v: TechniqueValue) => void;
}

export default function TechniqueSelector({ value, onChange }: Props) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">
        Technique
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as TechniqueValue)}
        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
      >
        <option value="">Select a technique...</option>
        {TECHNIQUES.map((t) => (
          <option key={t.value} value={t.value}>
            {t.label}
          </option>
        ))}
      </select>
    </div>
  );
}
```

- [ ] **Step 2: Create `frontend/components/VideoUpload.tsx`**

```tsx
"use client";
import { useRef, useState } from "react";

interface Props {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

export default function VideoUpload({ onFileSelect, selectedFile }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("video/")) {
      onFileSelect(file);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">Video</label>
      <div
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
          dragOver
            ? "border-green-400 bg-green-900/20"
            : "border-gray-700 hover:border-gray-500"
        }`}
      >
        {selectedFile ? (
          <div className="space-y-1">
            <p className="text-green-400 font-medium">{selectedFile.name}</p>
            <p className="text-sm text-gray-400">
              {(selectedFile.size / 1024 / 1024).toFixed(1)} MB
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-gray-300">Drag and drop your video here</p>
            <p className="text-sm text-gray-500">or click to browse</p>
            <p className="text-xs text-gray-600 mt-3">MP4, MOV, AVI · Max 50MB · Max 30 seconds</p>
          </div>
        )}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onFileSelect(f);
        }}
      />
      <p className="text-xs text-gray-500">
        Tip: Film from a 45° angle at waist height with good lighting for best results.
      </p>
    </div>
  );
}
```

- [ ] **Step 3: Replace `frontend/app/page.tsx`**

```tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import VideoUpload from "@/components/VideoUpload";
import TechniqueSelector, { TechniqueValue } from "@/components/TechniqueSelector";
import { analyzeVideo } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [technique, setTechnique] = useState<TechniqueValue | "">("");
  const [kickingFoot, setKickingFoot] = useState<"left" | "right">("right");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = file && technique;

  const handleSubmit = async () => {
    if (!file || !technique) return;
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeVideo(file, technique, kickingFoot);
      sessionStorage.setItem("analysisResult", JSON.stringify(result));
      router.push("/results");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold mb-2">Analyze Your Technique</h2>
        <p className="text-gray-400">
          Upload a video of your technique and receive professional-grade coaching feedback powered by AI biomechanics analysis.
        </p>
      </div>

      <div className="bg-gray-900 rounded-2xl p-8 space-y-6">
        <VideoUpload onFileSelect={setFile} selectedFile={file} />

        <TechniqueSelector value={technique} onChange={setTechnique} />

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">Kicking Foot</label>
          <div className="flex gap-3">
            {(["right", "left"] as const).map((foot) => (
              <button
                key={foot}
                onClick={() => setKickingFoot(foot)}
                className={`flex-1 py-3 rounded-lg border text-sm font-medium transition-colors ${
                  kickingFoot === foot
                    ? "bg-green-600 border-green-600 text-white"
                    : "border-gray-700 text-gray-300 hover:border-gray-500"
                }`}
              >
                {foot.charAt(0).toUpperCase() + foot.slice(1)} Foot
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="bg-red-900/40 border border-red-700 rounded-lg px-4 py-3 text-red-300 text-sm">
            {error}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={!canSubmit || loading}
          className="w-full py-4 bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:text-gray-500 rounded-xl font-semibold text-lg transition-colors"
        >
          {loading ? "Analyzing your technique..." : "Analyze Technique"}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Start dev server and verify upload page renders**

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` — verify:
- File drag-and-drop area renders
- Technique dropdown shows "Shooting — Driven Shot" and "Passing — Short Pass"
- Left/Right foot buttons toggle correctly
- Submit button is disabled until file + technique are selected

Press Ctrl+C.

- [ ] **Step 5: Commit**

```bash
cd CSProject
git add frontend/components/ frontend/app/page.tsx
git commit -m "feat: add upload page with video drop zone and technique selector"
```

---

## Task 11: Frontend Results Page

**Files:**
- Create: `frontend/components/ScoreCard.tsx`
- Create: `frontend/components/AnnotatedFrames.tsx`
- Create: `frontend/components/CoachingReport.tsx`
- Create: `frontend/app/results/page.tsx`

- [ ] **Step 1: Create `frontend/components/ScoreCard.tsx`**

```tsx
interface Props {
  scores: Record<string, number>;
  overallScore: number;
  flags: string[];
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  const color =
    score >= 80 ? "bg-green-500" : score >= 60 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-300">{label}</span>
        <span className="font-medium">{score}/100</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

export default function ScoreCard({ scores, overallScore, flags }: Props) {
  const overallColor =
    overallScore >= 80 ? "text-green-400" : overallScore >= 60 ? "text-yellow-400" : "text-red-400";

  return (
    <div className="bg-gray-900 rounded-2xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Technique Score</h3>
        <span className={`text-4xl font-bold ${overallColor}`}>{overallScore}</span>
      </div>

      <div className="space-y-3">
        {Object.entries(scores).map(([key, score]) => (
          <ScoreBar
            key={key}
            label={key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            score={score}
          />
        ))}
      </div>

      {flags.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-400">Issues Detected</p>
          <ul className="space-y-1">
            {flags.map((flag, i) => (
              <li key={i} className="text-sm text-yellow-300 flex gap-2">
                <span>⚠</span>
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create `frontend/components/AnnotatedFrames.tsx`**

```tsx
interface Props {
  frames: string[];
}

const FRAME_LABELS = ["Approach", "Contact", "Follow-Through"];

export default function AnnotatedFrames({ frames }: Props) {
  if (frames.length === 0) return null;

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">Key Frames</h3>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {frames.map((frame, i) => (
          <div key={i} className="space-y-1">
            <img
              src={`data:image/jpeg;base64,${frame}`}
              alt={FRAME_LABELS[i] ?? `Frame ${i + 1}`}
              className="rounded-xl w-full object-cover bg-gray-800"
            />
            <p className="text-xs text-center text-gray-400">
              {FRAME_LABELS[i] ?? `Frame ${i + 1}`}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create `frontend/components/CoachingReport.tsx`**

```tsx
interface Props {
  report: string | null;
}

export default function CoachingReport({ report }: Props) {
  if (!report) {
    return (
      <div className="bg-gray-900 rounded-2xl p-6">
        <h3 className="text-lg font-semibold mb-2">Coaching Report</h3>
        <p className="text-gray-400 text-sm">
          Coaching report unavailable — scores and flags above reflect your analysis.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-2xl p-6 space-y-3">
      <h3 className="text-lg font-semibold">Coaching Report</h3>
      <div className="text-gray-300 leading-relaxed whitespace-pre-line text-sm">
        {report}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create `frontend/app/results/page.tsx`**

```tsx
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { AnalysisResult } from "@/lib/api";
import ScoreCard from "@/components/ScoreCard";
import AnnotatedFrames from "@/components/AnnotatedFrames";
import CoachingReport from "@/components/CoachingReport";

export default function ResultsPage() {
  const router = useRouter();
  const [result, setResult] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("analysisResult");
    if (!raw) {
      router.replace("/");
      return;
    }
    setResult(JSON.parse(raw));
  }, [router]);

  if (!result) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <p className="text-gray-400">Loading results...</p>
      </div>
    );
  }

  const techniqueLabel = result.technique
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold mb-1">Analysis Complete</h2>
        <p className="text-gray-400">{techniqueLabel}</p>
      </div>

      <ScoreCard
        scores={result.scores}
        overallScore={result.overall_score}
        flags={result.flags}
      />

      <AnnotatedFrames frames={result.annotated_frames} />

      <CoachingReport report={result.coaching_report} />

      <button
        onClick={() => {
          sessionStorage.removeItem("analysisResult");
          router.push("/");
        }}
        className="w-full py-3 border border-gray-700 hover:border-gray-500 rounded-xl text-gray-300 transition-colors"
      >
        Analyze Another Video
      </button>
    </div>
  );
}
```

- [ ] **Step 5: Test the full UI flow end-to-end**

Start both servers:

Terminal 1:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Terminal 2:
```bash
cd frontend
npm run dev
```

Verify:
1. `http://localhost:3000` shows upload page
2. Upload a short video, select a technique and kicking foot, click Analyze
3. Results page shows score bars, annotated frames, and coaching report
4. "Analyze Another Video" button returns to home

- [ ] **Step 6: Commit**

```bash
cd CSProject
git add frontend/components/ frontend/app/results/
git commit -m "feat: add results page with scores, frames, and coaching report"
```

---

## Task 12: Deployment

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/.env.local.example`
- Create: `README.md`

- [ ] **Step 1: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create `frontend/.env.local.example`**

```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

- [ ] **Step 3: Deploy backend to Railway**

1. Go to [railway.app](https://railway.app) and create a new project
2. Connect your GitHub repo
3. Set root directory to `backend/`
4. Add environment variable: `ANTHROPIC_API_KEY=your_key`
5. Railway auto-detects the Dockerfile and deploys
6. Copy the generated URL (e.g. `https://ai-soccer-coach-backend.railway.app`)

- [ ] **Step 4: Deploy frontend to Vercel**

```bash
cd frontend
npx vercel
```

When prompted:
- Link to existing project: No
- Project name: `ai-soccer-coach`
- Root directory: `./` (already in frontend/)

Then set the environment variable:
```bash
npx vercel env add NEXT_PUBLIC_API_URL production
# Paste your Railway URL when prompted
npx vercel --prod
```

- [ ] **Step 5: Create `README.md`**

````markdown
# AI Soccer Coach

AI-powered biomechanical technique analysis for professional soccer players.

Upload a short video of your technique and receive instant coaching feedback — plant foot positioning, hip rotation, body lean, follow-through, and more — analyzed against professional standards.

## Demo

[Live App](https://your-app.vercel.app) | [Demo Video](link-to-loom-or-youtube)

## Tech Stack

- **Frontend:** Next.js 14, TailwindCSS, Vercel
- **Backend:** FastAPI, Python 3.11, Railway
- **ML:** MediaPipe Pose, OpenCV, NumPy
- **AI:** Claude API (claude-sonnet-4-6)

## Architecture

```
Video Upload → Frame Extraction (OpenCV) → Pose Estimation (MediaPipe)
→ Biomechanics Scoring (NumPy) → Coaching Feedback (Claude API) → Results UI
```

## Supported Techniques (MVP)

- Shooting — Driven Shot
- Passing — Short Pass

## Local Development

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your ANTHROPIC_API_KEY
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.local.example .env.local  # Set NEXT_PUBLIC_API_URL
npm run dev
```

**Tests:**
```bash
cd backend && pytest tests/ -v
```
````

- [ ] **Step 6: Final commit**

```bash
cd CSProject
git add backend/Dockerfile frontend/.env.local.example README.md
git commit -m "feat: add deployment config and README"
```

---

## Self-Review Notes

**Spec coverage check:**
- ✅ Video upload + technique selection → Task 10
- ✅ MediaPipe pose estimation pipeline → Tasks 3, 4
- ✅ Biomechanics rules for Shooting → Task 5
- ✅ Biomechanics rules for Passing → Task 6
- ✅ Claude-powered coaching report → Task 7
- ✅ Annotated freeze-frames → Task 8 (`get_annotated_frames`) + Task 11
- ✅ Deployed frontend + backend → Task 12
- ✅ Error handling (file size, duration, no person, LLM failure) → Tasks 2, 3, 8
- ✅ Filming guide tip → Task 10 (`VideoUpload.tsx`)

**Type consistency:** `BiomechanicsResult` defined in Task 4, used identically in Tasks 5, 6, 7, 8. `find_contact_frame_idx` defined in `shooting.py` (Task 5), imported in `analyze.py` (Task 8) — consistent. `AnalysisResult` TypeScript interface in `api.ts` matches the JSON shape returned by the router.

**No placeholders:** All tasks contain complete code. No TBDs.
