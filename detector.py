"""Clause detection and extraction for Landlorded's 11 patterns."""

import re
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    INFO = "INFO"
    YELLOW = "YELLOW FLAG"
    RED = "RED FLAG"


@dataclass
class PatternResult:
    """Result of running one pattern against agreement text."""
    pattern_id: int
    pattern_name: str
    fired: bool
    severity: Severity | None = None
    matched_text: list[str] = field(default_factory=list)
    extracted: dict = field(default_factory=dict)
    explanation: str = ""
    statute_refs: list[str] = field(default_factory=list)


def detect_all(lease_text: str, schedule_text: str = "") -> list[PatternResult]:
    """Run all 11 patterns against extracted lease text."""
    full = lease_text + "\n" + schedule_text
    return [
        _p1_deposit_ratio(lease_text),
        _p2_refund_timeline(lease_text),
        _p3_advance(lease_text),
        _p4_lockin(lease_text),
        _p5_repair_burden(lease_text),
        _p6_broad_deductions(lease_text + "\n" + schedule_text),
        _p7_registration(lease_text),
        _p8_entry_clause(lease_text),
        _p9_utility_charges(lease_text),
        _p10_occupancy_subletting(lease_text),
        _p11_essential_services(lease_text),
    ]


# --- Helpers ---

def _find_amounts(text: str) -> list[tuple[str, int]]:
    """Find INR amounts in text. Returns list of (context, amount_int).

    Handles OCR noise: 'Rs .', 'Rs,', 'Rs .63,000', and amounts in words.
    """
    results = []
    # Match Rs. / Rs / INR / Rupees followed by amount with optional commas
    for m in re.finditer(
        r'(?:Rs\s*[.,]?\s*|INR\s*|Rupees\s+)([\d,]+(?:\.\d+)?)\s*/?\s*-?\s*(?:\(([^)]+)\))?',
        text, re.IGNORECASE
    ):
        raw = m.group(1).replace(",", "").split(".")[0]
        try:
            amount = int(raw)
            if amount < 100:  # Skip noise like page numbers
                continue
            context = text[max(0, m.start() - 120):m.end() + 120]
            results.append((context, amount))
        except ValueError:
            continue

    # Also try to extract amounts from word forms like "Two Lakh Seventy Thousand"
    word_amounts = _parse_word_amounts(text)
    results.extend(word_amounts)

    return results


def _parse_word_amounts(text: str) -> list[tuple[str, int]]:
    """Extract INR amounts expressed in words (e.g., 'Two Lakh Seventy Thousand')."""
    results = []
    word_values = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
        "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    }
    # Match patterns like "Two Lakh Seventy Thousand"
    for m in re.finditer(
        r'\b((?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|'
        r'thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|'
        r'thirty|forty|fifty|sixty|seventy|eighty|ninety)\s*)+(?:lakh|lac|lakhs?|'
        r'crore|crores?|thousand|hundred)\s*(?:(?:and\s+)?(?:one|two|three|four|'
        r'five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|'
        r'sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|'
        r'seventy|eighty|ninety)\s*(?:lakh|lac|lakhs?|crore|crores?|thousand|hundred)\s*)*)',
        text, re.IGNORECASE
    ):
        word_str = m.group(1).strip().lower()
        amount = _words_to_number(word_str, word_values)
        if amount and amount >= 1000:
            context = text[max(0, m.start() - 120):m.end() + 120]
            results.append((context, amount))
    return results


def _words_to_number(text: str, word_values: dict) -> int | None:
    """Convert Indian English number words to integer."""
    text = re.sub(r'\s+', ' ', text.strip())
    total = 0
    current = 0

    for word in re.split(r'[\s-]+', text):
        word = word.lower().rstrip('s')  # "lakhs" -> "lakh"
        if word in ('and', ''):
            continue
        elif word in word_values:
            current += word_values[word]
        elif word in ('hundred',):
            current *= 100
        elif word in ('thousand',):
            current *= 1000
            total += current
            current = 0
        elif word in ('lakh', 'lac'):
            current *= 100000
            total += current
            current = 0
        elif word in ('crore',):
            current *= 10000000
            total += current
            current = 0

    total += current
    return total if total > 0 else None


