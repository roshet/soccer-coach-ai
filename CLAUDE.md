# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Soccer Coach — a full-stack app that accepts video uploads and uses MediaPipe pose estimation + Claude API to analyze soccer technique (shooting/passing) and generate coaching feedback.

## Commands

### Backend (FastAPI + Python 3.11)

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Set ANTHROPIC_API_KEY and ALLOWED_ORIGINS
uvicorn main:app --reload       # Runs on :8000
```

Run all tests:
```bash
cd backend && pytest tests/ -v
```

Run a single test file:
```bash
cd backend && pytest tests/test_biomechanics_shooting.py -v
```

### Frontend (Next.js 14)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # Set NEXT_PUBLIC_API_URL
npm run dev      # Runs on :3000
npm run build
npm run lint
```

## Validation Loop

Before claiming any task complete, fixed, or working, you MUST run the relevant checks below and paste/quote the actual output. "I think it works" or "the change looks right" is not acceptable — evidence before assertions.

**After backend changes (anything under `backend/`):**
```bash
cd backend && pytest tests/ -v
```
All tests must pass. If a test fails, fix the root cause — do NOT delete, skip, `xfail`, or comment out the test to make it pass.

**After frontend changes (anything under `frontend/`):**
```bash
cd frontend && npm run build && npm run lint
```
Build must succeed and lint must be clean. Type errors are real errors — fix them, don't suppress with `any` or `@ts-ignore`.

**After changes that affect the API contract** (request/response shape in `routers/analyze.py` or `frontend/lib/api.ts`): run both the backend tests AND `npm run build` to confirm the frontend still type-checks against the new shape.

**If you cannot run validation** (missing dependencies, no `ANTHROPIC_API_KEY`, sandbox restrictions, etc.): say so explicitly. Do NOT claim success based on reading the diff. State which checks you ran, which you skipped, and why.

**UI/behavior changes** are not validated by tests alone. If you change the upload flow, results rendering, or any user-visible behavior, say plainly that automated checks passed but the UI was not exercised in a browser — don't claim the feature "works."

## Architecture

### Data Pipeline

```
POST /analyze (video + technique + kicking_foot)
  → extract_frames()          # OpenCV: max 60 frames, ≤50MB, ≤30s
  → estimate_poses()          # MediaPipe: 33 landmarks → 13 key landmarks per frame
  → find_contact_frame_idx()  # Max ankle velocity = ball contact frame
  → analyze_shooting/passing() # Biomechanics scoring (0-100 per checkpoint)
  → generate_feedback()       # Claude claude-sonnet-4-6: UEFA coach persona, 300-400 words
  → annotate frames           # Skeleton overlay → base64 JPEG
  ← JSON: overall_score + scores + flags + technique + coaching_report + annotated_frames
```

### Backend Structure

- `main.py` — FastAPI app, CORS middleware (reads `ALLOWED_ORIGINS` from env)
- `routers/analyze.py` — Single `/analyze` endpoint, orchestrates all services
- `services/video_processor.py` — OpenCV frame extraction and validation
- `services/pose_estimator.py` — MediaPipe pose estimation and frame annotation
- `services/biomechanics/base.py` — `BiomechanicsResult` and `CheckpointScore` dataclasses
- `services/biomechanics/shooting.py` — 5 checkpoints: plant foot, knee over ball, hip rotation, body lean, follow-through
- `services/biomechanics/passing.py` — 4 checkpoints: body shape, head position, plant foot, weight transfer
- `services/feedback_generator.py` — Claude API call; returns `None` on failure (triggers 206)

**Technique identifiers:** The `technique` form field must be one of the keys in `TECHNIQUE_ANALYZERS` (`routers/analyze.py`): currently `shooting_driven` and `passing_short`. Anything else returns 422. These exact strings are also used by `TECHNIQUE_LABELS` in `feedback_generator.py`.

**Adding a new technique:** Create `services/biomechanics/<technique>.py`, register its analyzer in the `TECHNIQUE_ANALYZERS` dict in `routers/analyze.py`, and add a display label in `TECHNIQUE_LABELS` in `feedback_generator.py`. Note `find_contact_frame_idx` lives in `shooting.py` and is reused for every technique.

### Frontend Structure

- `app/page.tsx` — Home page: video upload + technique + kicking foot selection
- `app/results/page.tsx` — Results: reads analysis data from `sessionStorage`
- `lib/api.ts` — `analyzeVideo()`: POSTs multipart form-data, handles 200 (full) and 206 (partial, LLM failed)
- Cross-page state passed via `sessionStorage` (not URL params or React context)

### Error Responses

| Condition | HTTP Status |
|-----------|-------------|
| File >50MB or video >30s | 400 |
| No person detected | 422 |
| Invalid technique | 422 |
| Claude API failure | 206 (scores/frames still returned) |

### Test Strategy

Tests live in `backend/tests/`. The `conftest.py` fixture creates a real 60-frame MP4 for video processor tests. All external dependencies (MediaPipe, Claude API) are mocked in unit/integration tests. Router tests use FastAPI `TestClient` with all services mocked.

## Environment Variables

| Variable | Location | Purpose |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | `backend/.env` | Claude API access |
| `ALLOWED_ORIGINS` | `backend/.env` | Comma-separated CORS origins |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | Backend base URL |
