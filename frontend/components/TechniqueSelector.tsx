export const TECHNIQUES = [
  { value: "shooting_driven", label: "Shooting — Driven Shot" },
  { value: "passing_short", label: "Passing — Short Pass" },
] as const;

export type TechniqueValue = (typeof TECHNIQUES)[number]["value"];

interface Props {
  value: TechniqueValue | "";
  onChange: (v: TechniqueValue) => void;
}

export default function TechniqueSelector({ value, onChange }: Props) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">
        Technique
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as TechniqueValue)}
        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
      >
        <option value="">Select a technique...</option>
        {TECHNIQUES.map((t) => (
          <option key={t.value} value={t.value}>
            {t.label}
          </option>
        ))}
      </select>
    </div>
  );
}
