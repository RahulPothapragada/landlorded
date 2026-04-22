"""Legal reasoning layer — enriches pattern results with statute-grounded analysis.

Takes raw PatternResults from detector.py, loads the corpus, and produces
structured legal output: verdict, statute citation, suggested rewrite, and
legal notice paragraph for each fired pattern.
"""

from dataclasses import dataclass, field
from .corpus_loader import Corpus, load_corpus
from .detector import PatternResult, Severity


@dataclass
class LegalAnalysis:
    """Enriched legal analysis for a single pattern."""
    pattern_id: int
    pattern_name: str
    severity: Severity | None
    fired: bool

    # From detector
    explanation: str = ""
    extracted: dict = field(default_factory=dict)
    matched_text: list[str] = field(default_factory=list)

    # From reasoner (new)
    verdict: str = ""
    statute_citation: str = ""
    suggested_rewrite: str = ""
    notice_paragraph: str = ""
    verbatim_statutes: dict[str, str] = field(default_factory=dict)


def reason(results: list[PatternResult], corpus: Corpus | None = None) -> list[LegalAnalysis]:
    """Enrich pattern results with legal reasoning from the corpus."""
    if corpus is None:
        corpus = load_corpus()

    analyses = []
    for r in results:
        if not r.fired:
            analyses.append(LegalAnalysis(
                pattern_id=r.pattern_id,
                pattern_name=r.pattern_name,
                severity=r.severity,
                fired=False,
            ))
            continue

        analysis = LegalAnalysis(
            pattern_id=r.pattern_id,
            pattern_name=r.pattern_name,
            severity=r.severity,
            fired=True,
            explanation=r.explanation,
            extracted=r.extracted,
            matched_text=r.matched_text,
        )

        # Load verbatim statute text for this pattern's references
        for ref in r.statute_refs:
            text = corpus.get_text(ref)
            if text:
                analysis.verbatim_statutes[ref] = text

        # Generate structured legal output
        builder = PATTERN_BUILDERS.get(r.pattern_id)
        if builder:
            builder(analysis, corpus)

        analyses.append(analysis)

    return analyses


# --- Pattern-specific reasoning builders ---

def _fmt_amount(val) -> str:
    """Format an amount as ₹X,XX,XXX (Indian numbering)."""
    if val is None:
        return "₹[amount]"
    # Indian numbering: last 3 digits, then groups of 2
    s = str(val)
    if len(s) <= 3:
        return f"₹{s}"
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while rest:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    return f"₹{','.join(groups)},{last3}"


def _build_p1(a: LegalAnalysis, c: Corpus):
    dep = a.extracted.get("deposit_amount")
    rent = a.extracted.get("monthly_rent")
    ratio = a.extracted.get("deposit_ratio")
    dep_str = _fmt_amount(dep)
    rent_str = _fmt_amount(rent)
    ratio_str = str(ratio) if ratio else "[N]"

    a.verdict = (
        f"Your security deposit is {dep_str}, which is {ratio_str} months of monthly rent "
        f"({rent_str}). Under Section 11(1) of the TN Tenancy Act 2017, the statutory default "
        f"is three months' rent, but the Act allows parties to contract otherwise ('save an "
        f"agreement to the contrary'). This means the deposit is not automatically illegal, but "
        f"the higher amount materially increases refund-risk and supports unfairness / "
        f"unconscionability arguments."
    )

    a.statute_citation = (
        f"Section 11(1) of the Tamil Nadu Regulation of Rights and Responsibilities of "
        f"Landlords and Tenants Act, 2017 establishes three times the monthly rent as the "
        f"statutory norm for security deposits. While the Act permits parties to contract to "
        f"a higher amount, the deposit of {dep_str} (being {ratio_str} months' rent) deviates "
        f"significantly from the statutory norm and prevailing Chennai market practice."
    )

    a.suggested_rewrite = (
        "The Security Deposit shall be an amount equivalent to three (3) months of the monthly "
        "Lease Rent and shall be refundable in full at the time of handover of vacant possession, "
        "subject only to itemized deductions supported by proof for actual damages beyond normal "
        "wear and tear or arrears of rent."
    )

    a.notice_paragraph = (
        f"My client paid a security deposit of {dep_str}, which represents {ratio_str} months "
        f"of monthly rent. While Section 11(1) of the Tamil Nadu Regulation of Rights and "
        f"Responsibilities of Landlords and Tenants Act, 2017 permits parties to contract "
        f"otherwise, the amount is substantially above the statutory norm of three months. "
        f"Under Section 11(2), the deposit is to be refunded at the time of handover of "
        f"vacant possession. Any refusal or delay in refund, or any deduction not supported "
        f"by documented damages, will be disputed."
    )


