"use client";

import { useEffect, useState } from "react";
import { getAudit, type AuditResponse } from "../lib/api";
import { RiskBanner } from "./RiskBanner";
import { ClauseCard } from "./ClauseCard";
import { DocumentDownloads } from "./DocumentDownloads";

export function AuditResults({ auditId }: { auditId: string }) {
  const [audit, setAudit] = useState<AuditResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        const data = await getAudit(auditId);
        if (cancelled) return;
        setAudit(data);

        if (data.status === "processing") {
          timer = setTimeout(poll, 2000);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load audit");
        }
      }
    }

    poll();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [auditId]);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        {error}
      </div>
    );
  }

  if (!audit) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (audit.status === "processing") {
    return (
      <div className="text-center py-12 space-y-4">
        <div className="animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full mx-auto" />
        <p className="text-gray-600">
          Analyzing your agreement... This usually takes 10-30 seconds.
        </p>
        <p className="text-sm text-gray-400">{audit.file_name}</p>
      </div>
    );
  }

  if (audit.status === "failed") {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        <p className="font-medium">Analysis failed</p>
        <p className="text-sm mt-1">{audit.error || "Unknown error"}</p>
      </div>
    );
  }

  const fired = audit.patterns.filter((p) => p.fired);
  const notFired = audit.patterns.filter((p) => !p.fired);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold">Audit Results</h2>
        <p className="text-sm text-gray-500 mt-1">
          {audit.file_name}
          {audit.page_count && ` -- ${audit.page_count} pages`}
          {audit.ocr_used && " (OCR)"}
        </p>
      </div>

      <RiskBanner
        riskLevel={audit.risk_level}
        redFlags={audit.red_flags}
        yellowFlags={audit.yellow_flags}
      />

      <DocumentDownloads
        auditId={auditId}
        available={audit.documents_available}
      />

      {/* Fired patterns */}
      {fired.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">
            Detected Issues ({fired.length})
          </h3>
          <div className="space-y-3">
            {fired.map((p) => (
              <ClauseCard key={p.pattern_id} pattern={p} />
            ))}
          </div>
        </div>
      )}

      {/* Not fired */}
      {notFired.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3 text-gray-500">
            Not Detected ({notFired.length})
          </h3>
          <div className="space-y-1">
            {notFired.map((p) => (
              <div
                key={p.pattern_id}
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-400"
              >
                <span className="w-6">{p.pattern_id}</span>
                <span>{p.pattern_name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
