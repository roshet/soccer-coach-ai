# AI Soccer Coach — Design Spec
**Date:** 2026-05-20  
**Author:** Rohan  
**Status:** Approved

---

## Overview

A web application where professional and aspiring professional soccer players upload a short video of themselves performing a technique, select the technique type, and receive instant AI-powered biomechanical analysis and professional-standard coaching feedback.

**Target users:** Professional, semi-professional, and academy players seeking technique feedback outside of formal training sessions.

**Core value:** Instant, specific, professional-grade coaching feedback on demand — referencing how elite players execute the same technique.

---

## Architecture

```
User (Browser)
     │
     ▼
Next.js Frontend (Vercel)
  - Video upload + technique selector
  - Results display with annotated frames
     │
     ▼
FastAPI Backend (Railway/Render)
     │
     ├── Video Processor
     │     └── OpenCV → extracts key frames
     │           └── MediaPipe → 33 pose landmarks per frame
     │
     ├── Biomechanics Analyzer
     │     └── Technique-specific rules engine
     │         (joint angles, positioning, timing)
     │
     └── Feedback Generator
           └── Claude API (claude-sonnet-4-6) → coaching report
```

**Core user flow:**
1. Player uploads video (≤30s, ≤50MB) and selects technique type
2. Backend extracts key frames via OpenCV, runs MediaPipe to get 33 body landmarks per frame
3. Biomechanics analyzer evaluates landmarks against professional standards for that technique
4. Structured results (scores + flags) sent to Claude API
5. Claude returns a 300–500 word coaching report
6. Frontend displays report alongside annotated freeze-frames

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TailwindCSS |
| Backend | FastAPI (Python) |
| Pose Estimation | MediaPipe Pose, OpenCV |
| Numerical Analysis | NumPy |
| AI Feedback | Claude API (claude-sonnet-4-6) |
| Frontend Deployment | Vercel |
| Backend Deployment | Railway or Render |

---

## Supported Techniques (MVP)

MVP ships with **Shooting** and **Passing** only. Additional techniques added in v2.

| Technique | Key Checkpoints |
|---|---|
| Shooting (driven) | Plant foot position, knee over ball, hip rotation, body lean, follow-through direction |
| Passing | Body shape, foot angle at contact, head position, weight transfer |

**V2 additions:** Heading, Crossing, First Touch

---

## Biomechanics Rules Engine

Each technique defines a set of measurable checkpoints evaluated from MediaPipe landmarks. Each checkpoint is scored 0–100 based on deviation from professional standard.

**Example — Shooting (Driven Shot):**

| Checkpoint | Professional Standard | How Measured |
|---|---|---|
| Plant foot position | 6–8 inches beside ball, pointed at target | Ankle landmark distance + angle to target direction |
| Knee over ball | Knee landmark directly above ankle at contact | X/Y delta between knee and ankle at contact frame |
| Hip rotation | Full rotation through the ball (≥80° from approach) | Hip landmark angle delta across key frames |
| Body lean | Slight forward lean (5–15°) at contact | Shoulder-to-hip angle at contact frame |
| Follow-through | Straight toward target, knee height minimum | Foot trajectory angle post-contact |

**Scoring payload sent to Claude:**
```json
{
  "technique": "Shooting - Driven Shot",
  "scores": {
    "plant_foot_position": 58,
    "knee_over_ball": 82,
    "hip_rotation": 71,
    "body_lean": 90,
    "follow_through": 65
  },
  "flags": [
    "Plant foot too far from ball",
    "Follow-through cuts off early"
  ],
  "overall_score": 73
}
```

Claude receives this payload with a system prompt priming it as a UEFA-licensed professional coach. It returns a natural language coaching report with specific, actionable cues referencing how elite players execute the technique differently.

---

## API Endpoints

### `POST /analyze`
Accepts video file + technique type, returns full analysis.

**Request:** `multipart/form-data`
- `video`: file (mp4, mov, avi — max 50MB)
- `technique`: string (e.g. `"shooting_driven"`)

**Response:**
```json
{
  "overall_score": 73,
  "scores": { ... },
  "flags": [ ... ],
  "coaching_report": "Your plant foot positioning is the primary area...",
  "annotated_frames": ["base64_frame_1", "base64_frame_2", "base64_frame_3"]
}
```

**Errors:**
- `400` — video exceeds size/length limit
- `422` — no player detected in video
- `206` — analysis succeeded but LLM feedback unavailable (returns scores/flags only)

---

## Frontend Pages

### `/` — Home / Upload
- Hero section explaining the product
- Drag-and-drop video upload
- Technique selector dropdown
- Filming guide tip (angle, distance, lighting)
- Submit button → loading state during analysis

### `/results` — Analysis Results
- Overall score (0–100) prominently displayed
- Per-checkpoint score breakdown
- 3 annotated freeze-frames (approach, contact, follow-through)
- Full coaching report
- "Analyze another video" CTA

---

## Error Handling

| Scenario | Handling |
|---|---|
| MediaPipe landmark confidence < 0.7 on key landmark | Return partial analysis with warning: "Video quality insufficient for [checkpoint] — film closer with better lighting" |
| Overhead or directly side-on camera angle | Filming guide on upload screen prevents this; low confidence scores surface it anyway |
| Video > 30s or > 50MB | Rejected at upload with clear message |
| No player detected | `422` response: "No player detected — ensure the player is clearly visible throughout the video" |
| Claude API timeout/failure | Retry once; if fails again, return scores + flags without narrative report (`206`) |

---

## MVP Scope

**In scope:**
- Video upload + technique selection
- MediaPipe pose estimation pipeline
- Biomechanics rules for Shooting and Passing
- Claude-powered coaching report
- Annotated freeze-frames
- Deployed frontend + backend

**Out of scope (v2):**
- User accounts / history
- Heading, Crossing, First Touch techniques
- Side-by-side comparison with professional player footage
- Mobile app
- Real-time (live camera) analysis

---

## Portfolio Notes

- Deploy publicly and record a demo video — embed in README and portfolio site
- Potential pilot: UC soccer program or local academy for real user testimonials
- README should include architecture diagram, tech stack badges, and sample output
