"use client";

import { useState } from "react";
import { getDocumentUrl } from "../lib/api";

const DOC_LABELS: Record<string, { label: string; icon: string }> = {
  report: { label: "Audit Report", icon: "PDF" },
  legal_notice: { label: "Legal Notice", icon: "PDF" },
  evidence_checklist: { label: "Evidence Checklist", icon: "MD" },
  whatsapp_message: { label: "WhatsApp Message", icon: "TXT" },
};

export function DocumentDownloads({
  auditId,
  available,
}: {
  auditId: string;
  available: string[];
}) {
  const [loading, setLoading] = useState<string | null>(null);

  async function handleDownload(docType: string) {
    setLoading(docType);
    try {
      const url = await getDocumentUrl(auditId, docType);
      window.open(url, "_blank");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Download failed");
    } finally {
      setLoading(null);
    }
  }

  if (available.length === 0) return null;

  return (
    <div>
      <h3 className="font-semibold mb-3">Documents</h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {available.map((docType) => {
          const meta = DOC_LABELS[docType] || {
            label: docType,
            icon: "FILE",
          };
          return (
            <button
              key={docType}
              onClick={() => handleDownload(docType)}
              disabled={loading === docType}
              className="flex flex-col items-center gap-1 p-4 border rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
            >
              <span className="text-xs font-mono bg-gray-200 px-2 py-0.5 rounded">
                {meta.icon}
              </span>
              <span className="text-sm font-medium text-center">
                {loading === docType ? "Loading..." : meta.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
