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