def _search(text: str, terms: list[str]) -> list[str]:
    """Find sentences/clauses containing any of the given terms."""
    matches = []
    text = _normalize(text)
    lower = text.lower()
    for term in terms:
        for m in re.finditer(re.escape(term.lower()), lower):
            start = max(0, m.start() - 150)
            end = min(len(text), m.end() + 150)
            # Expand to sentence boundaries
            while start > 0 and text[start] not in ".;\n":
                start -= 1
            while end < len(text) and text[end] not in ".;\n":
                end += 1
            snippet = text[start:end].strip().lstrip(".;")
            if snippet and snippet not in matches:
                matches.append(snippet)
    return matches


def _normalize(text: str) -> str:
    """Collapse all whitespace (including newlines) into single spaces."""
    return re.sub(r'\s+', ' ', text)


def _has_any(text: str, terms: list[str]) -> bool:
    lower = _normalize(text).lower()
    return any(t.lower() in lower for t in terms)


# --- Pattern detectors ---

def _p1_deposit_ratio(text: str) -> PatternResult:
    result = PatternResult(1, "Deposit-to-rent ratio", False,
                           statute_refs=["TN Act 2017, Section 11(1)", "TN Act 2017, Section 11(2)"])

    deposit_terms = ["security deposit", "caution deposit", "interest free deposit",
                     "interest free security deposit", "refundable deposit",
                     "interest free advance", "deposit of Rs"]
    rent_terms = ["monthly rent", "monthly lease rent", "lease rent", "monthly rental",
                  "rent of Rs", "month"]

    deposit_matches = _search(text, deposit_terms)
    rent_matches = _search(text, rent_terms)

    if not deposit_matches and not rent_matches:
        return result

    result.fired = True
    result.matched_text = deposit_matches[:3] + rent_matches[:2]

    # Try to extract amounts
    amounts = _find_amounts(text)
    deposit_amount = None
    monthly_rent = None

    for ctx, amt in amounts:
        ctx_lower = ctx.lower()
        if any(t in ctx_lower for t in deposit_terms):
            if deposit_amount is None or amt > deposit_amount:
                deposit_amount = amt
        if any(t in ctx_lower for t in rent_terms):
            if monthly_rent is None:
                monthly_rent = amt

    # Fallback: if we couldn't associate amounts with terms via context,
    # use heuristics — the larger amount is likely deposit, smaller is rent
    if (deposit_amount is None or monthly_rent is None) and len(amounts) >= 2:
        sorted_amts = sorted(set(amt for _, amt in amounts), reverse=True)
        if monthly_rent is None and len(sorted_amts) >= 1:
            # Smallest reasonable amount is likely monthly rent
            candidates = [a for a in sorted_amts if 5000 <= a <= 500000]
            if candidates:
                monthly_rent = candidates[-1]
        if deposit_amount is None and monthly_rent and len(sorted_amts) >= 2:
            # Deposit is usually larger than rent
            candidates = [a for a in sorted_amts if a > monthly_rent]
            if candidates:
                deposit_amount = candidates[-1]  # smallest amount larger than rent

    result.extracted["deposit_amount"] = deposit_amount
    result.extracted["monthly_rent"] = monthly_rent
    result.extracted["deposit_interest_bearing"] = not _has_any(text, ["interest free", "interest-free"])

    if deposit_amount and monthly_rent and monthly_rent > 0:
        ratio = round(deposit_amount / monthly_rent, 1)
        result.extracted["deposit_ratio"] = ratio
        if ratio <= 3:
            result.severity = Severity.INFO
            result.explanation = (
                f"Security deposit is Rs. {deposit_amount:,}, which is {ratio} months of "
                f"monthly rent (Rs. {monthly_rent:,}). Within the Section 11(1) statutory norm."
            )
        elif ratio <= 6:
            result.severity = Severity.YELLOW
            result.explanation = (
                f"Security deposit is Rs. {deposit_amount:,}, which is {ratio} months of "
                f"monthly rent (Rs. {monthly_rent:,}). Above the 3-month statutory norm in "
                f"Section 11(1). Not automatically illegal due to the 'save an agreement to "
                f"the contrary' qualifier, but increases refund risk and supports "
                f"unconscionability arguments."
            )
        else:
            result.severity = Severity.RED
            result.explanation = (
                f"Security deposit is Rs. {deposit_amount:,}, which is {ratio} months of "
                f"monthly rent (Rs. {monthly_rent:,}). Significantly above the 3-month norm. "
                f"Strong basis for unconscionability and unfair trade practice arguments."
            )
    else:
        result.severity = Severity.YELLOW
        result.explanation = (
            "Deposit and/or rent amounts could not be reliably extracted. "
            "Manual review needed to compute ratio."
        )

    return result


