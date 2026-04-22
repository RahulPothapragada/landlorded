# Landlorded — Project Context

## What it is
An AI agent that reads a Chennai rental agreement, flags unfair or illegal clauses under Tamil Nadu law, and generates a legal notice + consumer forum complaint. Started at the Claude Code hackathon, now a personal project.

**Tagline:** "Getting landlorded? Get un-landlorded."

## Who it's for
Young renters in Chennai (students, first-job professionals, group houses) who can't afford ₹5k+ lawyer consults for deposit/rent-hike disputes and don't know TN-specific rental law.

## Origin story (for the pitch)
Builder (me, the user) paid ₹4.5L security deposit (6× monthly rent) for a flat in Estancia, Vallancheri, Chengalpattu. Landlord delayed renewal discussions from January until tenant had no alternatives, then forced through a 20%+ rent hike. Separately, broker demanded ₹1.9L with no justification. Tool exists to stop this pattern.

## Scope lock (non-negotiable)
- **Geography:** Tamil Nadu only, Chennai focus
- **Property type:** Residential only
- **Dispute types:** Deposit issues, illegal rent hikes, unfair renewal terms, unjustified fees
- **NOT building:** Web app, mobile app, auth, database, multi-state, commercial leases, eviction defense, e-signature, landlord-side view

## Three modes (one tool)
1. **Audit Mode** — "I have an agreement. Tell me what's wrong with it." (Pre-signing or mid-tenancy review)
2. **Dispute Mode** — "Landlord is refusing refund / making unfair demand. Help me push back." (Produces legal notice + consumer complaint)
3. **Renewal Mode** — "Landlord is hiking rent / pressuring new deed signing. What should I check?"

## Deliverables (what the tool outputs)
- `report.pdf` — Plain-English analysis with clause-by-clause flags + TN statute citations
- `legal_notice.pdf` — Properly formatted notice citing user's actual clauses
- `consumer_complaint.pdf` — Draft for Chennai District Consumer Commission filing
- `whatsapp_message.txt` — Bilingual Tamil + English warning-shot message
- `evidence_checklist.md` — What to gather before filing

## Interface
CLI tool complete (`python landlorded.py audit agreement.pdf`). Now building full web app.

## Stack
- Python (Mac dev environment)
- Claude Code as agent runtime
- `pypdf` / `pdfplumber` for PDF reading
- `pandoc` or `python-docx` + `weasyprint` for PDF output
- `rich` for CLI output
- No DB, no backend, no auth

## Repo structure
```
landlorded/
├── CONTEXT.md                    ← this file
├── README.md
├── corpus/
│   ├── statutes/
│   │   ├── tn_act_2017.md        ✅ DONE
│   │   ├── tn_act_2017_rules.md  ✅ DONE (verbatim text with amendments incorporated)
│   │   ├── tn_rent_authority.md  ✅ DONE (Chengalpattu jurisdiction added)
│   │   ├── cpa_2019.md           ✅ DONE
│   │   ├── tpa_sections.md       ✅ DONE
│   │   └── indian_stamp_act.md   ✅ DONE
│   ├── templates/
│   │   ├── legal_notice.md       ✅ DONE
│   │   └── consumer_complaint.md ✅ DONE
│   └── samples/                  (sample legal notices for reference)
├── specs/
│   └── patterns.md               ⚠️ NEEDS UPDATES (3 pattern changes pending)
└── test_agreements/
    ├── sample_01_estancia.pdf    ✅ (user's own agreement)
    ├── sample_02_template.pdf    ❌ TODO
    └── sample_03_other.pdf       ❌ TODO
```

## The 9 clause patterns (core of the tool)
1. **Deposit-to-rent ratio** — flag if >3 months; address Section 11 "Save an agreement to the contrary" qualifier. Confidence MEDIUM.
2. **Escalation clause with no upper cap** (e.g., "not less than 5%")
3. **Asymmetric lock-in** (tenant locked, landlord free)
4. **Missing refund timeline** — Section 11(2) requires refund at handover. Confidence HIGH.
5. **Early-termination penalty**
6. **Deduction clause without itemization requirement**
7. **Stamp duty adequacy** (₹100 paper for high-value lease)
8. **Registration status** (TN Act 2017 Section 4 mandates Rent Authority registration)
9. **Joint-tenant liability** (multiple tenants, unclear refund mechanics)
10. **NEW: Essential services guarantee** — Section 20 non-overridable right ✅ Added as Pattern 11 in patterns.md

## Critical legal finding from Day 1 research
TN Act 2017 Section 11(1): "Save an agreement to the contrary, it shall be unlawful to charge a security deposit in excess of three times the monthly rent."

