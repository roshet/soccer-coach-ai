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
