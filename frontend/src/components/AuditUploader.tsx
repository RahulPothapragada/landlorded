"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { createAudit } from "../lib/api";

export function AuditUploader() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState("audit");
  const [tenantName, setTenantName] = useState("");
  const [landlordName, setLandlordName] = useState("");
  const [premises, setPremises] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError("");

    try {
      const result = await createAudit(
        file,
        mode,
        tenantName,
        landlordName,
        premises
      );
      router.push(`/audit/${result.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setUploading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File drop zone */}
      <div
        onClick={() => fileRef.current?.click()}
        className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/50 transition-colors"
      >
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        {file ? (
          <p className="font-medium">{file.name}</p>
        ) : (
          <div>
            <p className="text-gray-500">
              Drop your lease agreement PDF here, or click to browse
            </p>
            <p className="text-xs text-gray-400 mt-1">Max 20MB</p>
          </div>
        )}
      </div>

      {/* Mode selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Mode
        </label>
        <div className="grid grid-cols-3 gap-3">
          {[
            {
              value: "audit",
              label: "Audit",
              desc: "Analyze clauses",
            },
            {
              value: "dispute",
              label: "Dispute",
              desc: "Analyze + generate docs",
            },
            {
              value: "renewal",
              label: "Renewal",
              desc: "Check renewal terms",
            },
          ].map((m) => (
            <button
              key={m.value}
              type="button"
              onClick={() => setMode(m.value)}
              className={`p-3 rounded-lg border text-left transition-colors ${
                mode === m.value
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 hover:bg-gray-50"
              }`}
            >
              <p className="font-medium text-sm">{m.label}</p>
              <p className="text-xs text-gray-500">{m.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Details (shown for dispute/renewal modes) */}
      {mode !== "audit" && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your name
            </label>
            <input
              type="text"
              value={tenantName}
              onChange={(e) => setTenantName(e.target.value)}
              placeholder="Rahul Pothapragada"
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Landlord name
            </label>
            <input
              type="text"
              value={landlordName}
              onChange={(e) => setLandlordName(e.target.value)}
              placeholder="Mrs. J.E. Vasanth"
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Premises address
            </label>
            <input
              type="text"
              value={premises}
              onChange={(e) => setPremises(e.target.value)}
              placeholder="Apt 1136, Estancia, Chengalpattu"
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
        </div>
      )}

      {error && (
        <p className="text-sm text-red-600 bg-red-50 p-3 rounded">{error}</p>
      )}

      <button
        type="submit"
        disabled={!file || uploading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {uploading ? "Analyzing..." : "Analyze Agreement"}
      </button>
    </form>
  );
}