def _build_p2(a: LegalAnalysis, c: Corpus):
    a.verdict = (
        "The agreement allows deductions from the deposit but does not create a transparent, "
        "itemized refund mechanism. Section 11(2) requires refund at the time of taking over "
        "vacant possession after due deduction of tenant liability."
    )

    a.statute_citation = (
        "Section 11(2) of the Tamil Nadu Regulation of Rights and Responsibilities of "
        "Landlords and Tenants Act, 2017, read with Rule 7(2) of the Tamil Nadu Regulation "
        "of Rights and Responsibilities of Landlords and Tenants Rules, 2019."
    )

    a.suggested_rewrite = (
        "At the time of handover of vacant possession, the Lessor shall refund the Security "
        "Deposit after deducting only documented arrears or actual damage beyond normal wear "
        "and tear, supported by an itemized statement and proof."
    )

    a.notice_paragraph = (
        "The lease does not provide a lawful and transparent refund mechanism. Under "
        "Section 11(2) of the Act, the security deposit is to be refunded at the time of "
        "taking over vacant possession after due deduction of tenant liability. Any delayed "
        "refund or unsupported deduction shall be disputed as unlawful withholding and "
        "unfair trade practice."
    )


def _build_p3(a: LegalAnalysis, c: Corpus):
    adv = a.extracted.get("advance_amount")
    adv_str = _fmt_amount(adv)

    a.verdict = (
        f"The agreement contains a pre-tenancy advance of {adv_str} to confirm the "
        f"arrangement, but its later treatment is not clearly explained. This creates "
        f"ambiguity over whether it is part of the deposit, part of rent, or separately "
        f"forfeitable."
    )

    a.statute_citation = (
        "Section 24(1) of the Tamil Nadu Regulation of Rights and Responsibilities of "
        "Landlords and Tenants Act, 2017."
    )

    a.suggested_rewrite = (
        "Any booking or advance amount paid before commencement shall stand adjusted against "
        "the Security Deposit or first month's rent and shall not be separately forfeited "
        "except for documented breach expressly stated in this Agreement."
    )

    a.notice_paragraph = (
        f"My client paid an advance of {adv_str} before commencement of tenancy. The "
        f"agreement does not clearly state whether this amount is to be adjusted toward "
        f"deposit or rent, nor the circumstances in which any part of it may be retained. "
        f"Such ambiguity must be construed against the drafter."
    )


def _build_p4(a: LegalAnalysis, c: Corpus):
    months = a.extracted.get("lockin_months", "[N]")

    a.verdict = (
        f"The agreement imposes a {months}-month lock-in and allows compensation to be "
        f"recovered from the security deposit if the tenant exits before or without completing "
        f"the notice period. This is a high-risk clause because it combines movement restriction "
        f"with automatic monetary recovery."
    )

    a.statute_citation = (
        "Sections 5, 11(2), 21 and 29(2) of the Tamil Nadu Regulation of Rights and "
        "Responsibilities of Landlords and Tenants Act, 2017."
    )

    a.suggested_rewrite = (
        "Either party may terminate by giving one month's written notice. No lock-in or "
        "penalty shall apply except actual documented loss directly caused by proven breach."
    )

    a.notice_paragraph = (
        f"The clause imposing a {months}-month lock-in and authorizing recovery of "
        f"compensation from the Security Deposit is oppressive and one-sided. Any deduction "
        f"on this basis, without proof of actual loss and without lawful refund at handover, "
        f"will be disputed."
    )


