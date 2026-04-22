"""Document generation — produces legal notice and consumer complaint PDFs.

Takes LegalAnalysis results and generates:
1. report.pdf — clause-by-clause audit report
2. legal_notice.pdf — formal legal notice with actual clause citations
3. evidence_checklist.md — what to gather before filing
"""

from pathlib import Path
from datetime import date
from reasoner import LegalAnalysis
from detector import Severity
import weasyprint


OUTPUT_DIR = Path(__file__).parent / "output"


# --- CSS for PDF styling ---

REPORT_CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm;
    @bottom-center { content: "Page " counter(page) " of " counter(pages); font-size: 9pt; color: #888; }
    @bottom-right { content: "Landlorded — Confidential"; font-size: 8pt; color: #aaa; }
}
body { font-family: 'Georgia', 'Times New Roman', serif; font-size: 11pt; line-height: 1.6; color: #222; }
h1 { font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 14pt; color: #333; margin-top: 24px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
h3 { font-size: 12pt; color: #444; margin-top: 16px; }
.severity-red { color: #c0392b; font-weight: bold; }
.severity-yellow { color: #d4a017; font-weight: bold; }
.severity-info { color: #27ae60; font-weight: bold; }
.verdict-box { background: #f8f9fa; border-left: 4px solid #3498db; padding: 10px 14px; margin: 10px 0; }
.clause-quote { background: #fff9e6; border-left: 3px solid #f0c040; padding: 8px 12px; margin: 8px 0; font-style: italic; font-size: 10pt; }
.statute-text { background: #f0f4f8; border-left: 3px solid #666; padding: 8px 12px; margin: 8px 0; font-size: 10pt; }
.rewrite-box { background: #e8f8e8; border-left: 3px solid #27ae60; padding: 8px 12px; margin: 8px 0; }
.notice-box { background: #f0e8f8; border-left: 3px solid #8e44ad; padding: 8px 12px; margin: 8px 0; }
.meta { color: #666; font-size: 10pt; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 10pt; }
th { background: #f0f0f0; font-weight: bold; }
.summary-table td:nth-child(3) { text-align: center; }
.summary-table td:nth-child(4) { text-align: center; }
"""

NOTICE_CSS = """
@page {
    size: A4;
    margin: 2.5cm 2.5cm;
    @bottom-center { content: "Page " counter(page); font-size: 9pt; color: #888; }
}
body { font-family: 'Georgia', 'Times New Roman', serif; font-size: 11pt; line-height: 1.8; color: #000; }
h1 { font-size: 16pt; text-align: center; text-decoration: underline; margin-bottom: 20px; }
h2 { font-size: 13pt; margin-top: 20px; }
.header { text-align: right; margin-bottom: 30px; font-size: 10pt; }
.addressee { margin: 20px 0; }
.subject { font-weight: bold; margin: 16px 0; }
.para { text-indent: 40px; margin: 8px 0; text-align: justify; }
.demand { margin-top: 16px; }
.signature { margin-top: 40px; }
"""


def generate_all(analyses: list[LegalAnalysis], agreement_path: str,
                 tenant_name: str = "[TENANT NAME]",
                 landlord_name: str = "[LANDLORD NAME]",
                 premises: str = "[PREMISES ADDRESS]") -> dict[str, Path]:
    """Generate all output documents. Returns dict of output file paths."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    outputs = {}
    outputs["report"] = _generate_report(analyses, agreement_path)
    outputs["legal_notice"] = _generate_legal_notice(analyses, tenant_name, landlord_name, premises)
    outputs["evidence_checklist"] = _generate_checklist(analyses)

    return outputs


# --- Report PDF ---

def _severity_class(sev: Severity | None) -> str:
    if sev == Severity.RED: return "severity-red"
    if sev == Severity.YELLOW: return "severity-yellow"
    return "severity-info"


def _severity_label(sev: Severity | None) -> str:
    if sev == Severity.RED: return "RED FLAG"
    if sev == Severity.YELLOW: return "YELLOW FLAG"
    return "INFO"


def _generate_report(analyses: list[LegalAnalysis], agreement_path: str) -> Path:
    """Generate the clause-by-clause audit report PDF."""
    fired = [a for a in analyses if a.fired]
    red_count = sum(1 for a in fired if a.severity == Severity.RED)
    yellow_count = sum(1 for a in fired if a.severity == Severity.YELLOW)

    # Build summary table
    summary_rows = ""
    for a in analyses:
        if a.fired:
            sev_class = _severity_class(a.severity)
            sev_label = _severity_label(a.severity)
            summary_rows += f'<tr><td>{a.pattern_id}</td><td>{a.pattern_name}</td><td>Detected</td><td class="{sev_class}">{sev_label}</td></tr>\n'
        else:
            summary_rows += f'<tr><td>{a.pattern_id}</td><td>{a.pattern_name}</td><td style="color:#999">Not found</td><td>—</td></tr>\n'

    # Build detailed findings
    findings_html = ""
    para_num = 1
    for a in fired:
        sev_class = _severity_class(a.severity)
        sev_label = _severity_label(a.severity)

        # Extracted values
        extracted_html = ""
        if a.extracted:
            for key, val in a.extracted.items():
                if val is not None and val != [] and val != "":
                    display = _format_display(val)
                    extracted_html += f"<li><strong>{key}:</strong> {display}</li>\n"

        # Matched text
        quotes_html = ""
        for text in a.matched_text[:2]:
            truncated = text[:300] + "..." if len(text) > 300 else text
            quotes_html += f'<div class="clause-quote">&ldquo;{_escape(truncated)}&rdquo;</div>\n'

        # Verbatim statute
        statute_html = ""
        for ref, text in list(a.verbatim_statutes.items())[:2]:
            preview = text[:400] + "..." if len(text) > 400 else text
            statute_html += f'<div class="statute-text"><strong>{ref}:</strong><br>{_escape(preview)}</div>\n'

        findings_html += f"""
        <h2>{para_num}. Pattern {a.pattern_id}: {a.pattern_name}
            <span class="{sev_class}">[{sev_label}]</span></h2>

        <div class="verdict-box">{_escape(a.verdict)}</div>

        {"<h3>Key findings</h3><ul>" + extracted_html + "</ul>" if extracted_html else ""}

        {"<h3>From the agreement</h3>" + quotes_html if quotes_html else ""}

        {"<h3>Applicable law</h3><p>" + _escape(a.statute_citation) + "</p>" + statute_html if a.statute_citation else ""}

        {"<h3>Suggested clause rewrite</h3><div class='rewrite-box'>&ldquo;" + _escape(a.suggested_rewrite) + "&rdquo;</div>" if a.suggested_rewrite else ""}

        {"<h3>For legal notice</h3><div class='notice-box'>&ldquo;" + _escape(a.notice_paragraph) + "&rdquo;</div>" if a.notice_paragraph else ""}

        <hr>
        """
        para_num += 1

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body>

<h1>Landlorded — Agreement Audit Report</h1>

<p class="meta">
    <strong>File analysed:</strong> {_escape(agreement_path)}<br>
    <strong>Date:</strong> {date.today().strftime('%d %B %Y')}<br>
    <strong>Patterns checked:</strong> {len(analyses)}<br>
    <strong>Patterns detected:</strong> {len(fired)}
    ({red_count} Red Flag{'s' if red_count != 1 else ''}, {yellow_count} Yellow Flag{'s' if yellow_count != 1 else ''})
</p>

<h2>Summary</h2>
<table class="summary-table">
    <tr><th>#</th><th>Pattern</th><th>Status</th><th>Severity</th></tr>
    {summary_rows}
</table>

<h2>Overall Assessment</h2>
<div class="verdict-box">
    {"<span class='severity-red'>HIGH RISK</span> — " + str(red_count) + " red flag(s) and " + str(yellow_count) + " yellow flag(s) detected. This agreement contains clauses that significantly disadvantage the tenant." if red_count > 0 else "<span class='severity-yellow'>MODERATE RISK</span> — " + str(yellow_count) + " yellow flag(s) detected. Several clauses warrant attention." if yellow_count > 0 else "<span class='severity-info'>LOW RISK</span> — No significant flags raised."}
</div>

<p class="meta"><strong>Disclaimer:</strong> This is an automated analysis tool. It does not constitute legal advice.
The user should review all findings and consider obtaining independent legal advice before taking action.</p>

<hr>

<h1>Detailed Findings</h1>

{findings_html}

<p class="meta" style="margin-top: 40px; text-align: center;">
    Generated by Landlorded — Getting landlorded? Get un-landlorded.<br>
    {date.today().strftime('%d %B %Y')}
</p>

</body></html>"""

    out_path = OUTPUT_DIR / "report.pdf"
    weasyprint.HTML(string=html).write_pdf(str(out_path), stylesheets=[weasyprint.CSS(string=REPORT_CSS)])
    return out_path


# --- Legal Notice PDF ---

def _generate_legal_notice(analyses: list[LegalAnalysis],
                           tenant_name: str, landlord_name: str,
                           premises: str) -> Path:
    """Generate the legal notice PDF from pattern results."""
    fired = [a for a in analyses if a.fired]

    # Build clause-specific paragraphs
    clause_paras = ""
    para_num = 6
    for a in fired:
        if a.notice_paragraph:
            clause_paras += f'<p class="para">{para_num}. {_escape(a.notice_paragraph)}</p>\n'
            para_num += 1

    # Collect all statute references
    all_statutes = set()
    for a in fired:
        if a.statute_citation:
            all_statutes.add(a.statute_citation)

    # Deposit amount for demand
    deposit_amount = "[DEPOSIT AMOUNT]"
    for a in analyses:
        dep = a.extracted.get("deposit_amount")
        if dep and isinstance(dep, int):
            deposit_amount = _fmt_inr(dep)
            break

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body>

<div class="header">
    <strong>Date:</strong> {date.today().strftime('%d %B %Y')}<br>
    <strong>Ref. No.:</strong> LN/{date.today().strftime('%Y%m%d')}/01
</div>

<p><strong>By Registered Post A/D / Speed Post / Email</strong></p>

<h1>LEGAL NOTICE</h1>

<div class="addressee">
<p><strong>To,</strong></p>
<p>1. <strong>{_escape(landlord_name)}</strong>,<br>
   [Landlord address]</p>
</div>

<p class="subject">Subject: Legal notice demanding refund of security deposit of {deposit_amount}
and addressing unlawful lease terms under the Tamil Nadu Regulation of Rights and
Responsibilities of Landlords and Tenants Act, 2017</p>

<p>Sir / Madam,</p>

<p class="para">1. Under instructions from and on behalf of my client <strong>{_escape(tenant_name)}</strong>,
residing at [tenant address], I hereby issue the present legal notice as follows:</p>

<p class="para">2. That my client entered into a Lease Deed with you in respect of
<strong>{_escape(premises)}</strong> (hereinafter &ldquo;the premises&rdquo;).</p>

<p class="para">3. That at the commencement of the tenancy, my client paid to you a sum of
<strong>{deposit_amount}</strong> towards interest-free refundable security deposit,
acknowledged in the Lease Deed.</p>

<p class="para">4. That during the entire period of the tenancy, my client regularly paid the
monthly lease rent without default.</p>

<p class="para">5. That upon review of the Lease Deed, the following issues have been identified:</p>

<h2>Clause-Specific Issues</h2>

{clause_paras}

<h2>Unfair Trade Practice</h2>

<p class="para">{para_num}. That the conduct described above, individually and collectively, amounts to
<strong>unfair trade practice</strong> within the meaning of <strong>Section 2(47) of the
Consumer Protection Act, 2019</strong>. The withholding of the security deposit without lawful basis,
the imposition of one-sided lease terms, and the failure to provide transparent refund mechanisms
constitute deceptive and unfair practices in the provision of a service (housing/accommodation)
to a consumer as defined under <strong>Section 2(7)</strong> of the said Act.</p>

<h2>Demand</h2>

<p class="para">{para_num + 1}. In the circumstances set out above, I hereby call upon you to:</p>

<p class="para" style="text-indent: 60px;">(a) Refund to my client the sum of <strong>{deposit_amount}</strong>,
less only such amount, if any, as may be lawfully adjusted and specifically supported by itemized
proof of actual damage beyond normal wear and tear or documented arrears of rent;</p>

<p class="para" style="text-indent: 60px;">(b) In case you claim any deduction whatsoever, furnish within the same period
a full and document-supported statement of such deductions, along with copies of invoices, bills,
repair estimates, proof of payment, photographs, and inspection records;</p>

<p class="para">within <strong>15 (fifteen) days</strong> from the date of receipt of this legal notice.</p>

<h2>Consequence of Non-Compliance</h2>

<p class="para">{para_num + 2}. Take notice that if you fail to comply with the above demand within the
stipulated period, my client shall be constrained to initiate appropriate legal proceedings
against you, including filing a consumer complaint before the District Consumer Disputes
Redressal Commission under Section 35 of the Consumer Protection Act, 2019, seeking refund,
compensation, punitive damages, costs, and all reliefs available under Section 39 of the said Act,
entirely at your risk as to costs and consequences.</p>

<p class="para">This notice is issued without prejudice to all other rights and remedies available
to my client in law and equity.</p>

<p class="para">A copy of this notice is retained for record and future action.</p>

<div class="signature">
<p><strong>Yours faithfully,</strong></p>
<br><br>
<p>________________________<br>
<strong>[Advocate Name / Sender]</strong></p>
</div>

</body></html>"""

    out_path = OUTPUT_DIR / "legal_notice.pdf"
    weasyprint.HTML(string=html).write_pdf(str(out_path), stylesheets=[weasyprint.CSS(string=NOTICE_CSS)])
    return out_path


# --- Evidence Checklist ---

def _generate_checklist(analyses: list[LegalAnalysis]) -> Path:
    """Generate evidence checklist as markdown."""
    fired = [a for a in analyses if a.fired]

    lines = [
        "# Evidence Checklist — Landlorded",
        "",
        f"Generated: {date.today().strftime('%d %B %Y')}",
        "",
        "Gather the following before sending the legal notice or filing a consumer complaint.",
        "",
        "## Essential Documents",
        "",
        "- [ ] Original Lease Deed (signed copy)",
        "- [ ] Proof of security deposit payment (bank transfer receipt / statement)",
        "- [ ] Rent payment proof for all months (bank statements showing transfers)",
        "- [ ] Aadhaar / ID proof of tenant",
        "",
    ]

    for a in fired:
        if a.pattern_id == 1:
            lines += [
                "## Pattern 1: Deposit Evidence",
                "- [ ] Bank statement showing deposit transfer",
                "- [ ] Any receipt or acknowledgment from landlord",
                "- [ ] Market survey of comparable deposit ratios in the area (optional)",
                "",
            ]
        elif a.pattern_id == 3:
            lines += [
                "## Pattern 3: Advance Payment Evidence",
                "- [ ] Bank statement showing advance transfer",
                "- [ ] Any communication confirming the advance and its purpose",
                "- [ ] Check if advance was later adjusted — payment trail",
                "",
            ]
        elif a.pattern_id == 4:
            lines += [
                "## Pattern 4: Lock-in / Penalty Evidence",
                "- [ ] Communication about early exit or notice period",
                "- [ ] Any deduction statement from landlord citing lock-in penalty",
                "",
            ]
        elif a.pattern_id == 6:
            lines += [
                "## Pattern 6: Fixture / Deduction Evidence",
                "- [ ] Move-in photos of premises and fixtures",
                "- [ ] Move-out photos of premises and fixtures",
                "- [ ] Schedule I from the lease deed (fixture list)",
                "- [ ] Any inspection report or damage claim from landlord",
                "",
            ]
        elif a.pattern_id == 7:
            lines += [
                "## Pattern 7: Registration Evidence",
                "- [ ] Check tenancy.tn.gov.in for registration status",
                "- [ ] Screenshot if registration not found on portal",
                "",
            ]
        elif a.pattern_id == 11:
            lines += [
                "## Pattern 11: Essential Services Evidence",
                "- [ ] Photos/videos of service disruption",
                "- [ ] WhatsApp messages about service cut-off",
                "- [ ] Association notices, if any",
                "- [ ] Dates and duration of disruption",
                "",
            ]

    lines += [
        "## Communication Records",
        "",
        "- [ ] Export WhatsApp chats with landlord (text + media)",
        "- [ ] Export WhatsApp chats with broker (text + media)",
        "- [ ] Emails to/from landlord about deposit, renewal, or disputes",
        "- [ ] Any written notice sent to landlord (copy + postal receipt)",
        "",
        "## For Consumer Complaint Filing",
        "",
        "- [ ] Copy of legal notice sent + AD card / tracking receipt",
        "- [ ] Reply from landlord to legal notice (if any)",
        "- [ ] Affidavit (required for filing)",
        "- [ ] Court fee (based on claim amount — check current District Commission schedule)",
        "- [ ] Vakalatnama if engaging an advocate",
        "",
        "---",
        "",
        "*Generated by Landlorded*",
    ]

    out_path = OUTPUT_DIR / "evidence_checklist.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


# --- Utilities ---

def _escape(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _format_display(val) -> str:
    if isinstance(val, bool):
        return "Yes" if val else "No"
    elif isinstance(val, int):
        return _fmt_inr(val) if val > 1000 else str(val)
    elif isinstance(val, float):
        return str(val)
    elif isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)


def _fmt_inr(amount: int) -> str:
    """Format amount in Indian numbering: ₹4,50,000."""
    s = str(amount)
    if len(s) <= 3:
        return f"₹{s}"
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while rest:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    return f"₹{','.join(groups)},{last3}"
