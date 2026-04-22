export function SeverityBadge({ severity }: { severity: string | null }) {
  if (!severity) return <span className="text-gray-400">--</span>;

  const styles: Record<string, string> = {
    "RED FLAG": "bg-red-100 text-red-800 border-red-200",
    "YELLOW FLAG": "bg-yellow-100 text-yellow-800 border-yellow-200",
    INFO: "bg-green-100 text-green-800 border-green-200",
  };

  return (
    <span
      className={`inline-block px-2 py-0.5 text-xs font-semibold rounded border ${styles[severity] || "bg-gray-100 text-gray-600"}`}
    >
      {severity}
    </span>
  );
}
