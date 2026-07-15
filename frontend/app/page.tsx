"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import VideoUpload from "@/components/VideoUpload";
import TechniqueSelector, { TechniqueValue } from "@/components/TechniqueSelector";
import { analyzeVideo, type AnalysisResult } from "@/lib/api";

// Persist the result for the results page. Annotated frames are large base64 JPEGs that can
// exceed the ~5MB sessionStorage quota; if storing the full payload throws, drop the frames
// so a successful analysis still shows scores + coaching instead of surfacing as an error.
function storeAnalysisResult(result: AnalysisResult) {
  try {
    sessionStorage.setItem("analysisResult", JSON.stringify(result));
  } catch {
    const trimmed: AnalysisResult = { ...result, annotated_frames: [], framesOmitted: true };
    sessionStorage.setItem("analysisResult", JSON.stringify(trimmed));
  }
}

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
      storeAnalysisResult(result);
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