def _p2_refund_timeline(text: str) -> PatternResult:
    result = PatternResult(2, "Missing refund timeline / weak refund language", False,
                           statute_refs=["TN Act 2017, Section 11(2)", "TN Act 2017, Section 24(2)",
                                         "TN Rules 2019, Rule 7(2)"])

    deduction_terms = ["deduct from security deposit", "deducted from the security deposit",
                       "return only the balance", "damages will be deducted",
                       "arrears of rent or other charges", "non-working condition",
                       "entitled to deduct", "deduction of any dues",
                       "compensation towards any repairs", "damages payable"]
    refund_quality_terms = ["at the time of handover", "within", "itemized", "supported by bills",
                            "itemised", "proof of damage"]

    matches = _search(text, deduction_terms)
    if not matches:
        return result

    result.fired = True
    result.matched_text = matches[:3]

    has_handover_link = _has_any(text, ["at the time of handing over", "at the time of handover",
                                        "at the time of taking over"])
    has_itemization = _has_any(text, ["itemized", "itemised", "item-wise", "itemwise"])
    has_proof_req = _has_any(text, ["supported by", "proof of", "bills", "invoices"])
    has_wear_tear = _has_any(text, ["wear and tear", "normal wear", "fair wear"])

    result.extracted["handover_linked_refund"] = has_handover_link
    result.extracted["itemization_required"] = has_itemization
    result.extracted["proof_required_for_deductions"] = has_proof_req
    result.extracted["wear_tear_exception"] = has_wear_tear

    if has_handover_link and has_itemization and has_proof_req:
        result.severity = Severity.INFO
        result.explanation = "Refund mechanism includes handover linkage, itemization, and proof requirement."
    elif has_handover_link and not (has_itemization and has_proof_req):
        result.severity = Severity.YELLOW
        result.explanation = (
            "Refund is linked to handover, but deduction language lacks itemization "
            "and/or proof requirement. Section 11(2) requires refund at handover after "
            "due deduction of tenant liability — broad discretion without standards is risky."
        )
    else:
        result.severity = Severity.RED
        result.explanation = (
            "No clear refund timing and broad deduction discretion. Section 11(2) requires "
            "refund at the time of taking over vacant possession. The current language gives "
            "the landlord unilateral deduction power without accountability."
        )

    return result


def _p3_advance(text: str) -> PatternResult:
    result = PatternResult(3, "Pre-tenancy advance / booking advance", False,
                           statute_refs=["TN Act 2017, Section 24(1)"])

    advance_terms = ["advance amount", "booking amount", "to confirm the lease arrangement",
                     "advance of Rs", "advance of rs"]

    matches = _search(text, advance_terms)
    if not matches:
        return result

    result.fired = True
    result.matched_text = matches[:3]

    # Try to find advance amount
    advance_amount = None
    for ctx, amt in _find_amounts(text):
        if any(t in ctx.lower() for t in ["advance amount", "advance of", "confirm the lease"]):
            advance_amount = amt
            break

    result.extracted["advance_amount"] = advance_amount

    adjustable = _has_any(text, ["adjusted against", "adjusted towards", "part of the deposit",
                                  "adjusted into"])
    refundable = _has_any(text, ["refundable advance", "advance shall be refunded"])
    forfeitable = _has_any(text, ["forfeit", "non-refundable", "not refundable"])

    result.extracted["adjustable_against_deposit"] = adjustable
    result.extracted["refundable"] = refundable
    result.extracted["forfeitable"] = forfeitable

    if adjustable or refundable:
        result.severity = Severity.INFO
        result.explanation = (
            f"Pre-tenancy advance of Rs. {advance_amount:,} found. "
            "Treatment is stated (adjustable/refundable)."
            if advance_amount else
            "Pre-tenancy advance found with stated adjustment terms."
        )
    elif forfeitable:
        result.severity = Severity.RED
        result.explanation = (
            f"Pre-tenancy advance of Rs. {advance_amount:,} appears non-refundable/forfeitable "
            "without clear standards."
            if advance_amount else
            "Pre-tenancy advance is non-refundable/forfeitable without clear standards."
        )
    else:
        result.severity = Severity.YELLOW
        result.explanation = (
            f"Pre-tenancy advance of Rs. {advance_amount:,} found, but treatment is unclear — "
            "not explicitly adjustable against deposit or rent, and not clearly refundable."
            if advance_amount else
            "Pre-tenancy advance found but its treatment (adjustable? refundable? forfeitable?) "
            "is not clearly stated."
        )

    return result


