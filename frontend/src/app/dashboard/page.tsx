"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "../../lib/supabase/client";
import { listAudits, deleteAudit, type AuditListItem } from "../../lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [audits, setAudits] = useState<AuditListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        router.push("/login");
        return;
      }

      try {
        const data = await listAudits();
        setAudits(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load audits");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [router]);

  async function handleDelete(id: string) {
    if (!confirm("Delete this audit?")) return;
    try {
      await deleteAudit(id);
      setAudits((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Delete failed");
    }
  }

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/");
  }

  const riskColors: Record<string, string> = {
    HIGH: "text-red-600",
    MODERATE: "text-yellow-600",
    LOW: "text-green-600",
  };

  return (
    <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Your Audits</h1>
        <div className="flex gap-3">
          <Link
            href="/audit/new"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            New Audit
          </Link>
          <button
            onClick={handleSignOut}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Sign out
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
        </div>
      )}

      {error && <p className="text-red-600">{error}</p>}

      {!loading && audits.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No audits yet.</p>
          <Link
            href="/audit/new"
            className="text-blue-600 font-medium hover:underline"
          >
            Upload your first agreement
          </Link>
        </div>
      )}

      {audits.length > 0 && (
        <div className="space-y-3">
          {audits.map((audit) => (
            <div
              key={audit.id}
              className="border rounded-lg p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <Link href={`/audit/${audit.id}`} className="flex-1 min-w-0">
                <p className="font-medium truncate">{audit.file_name}</p>
                <div className="flex gap-3 text-sm text-gray-500 mt-1">
                  <span>{audit.mode}</span>
                  <span>
                    {new Date(audit.created_at).toLocaleDateString()}
                  </span>
                  {audit.risk_level && (
                    <span
                      className={`font-medium ${riskColors[audit.risk_level] || ""}`}
                    >
                      {audit.risk_level}
                    </span>
                  )}
                  {audit.status === "processing" && (
                    <span className="text-blue-500">Processing...</span>
                  )}
                  {audit.status === "failed" && (
                    <span className="text-red-500">Failed</span>
                  )}
                </div>
              </Link>
              <button
                onClick={() => handleDelete(audit.id)}
                className="text-gray-400 hover:text-red-500 ml-3 text-sm"
                title="Delete audit"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
