import Link from "next/link";
import { AuditResults } from "../../../components/AuditResults";

export default async function AuditPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-8">
      <div className="mb-6">
        <Link
          href="/dashboard"
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          &larr; Dashboard
        </Link>
      </div>
      <AuditResults auditId={id} />
    </main>
  );
}
