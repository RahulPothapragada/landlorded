# Landlorded

**Getting landlorded? Get un-landlorded.**

AI-powered rental agreement auditor for Tamil Nadu tenants. Upload a Chennai rental agreement PDF — get a clause-by-clause audit against TN tenancy law, a ready-to-send legal notice, and a bilingual Tamil + English WhatsApp warning message.

## The problem

Every year, thousands of young renters in Chennai lose their security deposits because:
- They don't know TN-specific rental law
- Lawyers quote Rs. 5,000–8,000 just to review an agreement
- Legal notice generators are generic and don't cite actual clauses
- By the time they realize the agreement is unfair, they've already signed

**Landlorded** is the tool I wish I had before I paid Rs. 4,50,000 (6 months' rent) as security deposit for a flat in Estancia, Vallancheri. My landlord stalled renewal discussions for months, then forced through a 20%+ rent hike with no upper cap.

## What it does

Drop a lease agreement PDF. Get back:

| Output | What it contains |
|--------|-----------------|
| **Audit report** | Clause-by-clause analysis with severity flags and statute citations |
| **Legal notice** | Formal notice with your actual clauses, amounts, and TN Act references |
| **Evidence checklist** | Pattern-specific list of what to gather before filing |
| **WhatsApp message** | Bilingual Tamil + English warning-shot message |

## The 11 patterns it detects

| # | Pattern | What it catches |
|---|---------|----------------|
| 1 | Deposit-to-rent ratio | Deposit above 3-month statutory norm |
| 2 | Missing refund timeline | No itemized refund mechanism |
| 3 | Pre-tenancy advance | Booking advance with unclear treatment |
| 4 | Lock-in + penalty | Lock-in period with deposit-recovery penalty |
| 5 | Repair burden | Maintenance shifted beyond statutory allocation |
| 6 | Broad deductions | Fixture deductions without proof/standards |
| 7 | Missing registration | No Rent Authority registration evidence |
| 8 | Landlord entry | Entry without written 24-hour notice |
| 9 | Utility charges | Open-ended or unspecified pass-through charges |
| 10 | Association rules | Vague external rules as termination triggers |
| 11 | Essential services | Service cut-off or threat (water, electricity, parking) |

## Quick start (CLI)

```bash
git clone https://github.com/RahulPothapragada/landlorded.git
cd landlorded
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# macOS: weasyprint needs pango
brew install pango

# Run it
python landlorded.py audit agreement.pdf
python landlorded.py dispute agreement.pdf "Tenant Name" "Landlord Name" "Premises Address"
python landlorded.py renewal agreement.pdf
```

### Three modes

- **Audit** — Analyze clauses. CLI output only.
- **Dispute** — Audit + generate report PDF, legal notice, evidence checklist, WhatsApp message.
- **Renewal** — Check escalation clauses (floor with no ceiling) and supersession risks.

## Web app

Landlorded also has a full-stack web interface.

### Stack

| Layer | Choice |
|-------|--------|
| Frontend | Next.js + React (Vercel) |
| Backend | FastAPI wrapping existing Python pipeline (Render, Docker) |
| Auth / DB / Storage | Supabase (PostgreSQL + RLS + Storage) |

### Running locally

**Backend:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Supabase keys
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local   # fill in Supabase keys + API URL
npm run dev
```

**Supabase setup:**
1. Create a project at [supabase.com](https://supabase.com)
2. Run `supabase/migrations/001_initial.sql` in the SQL Editor
3. Create a private storage bucket called `landlorded`
4. Copy your Project URL, anon key, and service role key into the env files

### API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/audits` | Upload PDF, start analysis (202) |
| `GET` | `/audits` | List user's past audits |
| `GET` | `/audits/{id}` | Get full results (or 202 if processing) |
| `DELETE` | `/audits/{id}` | Delete audit + files |
| `GET` | `/audits/{id}/documents/{type}` | Signed download URL |
| `GET` | `/users/me` | Get profile |
| `PATCH` | `/users/me` | Update saved details |

### Architecture

```
agreement.pdf
      │
  extractor.py      PDF ingestion, OCR fallback, lease/schedule split
      │
  detector.py       11 regex-based pattern detectors
      │
  reasoner.py       Legal reasoning over verbatim corpus
      │              (verdict, statute citation, rewrite, notice paragraph)
      │
  generator.py      PDF generation (report + legal notice)
  whatsapp.py       Bilingual Tamil + English message
      │
  output/
    report.pdf
    legal_notice.pdf
    evidence_checklist.md
    whatsapp_message.txt
```

## Legal corpus

Reasoning is grounded in verbatim statute text, not summaries:

| File | Source |
|------|--------|
| `tn_act_2017.md` | TN Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 |
| `tn_act_2017_rules.md` | TN Tenancy Rules, 2019 |
| `tn_rent_authority.md` | Rent Authority jurisdiction and procedure |
| `cpa_2019.md` | Consumer Protection Act, 2019 |
| `tpa_sections.md` | Transfer of Property Act, 1882 (Sections 105, 108, 116) |
| `indian_stamp_act.md` | Indian Stamp Act, 1899 — Article 35 (Lease) as applied in TN |

## Scope

- **Geography:** Tamil Nadu only, Chennai focus
- **Property type:** Residential only
- **Dispute types:** Deposit issues, illegal rent hikes, unfair renewal terms, unjustified fees

## Disclaimer

This tool generates drafts based on automated pattern matching against statute text. It does not constitute legal advice. Review all output and consider obtaining independent legal advice before taking action.

## License

MIT
