export function RiskBanner({
  riskLevel,
  redFlags,
  yellowFlags,
}: {
  riskLevel: string | null;
  redFlags: number;
  yellowFlags: number;
}) {
  if (!riskLevel) return null;

  const styles: Record<string, string> = {
    HIGH: "bg-red-50 border-red-300 text-red-900",
    MODERATE: "bg-yellow-50 border-yellow-300 text-yellow-900",
    LOW: "bg-green-50 border-green-300 text-green-900",
  };

  const labels: Record<string, string> = {
    HIGH: "HIGH RISK",
    MODERATE: "MODERATE RISK",
    LOW: "LOW RISK",
  };

  return (
    <div className={`rounded-lg border p-4 ${styles[riskLevel] || ""}`}>
      <p className="font-bold text-lg">{labels[riskLevel]}</p>
      <p className="text-sm mt-1">
        {redFlags > 0 && (
          <span>
            {redFlags} red flag{redFlags !== 1 && "s"}
          </span>
        )}
        {redFlags > 0 && yellowFlags > 0 && ", "}
        {yellowFlags > 0 && (
          <span>
            {yellowFlags} yellow flag{yellowFlags !== 1 && "s"}
          </span>
        )}
        {redFlags === 0 && yellowFlags === 0 && "No flags raised."}
      </p>
    </div>
  );
}