def _build_p5(a: LegalAnalysis, c: Corpus):
    items = a.extracted.get("repair_items_detected", [])
    items_str = ", ".join(items) if items else "various items"

    a.verdict = (
        f"The agreement makes the tenant responsible for day-to-day minor repairs and "
        f"maintenance of appliances ({items_str}). Some of this may align with Section 15 "
        f"and the Second Schedule, but the exact items should be compared against the "
        f"statutory allocation."
    )

    a.statute_citation = (
        "Section 15 of the Tamil Nadu Regulation of Rights and Responsibilities of "
        "Landlords and Tenants Act, 2017, read with the Second Schedule thereto."
    )

    a.suggested_rewrite = (
        "Repair responsibilities shall follow Section 15 and the Second Schedule of "
        "the TN Tenancy Act. Structural repairs and landlord-side obligations shall remain "
        "with the Lessor."
    )

    a.notice_paragraph = (
        "To the extent the lease seeks to shift repair obligations beyond those assignable "
        "to the tenant under Section 15 read with the Second Schedule of the Act, my client "
        "disputes the enforceability of such additional burden."
    )


def _build_p6(a: LegalAnalysis, c: Corpus):
    has_schedule = a.extracted.get("inventory_schedule", False)
    has_proof = a.extracted.get("proof_required", False)
    has_wear = a.extracted.get("wear_tear_exception", False)

    schedule_note = "includes a fixture schedule, which helps, but t" if has_schedule else "T"

    a.verdict = (
        f"The agreement {schedule_note}he deduction language is still broad and does not "
        f"clearly require itemization, proof, or a normal-wear-and-tear standard."
    )

    a.statute_citation = (
        "Section 11(2) and Section 15 of the Tamil Nadu Regulation of Rights and "
        "Responsibilities of Landlords and Tenants Act, 2017."
    )

    a.suggested_rewrite = (
        "Deductions from the Security Deposit shall be limited to itemized, documented "
        "loss for damage beyond normal wear and tear, cross-checked against the signed "
        "inventory."
    )

    a.notice_paragraph = (
        "The lease permits broad deduction of alleged fixture and appliance value from "
        "the deposit without setting out a documented valuation or wear-and-tear standard. "
        "Any such deduction, unless supported by itemized proof, will be disputed."
    )


def _build_p7(a: LegalAnalysis, c: Corpus):
    evidenced = a.extracted.get("registration_evidenced", False)

    if evidenced:
        a.verdict = "Registration evidence found in the agreement."
        a.statute_citation = ""
        a.suggested_rewrite = ""
        a.notice_paragraph = ""
        return

    a.verdict = (
        "The reviewed agreement does not show a Tenancy Registration Number or other "
        "Rent Authority registration evidence. This does not conclusively prove "
        "non-registration, but it creates a compliance and evidentiary risk."
    )

    a.statute_citation = (
        "Sections 4 and 4-A of the Tamil Nadu Regulation of Rights and Responsibilities "
        "of Landlords and Tenants Act, 2017, read with Rule 3 of the Tamil Nadu Regulation "
        "of Rights and Responsibilities of Landlords and Tenants Rules, 2019."
    )

    a.suggested_rewrite = (
        "This Agreement shall be registered with the Rent Authority within the prescribed "
        "period, and the Tenancy Registration Number shall be recorded in the body of this "
        "Agreement."
    )

    a.notice_paragraph = (
        "The written lease relied upon by you does not disclose any Rent Authority "
        "registration particulars. Under Sections 4 and 4-A of the Act, registration "
        "is mandatory and directly affects the evidentiary use of the document."
    )


def _build_p8(a: LegalAnalysis, c: Corpus):
    a.verdict = (
        "The lease allows landlord entry during reasonable daytime hours, but it does not "
        "clearly require written 24-hour notice. Section 17 of the Act is more specific "
        "and should prevail."
    )

    a.statute_citation = (
        "Section 17 of the Tamil Nadu Regulation of Rights and Responsibilities of "
        "Landlords and Tenants Act, 2017."
    )

    a.suggested_rewrite = (
        "The Lessor may enter only upon written notice given at least twenty-four hours "
        "in advance, specifying the purpose, day, and time of entry, and only within the "
        "statutory time window."
    )

    a.notice_paragraph = (
        "Any entry into the premises must comply with Section 17 of the Act, including "
        "prior written notice and specified purpose. Any attempt at informal or surprise "
        "entry will be treated as unlawful interference with possession."
    )


