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

import mediapipe as mp
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
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True, model_complexity=1) as pose:
        for idx in indices:
            if idx in seen or frames[idx] is None:
                continue
            seen.add(idx)
            rgb = cv2.cvtColor(frames[idx], cv2.COLOR_BGR2RGB)
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

    suffix = os.path.splitext(video.filename or ".mp4")[1] or ".mp4"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await video.read())
        tmp_path = tmp.name

    try:
        frames = extract_frames(tmp_path)
    except VideoTooLargeError:
        raise HTTPException(status_code=400, detail="Video exceeds 50MB limit")
    except VideoDurationError:
        raise HTTPException(status_code=400, detail="Video exceeds 30-second limit")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Could not process video file — ensure it is a valid video",
        )
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