The **"Save an agreement to the contrary"** qualifier means the 3-month cap is a *default*, not a ceiling. Signed agreements can contract around it. Tool must NOT claim excessive deposits are "illegal" outright — must frame around unconscionability, unequal bargaining power, unregistered-agreement issues, and unfair trade practice under CPA 2019.

## 7-day plan
- **Day 1:** Legal corpus + pattern spec. NO CODE. ✅ DONE
- **Day 2:** PDF ingestion + clause extractor ✅ DONE
- **Day 3:** Legal reasoning layer over corpus ✅ DONE
- **Day 4:** Document generation (legal notice + consumer complaint PDFs) ✅ DONE
- **Day 5:** Tamil WhatsApp generator + CLI polish ✅ DONE
- **Day 6 (current):** Full-stack web app — see architecture below
- **Day 7:** Demo recording, pitch video, submission

## Day 1 tasks (all complete)
All corpus, pattern spec, and template tasks are done. CLI tool is functional.

## Current: Full-stack web app architecture

**Stack:**
- **Frontend:** Next.js + React (Vercel)
- **Backend:** FastAPI wrapping existing Python core (Render, Docker)
- **Auth/DB/Storage:** Supabase (PostgreSQL + RLS + Storage)

**Monorepo structure:**
```
landlorded/
├── backend/
│   ├── app/                   # FastAPI (main.py, config.py, deps.py)
│   │   ├── routers/           # audits.py, documents.py, users.py
│   │   ├── models/schemas.py
│   │   ├── db/queries.py
│   │   └── services/          # audit_service.py, storage_service.py
│   ├── core/                  # Existing CLI modules moved here unchanged
│   ├── corpus/                # Statute files bundled in Docker image
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/app/               # Landing, login, dashboard, audit/new, audit/[id]
│   ├── src/components/        # AuditUploader, AuditResults, ClauseCard, etc.
│   └── src/lib/               # Supabase client, API wrapper
└── supabase/migrations/
```

**API endpoints:**
- `POST /audits` → 202 (starts processing)
- `GET /audits` → user's past audits
- `GET /audits/{id}` → full results (or 202 if processing)
- `DELETE /audits/{id}` → delete audit + files
- `GET /audits/{id}/documents/{type}` → signed download URL
- `GET/PATCH /users/me` → profile

**Processing flow:** Upload → Supabase Storage → FastAPI BackgroundTask runs extract → detect → reason → generate → results as JSONB + docs to storage → frontend polls until complete.

**Key decisions:**
- Only `generator.py` changes (add `generate_report_bytes()`)
- Corpus loaded once at startup, cached as singleton
- Private storage with 60-second signed URLs
- No Celery/Redis initially — FastAPI BackgroundTasks
- Render Starter ($7/mo) to launch

**Database (3 tables):** profiles, audits (JSONB results), RLS policies

## Ground rules for the corpus (DO NOT VIOLATE)
- **Verbatim statute text, not summaries.** Paraphrases get cited wrong and hurt users.
- **Where law is ambiguous, say so in the file.** Honest corpus = honest tool.
- **One file per source of authority.** Don't merge Act + Rules + procedural info.
- **Cite amendments explicitly.** "as amended up to [year]" in every citation.

## Separate but related: builder's personal case
User has live tenancy at Estancia Apt 1136, lease expires April 30, 2026 (11 days from Day 1). Signing new lease at hiked rate despite duress because no alternative housing. Key protection steps:
- Look for "supersession" / "entire agreement" clauses in new deed, strike them
- Add handwritten note preserving ₹4.5L deposit claim with 30-day refund timeline
- Export WhatsApp chats with landlord + broker
- Do NOT pay ₹1.9L brokerage without GST invoice (separate track from lease signing)

Project and personal case are intertwined — user's real documents are the tool's primary test cases.

## Honest pitch frame (for the demo)
"I paid ₹4.5 lakh security deposit — 6 months of rent — to rent a flat in Chennai. My landlord has stalled refund discussions for months. Lawyers quoted ₹8,000 just to start. Every year, thousands of young Indians in Chennai lose their deposits because the legal path costs more than the loss. Landlorded is the tool I wish I'd had before I signed. [Drop PDF] [Show analysis] [Show generated legal notice with actual landlord name and clauses] [Show Tamil WhatsApp warning]. This is what AI agents can do that static legal websites and form-based notice generators can't."

---

**Resume instructions for new chat:** "Read CONTEXT.md. CLI tool is complete. We're building the full-stack web app — backend (FastAPI) + frontend (Next.js) + Supabase. Next: [whichever part of the web app you're working on]."
