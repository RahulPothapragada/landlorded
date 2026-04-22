#!/usr/bin/env python3
"""Landlorded — AI-powered rental agreement auditor for Tamil Nadu tenants."""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from extractor import extract_agreement
from detector import detect_all, Severity
from corpus_loader import load_corpus
from reasoner import reason, LegalAnalysis


console = Console()


SEVERITY_STYLES = {
    Severity.INFO: ("green", "INFO"),
    Severity.YELLOW: ("yellow", "YELLOW FLAG"),
    Severity.RED: ("red bold", "RED FLAG"),
}


def print_banner():
    console.print()
    console.print(Panel.fit(
        "[bold]Landlorded[/bold]\n"
        "[dim]Getting landlorded? Get un-landlorded.[/dim]\n"
        "[dim]Tamil Nadu Residential Tenancy Agreement Auditor[/dim]",
        border_style="blue",
    ))
    console.print()


def print_extraction_summary(agreement):
    console.print(f"[bold]File:[/bold] {agreement.file_path}")
    ocr_note = " [yellow](OCR — scanned PDF)[/yellow]" if agreement.ocr_used else ""
    console.print(f"[bold]Pages:[/bold] {agreement.page_count} total "
                  f"({len(agreement.lease_text):,} chars lease text"
                  f"{f', {len(agreement.schedule_text):,} chars schedule' if agreement.schedule_text else ''})"
                  f"{ocr_note}")
    console.print()


def print_results(analyses: list[LegalAnalysis]):
    # Summary table
    table = Table(title="Clause Audit Summary", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Pattern", min_width=30)
    table.add_column("Status", width=14)
    table.add_column("Severity", width=14)

    fired_count = 0
    red_count = 0
    yellow_count = 0

    for a in analyses:
        if a.fired:
            fired_count += 1
            style, label = SEVERITY_STYLES.get(a.severity, ("white", "UNKNOWN"))
            if a.severity == Severity.RED:
                red_count += 1
            elif a.severity == Severity.YELLOW:
                yellow_count += 1
            table.add_row(str(a.pattern_id), a.pattern_name, "[green]DETECTED[/green]",
                          f"[{style}]{label}[/{style}]")
        else:
            table.add_row(str(a.pattern_id), a.pattern_name, "[dim]not found[/dim]", "[dim]—[/dim]")

    console.print(table)
    console.print()

    # Overall risk
    if red_count > 0:
        console.print(Panel(
            f"[red bold]{red_count} RED FLAG(s)[/red bold], "
            f"[yellow]{yellow_count} YELLOW FLAG(s)[/yellow] — "
            f"{fired_count} of {len(analyses)} patterns detected.",
            title="Overall Risk", border_style="red",
        ))
    elif yellow_count > 0:
        console.print(Panel(
            f"[yellow]{yellow_count} YELLOW FLAG(s)[/yellow] — "
            f"{fired_count} of {len(analyses)} patterns detected.",
            title="Overall Risk", border_style="yellow",
        ))
    else:
        console.print(Panel(
            f"{fired_count} of {len(analyses)} patterns detected. No flags raised.",
            title="Overall Risk", border_style="green",
        ))
    console.print()

    # Detailed findings
    console.print("[bold underline]Detailed Findings[/bold underline]")
    console.print()

    for a in analyses:
        if not a.fired:
            continue

        style, label = SEVERITY_STYLES.get(a.severity, ("white", "UNKNOWN"))
        console.print(f"[bold]Pattern {a.pattern_id}: {a.pattern_name}[/bold] [{style}][{label}][/{style}]")
        console.print()

        # Verdict (from reasoner)
        if a.verdict:
            console.print(Panel(a.verdict, title="What this means", border_style="blue", padding=(0, 2)))
            console.print()

        # Key extracted values
        if a.extracted:
            important_keys = _get_important_keys(a.pattern_id)
            shown = False
            for key, val in a.extracted.items():
                if val is not None and val != [] and val != "" and key in important_keys:
                    display_val = _format_val(val)
                    console.print(f"  [dim]{key}:[/dim] {display_val}")
                    shown = True
            if shown:
                console.print()

        # Matched clause text
        if a.matched_text:
            console.print("  [dim]From your agreement:[/dim]")
            for match in a.matched_text[:2]:
                truncated = match[:250] + "..." if len(match) > 250 else match
                console.print(f"  [italic]\"{truncated}\"[/italic]")
            console.print()

        # Statute citation (from reasoner)
        if a.statute_citation:
            console.print(f"  [bold]Statute citation:[/bold]")
            console.print(f"  {a.statute_citation}")
            console.print()

        # Verbatim statute text (from corpus)
        if a.verbatim_statutes:
            for ref, text in list(a.verbatim_statutes.items())[:2]:
                # Show first 300 chars of verbatim text
                preview = text[:300] + "..." if len(text) > 300 else text
                console.print(f"  [dim]{ref} (verbatim):[/dim]")
                console.print(f"  {preview}")
            console.print()

        # Suggested rewrite
        if a.suggested_rewrite:
            console.print(f"  [bold green]Suggested clause rewrite:[/bold green]")
            console.print(f"  \"{a.suggested_rewrite}\"")
            console.print()

        # Legal notice paragraph
        if a.notice_paragraph:
            console.print(f"  [bold]For your legal notice:[/bold]")
            console.print(f"  \"{a.notice_paragraph}\"")

        console.print()
        console.print("  " + "─" * 60)
        console.print()


def _get_important_keys(pattern_id: int) -> set:
    """Return the most important extracted keys to display for each pattern."""
    return {
        1: {"deposit_amount", "monthly_rent", "deposit_ratio"},
        2: {"handover_linked_refund", "itemization_required", "proof_required_for_deductions"},
        3: {"advance_amount", "adjustable_against_deposit", "refundable", "forfeitable"},
        4: {"lockin_months", "has_penalty", "penalty_from_deposit"},
        5: {"has_appliance_maintenance", "repair_items_detected"},
        6: {"itemization_required", "proof_required", "wear_tear_exception", "inventory_schedule"},
        7: {"registration_evidenced"},
        8: {"written_notice_required", "24_hour_notice"},
        9: {"charges_detected", "open_ended_charges"},
        10: {"occupancy_cap", "subletting_banned", "external_rules_incorporated"},
        11: {},
    }.get(pattern_id, set())


def _format_val(val) -> str:
    if isinstance(val, bool):
        return "Yes" if val else "No"
    elif isinstance(val, int):
        return f"Rs. {val:,}" if val > 1000 else str(val)
    elif isinstance(val, float):
        return str(val)
    elif isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)


