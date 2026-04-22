const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getToken(): Promise<string> {
  const { createClient } = await import("./supabase/client");
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token || "";
}

async function apiFetch(path: string, options: RequestInit = {}) {
  const token = await getToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `API error ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

export interface AuditListItem {
  id: string;
  status: "processing" | "complete" | "failed";
  mode: string;
  created_at: string;
  file_name: string;
  risk_level: string | null;
  red_flags: number;
  yellow_flags: number;
}

export interface PatternSummary {
  pattern_id: number;
  pattern_name: string;
  fired: boolean;
  severity: string | null;
  explanation: string;
  verdict: string;
  statute_citation: string;
  suggested_rewrite: string;
  notice_paragraph: string;
  extracted: Record<string, unknown>;
  matched_text: string[];
}

export interface AuditResponse extends AuditListItem {
  page_count: number | null;
  ocr_used: boolean;
  patterns: PatternSummary[];
  documents_available: string[];
  error: string | null;
}

export async function createAudit(
  file: File,
  mode: string,
  tenantName: string,
  landlordName: string,
  premises: string
): Promise<{ id: string; status: string }> {
  const form = new FormData();
  form.append("file", file);
  form.append("mode", mode);
  form.append("tenant_name", tenantName);
  form.append("landlord_name", landlordName);
  form.append("premises", premises);

  return apiFetch("/audits", { method: "POST", body: form });
}

export async function listAudits(): Promise<AuditListItem[]> {
  return apiFetch("/audits");
}

export async function getAudit(id: string): Promise<AuditResponse> {
  return apiFetch(`/audits/${id}`);
}

export async function deleteAudit(id: string): Promise<void> {
  await apiFetch(`/audits/${id}`, { method: "DELETE" });
}

export async function getDocumentUrl(
  auditId: string,
  docType: string
): Promise<string> {
  const data = await apiFetch(`/audits/${auditId}/documents/${docType}`);
  return data.url;
}
