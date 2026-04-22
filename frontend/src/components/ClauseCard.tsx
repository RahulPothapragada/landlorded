"use client";

import { useState } from "react";
import { SeverityBadge } from "./SeverityBadge";
import type { PatternSummary } from "../lib/api";

export function ClauseCard({ pattern }: { pattern: PatternSummary }) {
  const [open, setOpen] = useState(pattern.severity === "RED FLAG");

  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
      >
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500 w-6">
            {pattern.pattern_id}
          </span>
          <span className="font-medium">{pattern.pattern_name}</span>
        </div>
        <div className="flex items-center gap-2">
          <SeverityBadge severity={pattern.severity} />
          <span className="text-gray-400">{open ? "−" : "+"}</span>
        </div>
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-4 border-t">
          {pattern.verdict && (
            <div className="mt-3 bg-blue-50 border-l-4 border-blue-400 p-3 text-sm">
              {pattern.verdict}
            </div>
          )}

          {pattern.matched_text.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
                From your agreement
              </h4>
              {pattern.matched_text.map((text, i) => (
                <blockquote
                  key={i}
                  className="border-l-3 border-yellow-400 bg-yellow-50 pl-3 py-2 text-sm italic text-gray-700 mb-2"
                >
                  &ldquo;{text.length > 300 ? text.slice(0, 300) + "..." : text}
                  &rdquo;
                </blockquote>
              ))}
            </div>
          )}

          {pattern.statute_citation && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
                Applicable law
              </h4>
              <p className="text-sm text-gray-700">{pattern.statute_citation}</p>
            </div>
          )}

          {pattern.suggested_rewrite && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
                Suggested rewrite
              </h4>
              <div className="bg-green-50 border-l-4 border-green-400 p-3 text-sm">
                &ldquo;{pattern.suggested_rewrite}&rdquo;
              </div>
            </div>
          )}

          {pattern.notice_paragraph && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
                For your legal notice
              </h4>
              <div className="bg-purple-50 border-l-4 border-purple-400 p-3 text-sm">
                &ldquo;{pattern.notice_paragraph}&rdquo;
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