def _run_analysis(pdf_path: str):
    """Common analysis pipeline — returns (agreement, analyses)."""
    path = Path(pdf_path)
    if not path.exists():
        console.print(f"[red]Error: File not found: {pdf_path}[/red]")
        sys.exit(1)
    if path.suffix.lower() != ".pdf":
        console.print(f"[red]Error: Expected a PDF file, got: {path.suffix}[/red]")
        sys.exit(1)

    print_banner()

    with console.status("[bold blue]Reading PDF..."):
        agreement = extract_agreement(str(path))
    print_extraction_summary(agreement)

    with console.status("[bold blue]Loading legal corpus..."):
        corpus = load_corpus()
    console.print(f"[bold]Corpus:[/bold] {len(corpus.sections)} statute sections loaded from {len(corpus.raw_files)} files")
    console.print()

    with console.status("[bold blue]Running clause detection (11 patterns)..."):
        results = detect_all(agreement.lease_text, agreement.schedule_text)

    with console.status("[bold blue]Applying legal reasoning..."):
        analyses = reason(results, corpus)

    return agreement, analyses


def cmd_audit(pdf_path: str):
    """Run audit mode on a lease agreement PDF."""
    agreement, analyses = _run_analysis(pdf_path)
    print_results(analyses)


def cmd_dispute(pdf_path: str, tenant_name: str = "[TENANT NAME]",
                landlord_name: str = "[LANDLORD NAME]",
                premises: str = "[PREMISES ADDRESS]"):
    """Run dispute mode — audit + generate all documents including WhatsApp message."""
    from generator import generate_all
    from whatsapp import generate_whatsapp

    agreement, analyses = _run_analysis(pdf_path)
    print_results(analyses)

    console.print()
    console.print("[bold underline]Generating Documents[/bold underline]")
    console.print()

    with console.status("[bold blue]Generating PDFs and documents..."):
        outputs = generate_all(analyses, pdf_path,
                               tenant_name=tenant_name,
                               landlord_name=landlord_name,
                               premises=premises)
        whatsapp_msg = generate_whatsapp(analyses,
                                         tenant_name=tenant_name,
                                         landlord_name=landlord_name)
        outputs["whatsapp_message"] = Path("output/whatsapp_message.txt")

    for doc_type, path in outputs.items():
        console.print(f"  [green]Generated:[/green] {doc_type} -> {path}")

    # Show WhatsApp message preview
    console.print()
    console.print("[bold underline]WhatsApp Message Preview[/bold underline]")
    console.print()
    preview_lines = whatsapp_msg.split("\n")[:15]
    for line in preview_lines:
        console.print(f"  {line}")
    if len(whatsapp_msg.split("\n")) > 15:
        console.print(f"  [dim]... ({len(whatsapp_msg.split(chr(10)))} lines total — see output/whatsapp_message.txt)[/dim]")

    console.print()
    console.print(Panel(
        "[bold]Next steps:[/bold]\n"
        "1. Review report.pdf for accuracy\n"
        "2. Fill in bracketed placeholders in legal_notice.pdf\n"
        "3. Send WhatsApp message as a first warning (whatsapp_message.txt)\n"
        "4. Gather evidence listed in evidence_checklist.md\n"
        "5. Send legal notice by Registered Post A/D\n"
        "6. If no response in 15 days, file consumer complaint",
        title="What to do now", border_style="green",
    ))


