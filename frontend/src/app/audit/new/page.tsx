import { AuditUploader } from "../../../components/AuditUploader";
import Link from "next/link";

export default function NewAuditPage() {
  return (
    <main className="flex-1 max-w-xl mx-auto w-full px-4 py-8">
      <div className="mb-6">
        <Link
          href="/dashboard"
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          &larr; Dashboard
        </Link>
        <h1 className="text-2xl font-bold mt-2">Analyze Agreement</h1>
        <p className="text-sm text-gray-500 mt-1">
          Upload your Chennai rental agreement PDF for a clause-by-clause audit.
        </p>
      </div>
      <AuditUploader />
    </main>
  );
}
