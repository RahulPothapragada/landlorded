import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="flex-1 flex flex-col items-center justify-center px-4">
      <div className="max-w-2xl text-center space-y-6">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Landlorded
        </h1>
        <p className="text-lg text-gray-500">
          Getting landlorded? Get un-landlorded.
        </p>
        <p className="text-gray-600 max-w-lg mx-auto">
          Upload your Chennai rental agreement. Get a clause-by-clause audit
          against Tamil Nadu tenancy law, a ready-to-send legal notice, and a
          bilingual WhatsApp warning message.
        </p>

        <div className="flex gap-4 justify-center pt-4">
          <Link
            href="/audit/new"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Analyze Agreement
          </Link>
          <Link
            href="/login"
            className="border border-gray-300 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Sign In
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-8 text-left">
          <div>
            <h3 className="font-semibold mb-1">11 Clause Patterns</h3>
            <p className="text-sm text-gray-500">
              Deposit ratio, refund timeline, lock-in, registration, and more
              &mdash; each checked against TN statutes.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-1">Legal Documents</h3>
            <p className="text-sm text-gray-500">
              Report PDF, legal notice, evidence checklist &mdash; populated
              with your actual clause text and amounts.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-1">WhatsApp Message</h3>
            <p className="text-sm text-gray-500">
              Bilingual Tamil + English warning message with section references.
              Send before the legal notice.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
