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
