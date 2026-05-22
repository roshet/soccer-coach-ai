# AI Soccer Coach

AI-powered biomechanical technique analysis for professional soccer players. Upload a short video of your technique and receive instant coaching feedback — plant foot positioning, hip rotation, body lean, follow-through, and more — benchmarked against professional standards.

## Demo

> Record a short Loom or YouTube demo and add the link here before sharing your portfolio.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TailwindCSS |
| Backend | FastAPI, Python 3.11 |
| Pose Estimation | MediaPipe Pose, OpenCV |
| Biomechanics | NumPy |
| AI Feedback | Claude API (claude-sonnet-4-6) |
| Frontend Deploy | Vercel |
| Backend Deploy | Railway |

## Architecture

```
Video Upload
    │
    ▼
Frame Extraction (OpenCV)
    │
    ▼
Pose Estimation (MediaPipe) ── 33 body landmarks per frame
    │
    ▼
Biomechanics Scoring (NumPy) ── technique-specific rules, 0–100 per checkpoint
    │
    ▼
AI Coaching Feedback (Claude API) ── UEFA-standard coaching report
    │
    ▼
Results UI (Next.js)
```

## Supported Techniques (MVP)

| Technique | Checkpoints Analyzed |
|---|---|
| Shooting — Driven Shot | Plant foot position, knee over ball, hip rotation, body lean, follow-through |
| Passing — Short Pass | Body shape, head position, plant foot position, weight transfer |

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # add your ANTHROPIC_API_KEY
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL
npm run dev
```

### Run Backend Tests

```bash
cd backend
pytest tests/ -v
```

All 26 tests should pass.

## Deployment

### Backend → Railway

1. Create a new Railway project and connect this GitHub repo
2. Set root directory to `backend/`
3. Add environment variable: `ANTHROPIC_API_KEY=your_key`
4. Railway auto-detects the Dockerfile and deploys
5. Copy the generated URL (e.g. `https://ai-soccer-coach-backend.up.railway.app`)
6. Add `ALLOWED_ORIGINS=https://your-app.vercel.app` to Railway env vars

### Frontend → Vercel

```bash
cd frontend
npx vercel
# Set NEXT_PUBLIC_API_URL to your Railway URL when prompted
npx vercel --prod
```

## Project Structure

```
CSProject/
├── backend/
│   ├── main.py                          # FastAPI app entry point
│   ├── routers/analyze.py               # POST /analyze endpoint
│   ├── services/
│   │   ├── video_processor.py           # OpenCV frame extraction
│   │   ├── pose_estimator.py            # MediaPipe pose estimation
│   │   ├── feedback_generator.py        # Claude API integration
│   │   └── biomechanics/
│   │       ├── base.py                  # BiomechanicsResult dataclass
│   │       ├── shooting.py              # Shooting technique analysis
│   │       └── passing.py              # Passing technique analysis
│   └── tests/                           # 26 tests, all passing
└── frontend/
    ├── app/
    │   ├── page.tsx                     # Upload page
    │   └── results/page.tsx             # Results page
    ├── components/
    │   ├── VideoUpload.tsx
    │   ├── TechniqueSelector.tsx
    │   ├── ScoreCard.tsx
    │   ├── AnnotatedFrames.tsx
    │   └── CoachingReport.tsx
    └── lib/api.ts                       # API client
```
