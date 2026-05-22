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