def _p4_lockin(text: str) -> PatternResult:
    result = PatternResult(4, "Lock-in period with early-exit penalty", False,
                           statute_refs=["TN Act 2017, Section 5", "TN Act 2017, Section 11(2)",
                                         "TN Act 2017, Section 21", "TN Act 2017, Section 29(2)"])

    lockin_terms = ["shall not terminate", "lock-in", "lock in", "first 8", "first 6",
                    "first 12", "first 3", "first eight", "first six", "first twelve",
                    "minimum commitment", "period of 11 months", "period of 12 months",
                    "penalty clause"]
    penalty_terms = ["compensation", "recovered from security deposit",
                     "recovered from the security", "will be recovered",
                     "two months compensation", "penalty",
                     "forced re-entry", "forced reentry",
                     "right of forced", "vacating the premises"]
    notice_terms = ["notice period", "months in advance", "written notice of",
                    "notice of 2", "notice of two"]

    lockin_matches = _search(text, lockin_terms)
    penalty_matches = _search(text, penalty_terms)

    if not lockin_matches and not penalty_matches:
        return result

    result.fired = True
    result.matched_text = lockin_matches[:2] + penalty_matches[:2]

    # Extract lock-in months
    lockin_months = None
    for m in re.finditer(r'first\s+(\d+)\s*\(?(\w+)?\)?\s*months?', text, re.IGNORECASE):
        lockin_months = int(m.group(1))
        break
    if not lockin_months:
        for m in re.finditer(r'first\s+(eight|six|twelve|three|nine|ten|eleven)\s+months?', text, re.IGNORECASE):
            word_to_num = {"three": 3, "six": 6, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
            lockin_months = word_to_num.get(m.group(1).lower())
            break
    if not lockin_months:
        # Try "period of N months" pattern (common in scanned agreements)
        for m in re.finditer(r'period\s+of\s+(\d+)\s*months?', text, re.IGNORECASE):
            lockin_months = int(m.group(1))
            break

    has_penalty = _has_any(text, penalty_terms)
    has_notice = _has_any(text, notice_terms)
    deposit_recovery = _has_any(text, ["recovered from security deposit", "recovered from the security",
                                        "recovered from Security Deposit"])

    result.extracted["lockin_months"] = lockin_months
    result.extracted["has_penalty"] = has_penalty
    result.extracted["has_notice_period"] = has_notice
    result.extracted["penalty_from_deposit"] = deposit_recovery

    if lockin_months and has_penalty and deposit_recovery:
        result.severity = Severity.RED
        result.explanation = (
            f"{lockin_months}-month lock-in with compensation recovered from security deposit. "
            "This combines movement restriction with automatic monetary recovery — high risk."
        )
    elif lockin_months and has_penalty:
        result.severity = Severity.YELLOW
        result.explanation = (
            f"{lockin_months}-month lock-in with penalty clause. "
            "Penalty exists but may not be directly tied to deposit recovery."
        )
    elif lockin_months:
        result.severity = Severity.YELLOW
        result.explanation = (
            f"{lockin_months}-month lock-in found. No explicit penalty but lock-in "
            "itself restricts tenant mobility."
        )
    else:
        result.severity = Severity.YELLOW
        result.explanation = "Lock-in or penalty language detected. Review clause details."

    return result


def _p5_repair_burden(text: str) -> PatternResult:
    result = PatternResult(5, "Repair and maintenance burden shifted to tenant", False,
                           statute_refs=["TN Act 2017, Section 15", "TN Act 2017, Second Schedule"])

    repair_terms = ["minor repairs", "day-to-day repairs", "day to day repairs",
                    "regular service and maintenance", "exclusively used by the lessee",
                    "handover all fixtures", "good working condition",
                    "lessee agrees to carry out", "replacement of water tap",
                    "replacement of fused", "repair of or replace",
                    "make good or pay", "broken, lost, damaged",
                    "damages payable by the tenant"]
    appliance_terms = ["air-conditioner", "air conditioner", "AC", "water purifier",
                       "water heater", "motor pump", "fan"]

    matches = _search(text, repair_terms)
    if not matches:
        return result

    result.fired = True
    result.matched_text = matches[:3]

    has_appliance_maintenance = _has_any(text, ["regular service and maintenance of the durables",
                                                  "service and maintenance of the durables",
                                                  "maintenance of the durables"])

    result.extracted["has_appliance_maintenance"] = has_appliance_maintenance
    result.extracted["repair_items_detected"] = [t for t in appliance_terms if t.lower() in text.lower()]

    if has_appliance_maintenance:
        result.severity = Severity.YELLOW
        result.explanation = (
            "Tenant bears day-to-day minor repairs AND regular service/maintenance of "
            "durables (ACs, water purifier, etc.). The appliance maintenance burden "
            "should be compared against Section 15 and the Second Schedule."
        )
    else:
        result.severity = Severity.INFO
        result.explanation = (
            "Tenant bears day-to-day minor repairs (tap washers, fuses, bulbs, etc.). "
            "This may align with Section 15 and the Second Schedule."
        )

    return result


def _p6_broad_deductions(text: str) -> PatternResult:
    result = PatternResult(6, "Broad deduction rights for fixtures/appliances", False,
                           statute_refs=["TN Act 2017, Section 11(2)", "TN Act 2017, Section 15",
                                         "CPA 2019, Section 2(47)"])

    deduction_terms = ["damages will be deducted", "deducted from the security deposit",
                       "non-working condition", "fixtures/fittings",
                       "fixtures/ fittings", "return only the balance",
                       "entitled to deduct", "other charges payable",
                       "deduction of any dues", "compensation towards any repairs",
                       "damages payable", "repairs and damages",
                       "broken, lost, damaged", "make good or pay"]

    matches = _search(text, deduction_terms)
    if not matches:
        return result

    result.fired = True
    result.matched_text = matches[:3]

    has_itemization = _has_any(text, ["itemized", "itemised", "item-wise"])
    has_proof = _has_any(text, ["supported by proof", "proof of damage", "invoices",
                                 "documented", "bills for"])
    has_wear_tear = _has_any(text, ["wear and tear", "normal wear", "fair wear",
                                     "reasonable wear"])
    has_inspection = _has_any(text, ["joint inspection", "inspection report", "move-out inspection"])
    has_inventory = _has_any(text, ["schedule", "Schedule I", "list of fixtures",
                                     "inventory"])

    result.extracted["itemization_required"] = has_itemization
    result.extracted["proof_required"] = has_proof
    result.extracted["wear_tear_exception"] = has_wear_tear
    result.extracted["inspection_mechanism"] = has_inspection
    result.extracted["inventory_schedule"] = has_inventory

    if has_inventory and has_itemization and has_proof and has_wear_tear:
        result.severity = Severity.INFO
        result.explanation = "Deduction clause has inventory, itemization, proof, and wear-and-tear standard."
    elif has_inventory and not (has_itemization and has_proof):
        result.severity = Severity.YELLOW
        result.explanation = (
            "Fixture schedule exists (helps identify items), but deduction language "
            "still lacks itemization and/or proof requirement. Broad discretion risk."
        )
    else:
        result.severity = Severity.RED
        result.explanation = (
            "Broad deduction rights without proof, itemization, or wear-and-tear standard. "
            "This is the main route by which deposits get depleted at move-out."
        )

    return result


def _p7_registration(text: str) -> PatternResult:
    result = PatternResult(7, "Missing tenancy registration / Rent Authority", False,
                           statute_refs=["TN Act 2017, Sections 4 and 4-A", "TN Rules 2019, Rule 3"])

    registration_terms = ["T.R. No", "Tenancy Registration Number",
                          "registered with Rent Authority", "tenancy.tn.gov.in",
                          "Rent Authority registration", "registration number",
                          "registration certificate"]

    has_registration = _has_any(text, registration_terms)

    result.fired = True  # Always fires — absence is itself the finding

    if has_registration:
        result.severity = Severity.INFO
        result.matched_text = _search(text, registration_terms)[:2]
        result.explanation = "Registration evidence found in the agreement."
        result.extracted["registration_evidenced"] = True
    else:
        result.severity = Severity.YELLOW
        result.explanation = (
            "No Tenancy Registration Number or Rent Authority registration evidence "
            "found in the reviewed file. Under Sections 4 and 4-A, registration is "
            "mandatory. This does not prove non-registration but creates a compliance "
            "and evidentiary risk."
        )
        result.extracted["registration_evidenced"] = False

    return result


def _p8_entry_clause(text: str) -> PatternResult:
    result = PatternResult(8, "Landlord entry without written 24-hour notice", False,
                           statute_refs=["TN Act 2017, Section 17"])

    entry_terms = ["permit the lessor", "enter the said premises",
                   "view the state of affairs", "during reasonable hours",
                   "enter the premises", "inspection",
                   "permit the landlord", "enter the apartment",
                   "view the condition"]

    matches = _search(text, entry_terms)
    if not matches:
        return result

    result.fired = True
    result.matched_text = matches[:2]

    has_written_notice = _has_any(text, ["written notice", "prior written notice",
                                          "notice in writing"])
    has_24_hours = _has_any(text, ["24 hours", "twenty-four hours", "24-hour",
                                    "twenty four hours"])

    result.extracted["written_notice_required"] = has_written_notice
    result.extracted["24_hour_notice"] = has_24_hours

    if has_written_notice and has_24_hours:
        result.severity = Severity.INFO
        result.explanation = "Entry clause includes written notice and 24-hour requirement."
    elif _has_any(text, ["reasonable hours", "daytime"]):
        result.severity = Severity.YELLOW
        result.explanation = (
            "Entry permitted during reasonable daytime hours, but no explicit written "
            "24-hour notice requirement. Section 17 is more specific and should prevail."
        )
    else:
        result.severity = Severity.RED
        result.explanation = "Unrestricted or loosely worded entry clause without notice safeguards."

    return result


def _p9_utility_charges(text: str) -> PatternResult:
    result = PatternResult(9, "Utility / ancillary charges passed to tenant", False,
                           statute_refs=["TN Act 2017, Section 13", "TN Act 2017, Section 20",
                                         "TN Act 2017, Section 24(1)"])

    utility_terms = ["exclusive of", "electricity charges", "generator charges",
                     "water tax", "additional cost of water", "maintenance charges",
                     "association", "Gas, Internet", "electric light and power",
                     "diesel consumption", "metered cooking gas", "cooking gas",
                     "standby power"]

    matches = _search(text, utility_terms)
    if not matches:
        return result

    result.fired = True
    result.matched_text = matches[:3]

    charges_detected = []
    for term in ["electricity", "generator", "water", "gas", "internet", "cable",
                 "maintenance", "AC maintenance", "DTH"]:
        if term.lower() in text.lower():
            charges_detected.append(term)

    has_meter = _has_any(text, ["meter", "sub meter", "sub-meter", "Main / Sub"])
    has_open_ended = _has_any(text, ["other charges", "additional cost", "any additional",
                                      "such a demand arises"])

    result.extracted["charges_detected"] = charges_detected
    result.extracted["meter_basis"] = has_meter
    result.extracted["open_ended_charges"] = has_open_ended

    if has_open_ended:
        result.severity = Severity.YELLOW
        result.explanation = (
            f"Charges passed to tenant: {', '.join(charges_detected)}. "
            "Some charges are open-ended or variable without clear billing basis."
        )
    else:
        result.severity = Severity.INFO
        result.explanation = (
            f"Charges passed to tenant: {', '.join(charges_detected)}. "
            "Charges appear to be specifically listed."
        )

    return result


def _p10_occupancy_subletting(text: str) -> PatternResult:
    result = PatternResult(10, "Occupancy / subletting / association-rules control", False,
                           statute_refs=["TN Act 2017, Section 7", "TN Act 2017, Section 21(2)(c)",
                                         "TN Act 2017, Section 21(2)(d)", "TN Act 2017, Section 29"])

    terms = ["residential purposes only", "strictly for", "not to sublet",
             "not sublet", "not to assign", "not assign", "part with possession",
             "breach of rules and regulations", "association", "club rules",
             "Maintenance Agreement"]

    matches = _search(text, terms)
    if not matches:
        return result

    result.fired = True
    result.matched_text = matches[:3]

    # Extract occupancy cap
    occupancy_cap = None
    m = re.search(r'strictly for\s+(\d+)\s+people', text, re.IGNORECASE)
    if m:
        occupancy_cap = int(m.group(1))

    has_external_rules = _has_any(text, ["rules and regulations", "club rules",
                                          "Maintenance Agreement", "Annexure IV",
                                          "association rules"])
    rules_attached = _has_any(text, ["attached hereto", "annexed hereto",
                                      "signed as Annexure"])

    result.extracted["occupancy_cap"] = occupancy_cap
    result.extracted["subletting_banned"] = _has_any(text, ["not to sublet", "not sublet"])
    result.extracted["external_rules_incorporated"] = has_external_rules
    result.extracted["rules_attached"] = rules_attached

    if has_external_rules and not rules_attached:
        result.severity = Severity.RED
        result.explanation = (
            "External association/club rules incorporated by vague reference but not attached. "
            "This widens eviction risk through undefined standards."
        )
    elif has_external_rules:
        result.severity = Severity.YELLOW
        result.explanation = (
            "External rules incorporated and referenced as annexure. "
            "Still review the actual content for overbroad termination triggers."
        )
    else:
        result.severity = Severity.INFO
        result.explanation = "Standard residential-use and no-subletting restrictions."

    return result


def _p11_essential_services(text: str) -> PatternResult:
    result = PatternResult(11, "Essential services guarantee", False,
                           statute_refs=["TN Act 2017, Section 20(1)-(5)",
                                         "TN Act 2017, Section 31"])

    threat_terms = ["shall be entitled to disconnect", "landlord may stop",
                    "services will be withdrawn", "access will be denied",
                    "cut off", "cut-off", "withhold", "disconnect", "suspend",
                    "block access", "immediate eviction", "forced re-entry",
                    "forced reentry", "change the lock", "occupy the apartment"]
    service_terms = ["water", "electricity", "parking", "lift", "elevator",
                     "generator", "sanitary", "sewage", "common area",
                     "staircase lights"]

    # Look for clauses that authorize the landlord to cut services
    threat_matches = _search(text, threat_terms)

    # Filter: flag if threat terms appear near service terms OR if it's a
    # lock-change / forced-entry threat (which denies access to all services)
    access_denial_terms = ["change the lock", "forced re-entry", "forced reentry",
                           "occupy the apartment", "immediate eviction"]
    relevant_matches = []
    for match in threat_matches:
        if _has_any(match, service_terms) or _has_any(match, access_denial_terms):
            relevant_matches.append(match)

    if not relevant_matches:
        # No clause-level threat found — this pattern mainly fires from user-reported facts
        return result

    result.fired = True
    result.matched_text = relevant_matches[:3]
    result.severity = Severity.YELLOW
    result.explanation = (
        "The agreement contains language that may authorize service disruption. "
        "Section 20(1) prohibits any landlord from cutting off or withholding "
        "essential services. The Rent Authority can order immediate restoration "
        "under Section 20(2)."
    )

    return result