def _build_p9(a: LegalAnalysis, c: Corpus):
    charges = a.extracted.get("charges_detected", [])
    charges_str = ", ".join(charges) if charges else "various charges"

    a.verdict = (
        f"The lease passes several charges to the tenant: {charges_str}. Meter-based "
        f"electricity is easier to justify; open-ended water-shortage or other unspecified "
        f"charges deserve closer scrutiny."
    )

    a.statute_citation = (
        "Sections 13, 20 and 24(1) of the Tamil Nadu Regulation of Rights and "
        "Responsibilities of Landlords and Tenants Act, 2017."
    )

    a.suggested_rewrite = (
        "All tenant-borne charges shall be limited to objectively measurable, documented "
        "charges specifically listed in the Agreement, and copies of supporting bills shall "
        "be shared on demand."
    )

    a.notice_paragraph = (
        "My client disputes any charge not specifically listed and objectively measurable "
        "under the Agreement. Any additional recovery demand unsupported by meter reading, "
        "bill, or contractual basis is denied."
    )


def _build_p10(a: LegalAnalysis, c: Corpus):
    cap = a.extracted.get("occupancy_cap")
    external = a.extracted.get("external_rules_incorporated", False)
    cap_str = f" for {cap} people" if cap else ""

    a.verdict = (
        f"The agreement contains residential-use{cap_str} and no-subletting restrictions"
        + (", and ties termination to breaches of separate association / club rules. "
           "That external-rule incorporation should be reviewed carefully because it "
           "widens eviction risk." if external else ".")
    )

    a.statute_citation = (
        "Sections 7, 21(2)(c), 21(2)(d), and 29 of the Tamil Nadu Regulation of "
        "Rights and Responsibilities of Landlords and Tenants Act, 2017."
    )

    a.suggested_rewrite = (
        "Any external rules incorporated into this Agreement shall be attached as "
        "schedules and shall not operate to create automatic termination unless the "
        "breach is material, documented, and consistent with applicable law."
    )

    a.notice_paragraph = (
        "While my client does not dispute lawful residential-use and no-subletting "
        "restrictions, any attempt to terminate the tenancy on the basis of unspecified "
        "or unattached association rules will be disputed as vague and overbroad."
    )


def _build_p11(a: LegalAnalysis, c: Corpus):
    a.verdict = (
        "This is not just a contract issue. Section 20 of the TN Tenancy Act makes it "
        "unlawful for any landlord — directly or through others — to cut off or withhold "
        "essential services including water, electricity, parking, lifts, and sanitary "
        "services. If services have been interrupted, the Rent Authority can pass an "
        "interim order restoring them immediately, even before completing the inquiry. "
        "The inquiry itself must be completed within one month."
    )

    a.statute_citation = (
        "Section 20 of the Tamil Nadu Regulation of Rights and Responsibilities of "
        "Landlords and Tenants Act, 2017. Sub-section (1) prohibits any landlord from "
        "cutting off or withholding essential supply or service. Sub-section (2) empowers "
        "the Rent Authority to pass an interim order directing immediate restoration. "
        "The Rent Authority exercises these powers under Section 31 of the Act."
    )

    a.suggested_rewrite = (
        "Neither party shall cut off, withhold, or cause to be cut off or withheld any "
        "essential supply or service as defined in Section 20 of the Tamil Nadu Regulation "
        "of Rights and Responsibilities of Landlords and Tenants Act, 2017, regardless of "
        "any dispute between the parties."
    )

    a.notice_paragraph = (
        "You have cut off / threatened to cut off essential services to the premises. This "
        "is in direct contravention of Section 20(1) of the Tamil Nadu Regulation of Rights "
        "and Responsibilities of Landlords and Tenants Act, 2017. My client reserves the "
        "right to approach the Rent Authority for immediate interim restoration under "
        "Section 20(2) and to seek the penalty prescribed under Section 20(4)."
    )


PATTERN_BUILDERS = {
    1: _build_p1,
    2: _build_p2,
    3: _build_p3,
    4: _build_p4,
    5: _build_p5,
    6: _build_p6,
    7: _build_p7,
    8: _build_p8,
    9: _build_p9,
    10: _build_p10,
    11: _build_p11,
}