def cmd_renewal(pdf_path: str):
    """Run renewal mode — focus on escalation clause and renewal terms."""
    agreement, analyses = _run_analysis(pdf_path)

    # Filter to renewal-relevant patterns
    renewal_patterns = {1, 2, 4, 7, 9}  # deposit, refund, lock-in, registration, charges
    renewal_analyses = [a for a in analyses if a.pattern_id in renewal_patterns]

    print_results(analyses)

    # Check for escalation clause
    console.print()
    console.print("[bold underline]Renewal-Specific Analysis[/bold underline]")
    console.print()

    import re
    from detector import _normalize
    text = _normalize(agreement.lease_text)
    lower = text.lower()

    # Escalation detection
    escalation_terms = ["not less than", "escalation", "rent hike", "increase",
                        "revised terms", "rental rate escalation", "5%", "5 %",
                        "ten percent", "10%"]
    escalation_found = []
    for term in escalation_terms:
        if term in lower:
            idx = lower.index(term)
            start = max(0, idx - 100)
            end = min(len(text), idx + len(term) + 150)
            snippet = text[start:end].strip()
            if snippet not in escalation_found:
                escalation_found.append(snippet)

    if escalation_found:
        console.print("[yellow bold]Escalation clause detected:[/yellow bold]")
        console.print()
        for snippet in escalation_found[:2]:
            truncated = snippet[:300] + "..." if len(snippet) > 300 else snippet
            console.print(f"  [italic]\"{truncated}\"[/italic]")
        console.print()

        # Check for cap
        has_cap = any(t in lower for t in ["not exceeding", "maximum", "upper limit", "cap of", "up to"])
        has_no_cap = any(t in lower for t in ["not less than", "at least", "minimum"])

        if has_no_cap and not has_cap:
            console.print(Panel(
                "[red bold]No upper cap on escalation.[/red bold] The clause sets a floor "
                "(e.g., 'not less than 5%') but no ceiling. This means the landlord can "
                "demand any increase above the floor. Negotiate for a fixed rate or a cap.",
                title="Escalation Risk", border_style="red",
            ))
        elif has_cap:
            console.print(Panel(
                "[green]Escalation has a cap.[/green] Review whether the cap is reasonable "
                "relative to current market rates.",
                title="Escalation Assessment", border_style="green",
            ))
    else:
        console.print("[dim]No explicit escalation clause found in the agreement.[/dim]")

    console.print()

    # Renewal checklist
    console.print(Panel(
        "[bold]Before signing a renewal:[/bold]\n"
        "1. Check for 'supersession' or 'entire agreement' clauses — strike them\n"
        "2. Add handwritten note preserving original deposit claim with refund timeline\n"
        "3. Negotiate escalation cap (e.g., 'not exceeding 5%' instead of 'not less than 5%')\n"
        "4. Insist on Rent Authority registration of the new deed\n"
        "5. Export all WhatsApp chats with landlord and broker before signing\n"
        "6. Do NOT pay brokerage without GST invoice",
        title="Renewal Checklist", border_style="blue",
    ))


def main():
    if len(sys.argv) < 2:
        _print_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command in ("help", "--help", "-h"):
        _print_help()
        sys.exit(0)

    if len(sys.argv) < 3:
        _print_help()
        sys.exit(1)

    target = sys.argv[2]

    if command == "audit":
        cmd_audit(target)
    elif command == "dispute":
        tenant = sys.argv[3] if len(sys.argv) > 3 else "[TENANT NAME]"
        landlord = sys.argv[4] if len(sys.argv) > 4 else "[LANDLORD NAME]"
        premises = sys.argv[5] if len(sys.argv) > 5 else "[PREMISES ADDRESS]"
        cmd_dispute(target, tenant, landlord, premises)
    elif command == "renewal":
        cmd_renewal(target)
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print()
        _print_help()
        sys.exit(1)


def _print_help():
    print_banner()
    console.print("[bold]Usage:[/bold]")
    console.print()
    console.print("  [green]python landlorded.py audit[/green] <agreement.pdf>")
    console.print("    Analyze agreement for unfair/illegal clauses. CLI output only.")
    console.print()
    console.print("  [green]python landlorded.py dispute[/green] <agreement.pdf> [tenant] [landlord] [premises]")
    console.print("    Full pipeline: audit + generate report PDF, legal notice,")
    console.print("    evidence checklist, and bilingual WhatsApp message.")
    console.print()
    console.print("  [green]python landlorded.py renewal[/green] <agreement.pdf>")
    console.print("    Check renewal terms, escalation clauses, and supersession risks.")
    console.print()
    console.print("[bold]Examples:[/bold]")
    console.print()
    console.print('  python landlorded.py audit agreement.pdf')
    console.print('  python landlorded.py dispute agreement.pdf "Rahul" "Mrs. Vasanth" "Apt 1136, Estancia"')
    console.print('  python landlorded.py renewal new_lease.pdf')
    console.print()
    console.print("[bold]Output files[/bold] (dispute mode) are saved to [green]output/[/green]:")
    console.print("  report.pdf             — Clause-by-clause audit with statute citations")
    console.print("  legal_notice.pdf       — Formal legal notice with your details")
    console.print("  evidence_checklist.md  — What to gather before filing")
    console.print("  whatsapp_message.txt   — Bilingual Tamil + English warning message")


if __name__ == "__main__":
    main()
