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
