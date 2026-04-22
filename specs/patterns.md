# patterns.md
## Landlorded clause-detection patterns
### Test subject: Estancia 1136 lease deed dated 17 March 2025

**Purpose:** This file is the bridge between legal research and Day 2 code.  
Each pattern below is drafted so a developer can translate it directly into clause detection, extraction, evaluation, and output logic.

**Primary contract used as test subject:** `Estancia 1136 - Final Contract.pdf`

---

## Pattern 1: Deposit-to-rent ratio

### What it is
The security deposit amount, expressed as a multiple of monthly rent. Chennai norm is 2–3 months; TN statute default is 3 months subject to contract override.

### Why it matters
Excessive deposits are the single largest source of tenant financial exposure. A 6-month deposit on a ₹75,000 rent locks up ₹4,50,000 of the tenant's money with no interest and increases move-out refund risk.

### Detection — how the tool finds it
Look for clauses containing any of:
- "security deposit"
- "caution deposit"
- "interest free deposit"
- "interest free security deposit"
- "refundable deposit"
- "advance" when used alongside a large lump-sum amount

Also detect the monthly rent clause, usually phrased as:
- "monthly rent"
- "monthly lease rent"
- "rental"
- "monthly rental"
- "lease rent"

### Extraction — what the tool pulls out
- deposit_amount (integer, INR)
- deposit_currency (default INR)
- monthly_rent (integer, INR)
- deposit_ratio = deposit_amount / monthly_rent
- deposit_interest_bearing (boolean)
- deposit_refund_clause_present (boolean)
- deposit_refund_timeline_specified (boolean)
- registration_status_evidenced (boolean)

### Evaluation rule — how the tool judges it
- ratio <= 2 → INFO
- 2 < ratio <= 3 → INFO
- 3 < ratio <= 6 → YELLOW FLAG
- ratio > 6 → RED FLAG

The tool must **not** say the amount is automatically illegal. Section 11(1) contains the qualifier **"Save an agreement to the contrary"**.

### Statute reference
- TN Act 2017, Section 11(1)
- TN Act 2017, Section 11(2)
- TN Act 2017, Sections 4 and 4-A
- CPA 2019, Section 2(47)
- Indian Contract Act 1872, Section 23

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"Your security deposit is ₹[deposit_amount], which is [deposit_ratio] months of monthly rent. Under Section 11(1) of the TN Tenancy Act 2017, the statutory default is three months' rent, but the Act allows parties to contract otherwise. This means the deposit is not automatically illegal, but the higher amount materially increases refund-risk and supports unfairness / unconscionability arguments."

**Severity:** INFO / YELLOW FLAG / RED FLAG

**Statute citation to include in generated legal notice:**  
"Section 11(1) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 establishes three times the monthly rent as the statutory norm for security deposits. While the Act permits parties to contract to a higher amount, the deposit of ₹[X] (being [N] months' rent) deviates significantly from the statutory norm and prevailing Chennai market practice."

**Suggested clause rewrite:**  
"The Security Deposit shall be an amount equivalent to three (3) months of the monthly Lease Rent and shall be refundable in full at the time of handover of vacant possession, subject only to itemized deductions supported by proof for actual damages beyond normal wear and tear or arrears of rent."

**Suggested legal notice paragraph:**  
"My client paid a security deposit of ₹[X], which represents [N] months of monthly rent. While Section 11(1) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 permits parties to contract otherwise, the amount is substantially above the statutory norm of three months. Under Section 11(2), the deposit is to be refunded at the time of handover of vacant possession. Any refusal or delay in refund, or any deduction not supported by documented damages, will be disputed."

### Confidence
MEDIUM

### Example from real agreement
From Estancia lease deed dated 17 March 2025:  
*"The Interest free Security Deposit amounting to Rs. 4,50,000/ (Rupees Four Lakh Fifty Thousand only) is being deposited to Lessor's account on or before the commencement of the tenancy (01 June 2025)."*  
Monthly rent: ₹75,000. Ratio: 6.0. Registration not evidenced in the reviewed file.

### Edge cases / notes
- Some agreements split deposit into "security deposit" + "advance" — detector must not automatically sum them unless the contract treats them as one pool.
- Some agreements use "token advance" or "booking advance" — this is distinct from security deposit unless later adjusted.
- If agreement is unregistered or registration is not evidenced, landlord reliance on written deposit terms becomes weaker; tool should flag this as compounding context.
- Interest-bearing deposits are rare but should reduce unfairness severity if clearly documented.

---

## Pattern 2: Missing clear refund timeline / weak refund language

### What it is
A deposit-refund clause that allows deductions but does not clearly commit to refund at handover or through a documented itemized process.

### Why it matters
This is the most common source of move-out disputes. Vague refund language lets landlords delay payment or make unsupported deductions.

### Detection — how the tool finds it
Look for:
- "deduct from security deposit"
- "return only the balance"
- "damages will be deducted"
- "arrears of rent or other charges"
- absence of phrases like "at the time of handover", "within [X] days", "itemized deductions", "supported by bills"

### Extraction — what the tool pulls out
- refund_timeline_text
- deduction_language_text
- itemization_required (boolean)
- proof_required_for_deductions (boolean)
- handover_linked_refund (boolean)
- damage_deduction_scope

### Evaluation rule — how the tool judges it
- Explicit refund at handover + itemized deductions + proof → INFO
- Refund at handover but no itemization/proof → YELLOW FLAG
- No clear refund timing and broad deduction discretion → RED FLAG

### Statute reference
- TN Act 2017, Section 11(2)
- TN Act 2017, Section 24(2)
- TN Rules 2019, Rule 7(2)
- CPA 2019, Section 2(47)

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"The agreement allows deductions from the deposit but does not create a transparent, itemized refund mechanism. Section 11(2) requires refund at the time of taking over vacant possession after due deduction of tenant liability."

**Severity:** YELLOW FLAG / RED FLAG

**Statute citation to include in generated legal notice:**  
"Section 11(2) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017, read with Rule 7(2) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Rules, 2019."

**Suggested clause rewrite:**  
"At the time of handover of vacant possession, the Lessor shall refund the Security Deposit after deducting only documented arrears or actual damage beyond normal wear and tear, supported by an itemized statement and proof."

**Suggested legal notice paragraph:**  
"The lease does not provide a lawful and transparent refund mechanism. Under Section 11(2) of the Act, the security deposit is to be refunded at the time of taking over vacant possession after due deduction of tenant liability. Any delayed refund or unsupported deduction shall be disputed as unlawful withholding and unfair trade practice."

### Confidence
HIGH

### Example from real agreement
*"The LESSOR is entitled to deduct the value of fixtures/fittings handed over in damaged / non-working condition or towards arrears of rent or other charges payable by the LESSEE ... and return only the balance out of it if any, to the LESSEE."*

### Edge cases / notes
- A clause can be partly compliant on timing but still defective on proof and itemization.
- Pair with Pattern 6 where fixture schedule and appliance deductions are involved.

---

## Pattern 3: Pre-tenancy advance / booking advance

### What it is
A lump-sum amount paid before commencement of tenancy to "confirm" or secure the lease arrangement.

### Why it matters
Such advances are often poorly defined. In disputes, landlords may treat them as forfeitable, non-refundable, or separate from the main deposit framework.

### Detection — how the tool finds it
Look for:
- "advance amount"
- "booking amount"
- "to confirm the lease arrangement"
- payment due before tenancy commencement

### Extraction — what the tool pulls out
- advance_amount
- due_date
- purpose_label
- adjustable_against_deposit (boolean)
- refundable (boolean)
- forfeiture_terms_exist (boolean)

### Evaluation rule — how the tool judges it
- Advance clearly adjusted into deposit / rent and refund logic stated → INFO
- Advance mentioned but treatment unclear → YELLOW FLAG
- Advance non-refundable or forfeitable without standards → RED FLAG

### Statute reference
- TN Act 2017, Section 24(1)
- Indian Contract Act 1872, Section 23
- CPA 2019, Section 2(47)

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"The agreement contains a pre-tenancy advance of ₹[advance_amount] to confirm the arrangement, but its later treatment is not clearly explained. This creates ambiguity over whether it is part of the deposit, part of rent, or separately forfeitable."

**Severity:** YELLOW FLAG / RED FLAG

**Statute citation to include in generated legal notice:**  
"Section 24(1) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017."

**Suggested clause rewrite:**  
"Any booking or advance amount paid before commencement shall stand adjusted against the Security Deposit or first month's rent and shall not be separately forfeited except for documented breach expressly stated in this Agreement."

**Suggested legal notice paragraph:**  
"My client paid an advance of ₹[X] before commencement of tenancy. The agreement does not clearly state whether this amount is to be adjusted toward deposit or rent, nor the circumstances in which any part of it may be retained. Such ambiguity must be construed against the drafter."

### Confidence
MEDIUM

### Example from real agreement
*"an advance amount of Rs.2,25,000 ... will be deposited in the Lessor's account on or before February 19, 2025, to confirm the lease arrangement."*

### Edge cases / notes
- Some agreements later merge this amount into the security deposit; detector should check later clauses before output.
- Do not automatically count advance toward deposit ratio unless the contract or payment trail proves that link.

---

## Pattern 4: Lock-in period with early-exit penalty

### What it is
A clause preventing termination for an initial period and imposing compensation if the tenant exits before or during the notice period.

### Why it matters
Such clauses can trap tenants and turn the deposit into an automatic penalty pool.

### Detection — how the tool finds it
Look for:
- "shall not terminate"
- "first [X] months"
- "lock-in"
- "two months compensation"
- "notice period"
- "recovered from security deposit"

### Extraction — what the tool pulls out
- lockin_months
- notice_period_months
- compensation_formula
- compensation_source
- mutuality_of_exit_rights
- termination_exceptions

### Evaluation rule — how the tool judges it
- Mutual notice, no lock-in, no penalty → INFO
- Lock-in present but penalty limited and mutual → YELLOW FLAG
- Lock-in plus automatic compensation recovery from deposit → RED FLAG

### Statute reference
- TN Act 2017, Section 5
- TN Act 2017, Section 11(2)
- TN Act 2017, Section 21
- TN Act 2017, Section 29(2)
- Indian Contract Act 1872, Section 23

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"The agreement imposes an 8-month lock-in and allows two months' rent plus maintenance to be recovered from the security deposit if the tenant exits before or without completing the notice period. This is a high-risk clause because it combines movement restriction with automatic monetary recovery."

**Severity:** RED FLAG

**Statute citation to include in generated legal notice:**  
"Sections 5, 11(2), 21 and 29(2) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017."

**Suggested clause rewrite:**  
"Either party may terminate by giving one month's written notice. No lock-in or penalty shall apply except actual documented loss directly caused by proven breach."

**Suggested legal notice paragraph:**  
"The clause imposing an 8-month lock-in and authorizing recovery of two months' rent and maintenance from the Security Deposit is oppressive and one-sided. Any deduction on this basis, without proof of actual loss and without lawful refund at handover, will be disputed."

### Confidence
MEDIUM

### Example from real agreement
*"The LESSE shall not terminate this agreement for the first 8 (eight) months ... two months compensation of the monthly rental & maintenance will be recovered from Security Deposit."*

### Edge cases / notes
- Some agreements call this "minimum commitment period" instead of lock-in.
- Distinguish a notice requirement from a penalty clause.
- If the landlord is bound by equivalent exit consequences, reduce severity slightly.

---

## Pattern 5: Repair and maintenance burden shifted to tenant

### What it is
A clause making the tenant responsible for day-to-day or equipment-related repairs that may overlap with statutory repair allocation.

### Why it matters
Many leases push repair and maintenance obligations beyond what Section 15 and the Second Schedule intend.

### Detection — how the tool finds it
Look for:
- "minor repairs"
- "day-to-day repairs"
- "regular service and maintenance"
- "exclusively used by the lessee"
- "handover in working condition"

### Extraction — what the tool pulls out
- repair_items_list
- appliance_maintenance_list
- tenant_repair_scope
- landlord_repair_scope
- working_condition_handover_text

### Evaluation rule — how the tool judges it
- Clause tracks Section 15 / Second Schedule closely → INFO
- Clause shifts minor repairs and consumables only → INFO / YELLOW FLAG
- Clause shifts structural or landlord-side obligations to tenant → RED FLAG

### Statute reference
- TN Act 2017, Section 15
- TN Act 2017, Second Schedule

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"The agreement makes the tenant responsible for several minor and appliance-related repairs. Some of this may align with Section 15 and the Second Schedule, but the exact items should be compared against the statutory allocation."

**Severity:** YELLOW FLAG unless clearly aligned

**Statute citation to include in generated legal notice:**  
"Section 15 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017, read with the Second Schedule thereto."

**Suggested clause rewrite:**  
"Repair responsibilities shall follow Section 15 and the Second Schedule of the TN Tenancy Act. Structural repairs and landlord-side obligations shall remain with the Lessor."

**Suggested legal notice paragraph:**  
"To the extent the lease seeks to shift repair obligations beyond those assignable to the tenant under Section 15 read with the Second Schedule of the Act, my client disputes the enforceability of such additional burden."

### Confidence
MEDIUM

### Example from real agreement
*"The LESSEE agrees to carry out all day-to-day minor repairs..."*  
and  
*"the lessee undertakes the regular service and maintenance of the durables..."*

### Edge cases / notes
- Final severity depends on separately adding the Second Schedule to the corpus.
- Appliances like ACs and purifier can be contestable depending on drafting and usage.

---

## Pattern 6: Broad deduction rights for fixtures / appliances / non-working condition

### What it is
A clause allowing the landlord to deduct from the security deposit for damaged or non-working fixtures, fittings, appliances, or other charges without objective valuation standards.

### Why it matters
This is the main route by which deposits get depleted at move-out.

### Detection — how the tool finds it
Look for:
- "damages will be deducted from the security deposit"
- "non-working condition"
- "fixtures/fittings"
- "other charges payable"
- "return only the balance"

### Extraction — what the tool pulls out
- deductible_items_scope
- proof_required (boolean)
- itemization_required (boolean)
- normal_wear_and_tear_exception_present (boolean)
- inspection_mechanism_present (boolean)
- inventory_schedule_present (boolean)

### Evaluation rule — how the tool judges it
- Inventory exists + deductions limited + wear-and-tear carveout + proof required → INFO
- Inventory exists but deduction standards vague → YELLOW FLAG
- Broad deduction rights without proof / wear-and-tear standard → RED FLAG

### Statute reference
- TN Act 2017, Section 11(2)
- TN Act 2017, Section 15
- CPA 2019, Section 2(47)

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"The agreement includes a fixture schedule, which helps, but the deduction language is still broad and does not clearly require itemization, proof, or a normal-wear-and-tear standard."

**Severity:** YELLOW FLAG / RED FLAG

**Statute citation to include in generated legal notice:**  
"Section 11(2) and Section 15 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017."

**Suggested clause rewrite:**  
"Deductions from the Security Deposit shall be limited to itemized, documented loss for damage beyond normal wear and tear, cross-checked against the signed inventory."

**Suggested legal notice paragraph:**  
"The lease permits broad deduction of alleged fixture and appliance value from the deposit without setting out a documented valuation or wear-and-tear standard. Any such deduction, unless supported by itemized proof, will be disputed."

### Confidence
HIGH

### Example from real agreement
*"Any damages will be deducted from the security deposit."*  
and  
*"deduct the value of fixtures/fittings handed over in damaged / non-working condition..."*

### Edge cases / notes
- If there is a signed move-in inventory with condition photographs, severity can be reduced.
- Schedule I helps identify items, but not condition-at-handover by itself.

---

## Pattern 7: Missing tenancy registration / no Rent Authority evidence

### What it is
A written lease that does not evidence registration with the Tamil Nadu Rent Authority.

### Why it matters
Under Sections 4 and 4-A, registration is central to evidentiary use. Missing registration weakens reliance on the written terms.

### Detection — how the tool finds it
Look for:
- "T.R. No."
- "Tenancy Registration Number"
- "registered with Rent Authority"
- portal certificate annexure
- tenancy.tn.gov.in reference

If none appear in the reviewed agreement, flag as **registration not evidenced in reviewed file**.

### Extraction — what the tool pulls out
- registration_number_present
- registration_reference_text
- registration_certificate_annexed
- filing_date_present
- registration_status_evidenced

### Evaluation rule — how the tool judges it
- Registration number / certificate evidenced → INFO
- Registration not evidenced in file → YELLOW FLAG
- Express non-registration admission → RED FLAG

### Statute reference
- TN Act 2017, Sections 4 and 4-A
- TN Rules 2019, Rule 3

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"The reviewed agreement does not show a Tenancy Registration Number or other Rent Authority registration evidence. This does not conclusively prove non-registration, but it creates a compliance and evidentiary risk."

**Severity:** YELLOW FLAG / RED FLAG

**Statute citation to include in generated legal notice:**  
"Sections 4 and 4-A of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017, read with Rule 3 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Rules, 2019."

**Suggested clause rewrite:**  
"This Agreement shall be registered with the Rent Authority within the prescribed period, and the Tenancy Registration Number shall be recorded in the body of this Agreement."

**Suggested legal notice paragraph:**  
"The written lease relied upon by you does not disclose any Rent Authority registration particulars. Under Sections 4 and 4-A of the Act, registration is mandatory and directly affects the evidentiary use of the document."

### Confidence
HIGH

### Example from real agreement
Reviewed lease deed contains stamp-paper execution details, but no visible T.R. No., Rent Authority registration reference, or registration certificate annexure.

### Edge cases / notes
- Absence in the PDF is not proof of non-registration; output must say "not evidenced" unless a separate registration certificate is reviewed.
- Pair with Pattern 1 and Pattern 4 because registration affects landlord reliance on those clauses.

---

## Pattern 8: Landlord entry / inspection clause without written 24-hour notice

### What it is
A clause permitting landlord entry for inspection or repair but not expressly requiring the written-notice structure contemplated by statute.

### Why it matters
Tenants need privacy protection. Inspection clauses are often drafted too loosely.

### Detection — how the tool finds it
Look for:
- "permit the lessor"
- "enter the said premises"
- "view the state of affairs"
- "during reasonable hours"
- no mention of "written notice" or "24 hours"

### Extraction — what the tool pulls out
- entry_purpose
- notice_required
- notice_mode
- notice_hours
- entry_time_limit
- workmen_allowed

### Evaluation rule — how the tool judges it
- Written notice + 24 hours + purpose stated + time window → INFO
- Purpose and reasonable hours stated, but no written notice language → YELLOW FLAG
- Unrestricted inspection / surprise entry language → RED FLAG

### Statute reference
- TN Act 2017, Section 17

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"The lease allows landlord entry during reasonable daytime hours, but it does not clearly require written 24-hour notice. Section 17 of the Act is more specific and should prevail."

**Severity:** YELLOW FLAG

**Statute citation to include in generated legal notice:**  
"Section 17 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017."

**Suggested clause rewrite:**  
"The Lessor may enter only upon written notice given at least twenty-four hours in advance, specifying the purpose, day, and time of entry, and only within the statutory time window."

**Suggested legal notice paragraph:**  
"Any entry into the premises must comply with Section 17 of the Act, including prior written notice and specified purpose. Any attempt at informal or surprise entry will be treated as unlawful interference with possession."

### Confidence
HIGH

### Example from real agreement
*"To permit the LESSOR and her duly authorized agents or servants ... during reasonable hours in the daytime to enter the said premises..."*

### Edge cases / notes
- Emergency entry is separate and should not be over-flagged.
- Some agreements mention "prior intimation" but not written notice; treat as incomplete.

---

## Pattern 9: Utility / association / ancillary charges passed through to tenant

### What it is
A clause making the tenant pay electricity, water, generator, internet, additional water cost, taxes, or association-linked charges.

### Why it matters
Some of these charges may be legitimate, but vague drafting can let unrelated costs be shifted to the tenant.

### Detection — how the tool finds it
Look for:
- "exclusive of"
- "electricity charges"
- "generator charges"
- "water tax"
- "additional cost of water"
- "maintenance charges"
- "association"

### Extraction — what the tool pulls out
- included_charges
- excluded_charges
- pass_through_charge_list
- billing_basis_present
- meter_basis_present
- association_linked_costs

### Evaluation rule — how the tool judges it
- Clearly itemized and objectively measurable charges → INFO
- Additional or variable charges without billing basis → YELLOW FLAG
- Open-ended "other charges" recovery without limit → RED FLAG

### Statute reference
- TN Act 2017, Section 13
- TN Act 2017, Section 20
- TN Act 2017, Section 24(1)

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"The lease clearly passes several utility and association-linked charges to the tenant. Meter-based electricity is easier to justify; open-ended water-shortage or other unspecified charges deserve closer scrutiny."

**Severity:** INFO / YELLOW FLAG / RED FLAG

**Statute citation to include in generated legal notice:**  
"Sections 13, 20 and 24(1) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017."

**Suggested clause rewrite:**  
"All tenant-borne charges shall be limited to objectively measurable, documented charges specifically listed in the Agreement, and copies of supporting bills shall be shared on demand."

**Suggested legal notice paragraph:**  
"My client disputes any charge not specifically listed and objectively measurable under the Agreement. Any additional recovery demand unsupported by meter reading, bill, or contractual basis is denied."

### Confidence
MEDIUM

### Example from real agreement
*"The above noted LEASE RENT is exclusive of the electricity/Generator charges, Gas, Internet..."*  
and  
*"The LESSEE agrees to pay any additional cost of water ... as well as the water tax..."*

### Edge cases / notes
- Do not flag standard meter-based electricity as inherently unfair.
- Distinguish maintenance already included in rent from separately demanded maintenance.

---

## Pattern 10: Occupancy / use / subletting / association-rules control block

### What it is
A cluster of clauses restricting occupancy, banning subletting, requiring residential-only use, and incorporating association / club rules into termination risk.

### Why it matters
These clauses are common, but they can become grounds for eviction or deposit leverage if drafted broadly and enforced selectively.

### Detection — how the tool finds it
Look for:
- "residential purposes only"
- "strictly for [X] people"
- "not to sublet"
- "not assign"
- "breach of rules and regulations"
- "association"
- "club rules"

### Extraction — what the tool pulls out
- occupancy_cap
- permitted_use
- subletting_ban
- assignment_ban
- incorporated_external_rules
- termination_trigger_list

### Evaluation rule — how the tool judges it
- Standard residential-use and no-subletting clause → INFO
- External rules incorporated by vague reference only → YELLOW FLAG
- Broad termination tied to undefined external rules + deposit risk → RED FLAG

### Statute reference
- TN Act 2017, Section 7
- TN Act 2017, Section 21(2)(c)
- TN Act 2017, Section 21(2)(d)
- TN Act 2017, Section 29

### Recommended output — what the tool tells the user
**Plain-English verdict:**  
"The agreement contains standard residential-use and no-subletting restrictions, but it also ties termination to breaches of separate association / club rules. That external-rule incorporation should be reviewed carefully because it widens eviction risk."

**Severity:** YELLOW FLAG

**Statute citation to include in generated legal notice:**  
"Sections 7, 21(2)(c), 21(2)(d), and 29 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017."

**Suggested clause rewrite:**  
"Any external rules incorporated into this Agreement shall be attached as schedules and shall not operate to create automatic termination unless the breach is material, documented, and consistent with applicable law."

**Suggested legal notice paragraph:**  
"While my client does not dispute lawful residential-use and no-subletting restrictions, any attempt to terminate the tenancy on the basis of unspecified or unattached association rules will be disputed as vague and overbroad."

### Confidence
MEDIUM

### Example from real agreement
*"residential purposes strictly for 6 people"*  
*"Not to sublet, assign or otherwise part with possession..."*  
*"Any breach of rules and regulations as laid down in the Maintenance Agreement and club rules signed as Annexure IV"*

### Edge cases / notes
- Some agreements attach the rules; if attached and specific, severity can be reduced.
- Distinguish lawful occupancy control from arbitrary guest restrictions.

---

## Pattern 11: Essential services guarantee

### What it is
A situation where the landlord (directly or through the association, broker, or any third party) has cut off or threatened to cut off essential services — water, electricity, parking, lift, sanitary services, communication links, conservancy, or similar — as leverage in a deposit, rent, or renewal dispute.

### Why it matters
Section 20 is one of the strongest tenant-protection provisions in the TN Act 2017. Unlike most contract-interpretation patterns (Patterns 1–10), this is a tenant-remedy pattern: it gives the Rent Authority power to pass an **interim restoration order** before the inquiry is even complete, and imposes a penalty on the person responsible. This makes it operationally different from occupancy/subletting (Pattern 10) — it is not about lease control, it is about urgent relief.

### Detection — how the tool finds it
Look for:
- "cut off" / "cut-off"
- "withhold" / "withheld"
- "disconnect" / "disconnected"
- "suspend" / "suspended"
- "block access" / "blocked"
- "water" (in context of denial or restriction)
- "electricity" / "power supply"
- "parking" / "car park" / "parking slot"
- "lift" / "elevator"
- "generator" / "DG set"
- "sanitary" / "sewage"
- "common area" / "staircase lights"
- "association" blocking or restricting services
- any clause permitting the landlord to restrict or suspend services upon breach or non-payment

Also detect threat language:
- "shall be entitled to disconnect"
- "landlord may stop"
- "services will be withdrawn"
- "access will be denied"

### Extraction — what the tool pulls out
- service_type (water, electricity, parking, lift, generator, sanitary, communication, other)
- who_cut_service (landlord, association, broker, third party, unclear)
- cut_or_threatened (actual | threatened | clause-authorized)
- date_started (if actual interruption reported by user)
- safety_impact (boolean — e.g., water/sanitary cut in occupied premises)
- evidence_available (WhatsApp messages, photos, association notices, meter readings)
- linked_to_dispute (boolean — is the cut-off connected to a rent/deposit/renewal dispute?)

### Evaluation rule — how the tool judges it
- Clause in agreement authorizing landlord to cut services upon breach → YELLOW FLAG
- Threatened interruption (verbal or written) → YELLOW FLAG
- Actual service interruption by landlord or through association/others → RED FLAG

### Statute reference
- TN Act 2017, Section 20(1) — prohibition on cutting off or withholding essential supply or service
- TN Act 2017, Section 20(2) — Rent Authority's power to pass interim restoration order
- TN Act 2017, Section 20(3) — one-month inquiry completion timeline
- TN Act 2017, Section 20(4) — penalty up to ₹5,000 on person responsible
- TN Act 2017, Section 20(5) — compensation for frivolous complaints
- TN Act 2017, Section 31 — Rent Authority has same powers as Rent Court for Section 20 proceedings

### Recommended output — what the tool tells the user
**Plain-English verdict:**
"This is not just a contract issue. Section 20 of the TN Tenancy Act makes it unlawful for any landlord — directly or through others — to cut off or withhold essential services including water, electricity, parking, lifts, and sanitary services. If services have been interrupted, the Rent Authority can pass an interim order restoring them immediately, even before completing the inquiry. The inquiry itself must be completed within one month."

**Severity:** YELLOW FLAG (threatened or clause-authorized) / RED FLAG (actual interruption)

**Statute citation to include in generated legal notice:**
"Section 20 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017. Sub-section (1) prohibits any landlord from cutting off or withholding essential supply or service. Sub-section (2) empowers the Rent Authority to pass an interim order directing immediate restoration. The Rent Authority exercises these powers under Section 31 of the Act."

**Suggested clause rewrite:**
"Neither party shall cut off, withhold, or cause to be cut off or withheld any essential supply or service as defined in Section 20 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017, regardless of any dispute between the parties."

**Suggested legal notice paragraph:**
"You have [cut off / threatened to cut off] [service_type] to the premises. This is in direct contravention of Section 20(1) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017, which prohibits any landlord from cutting off or withholding essential supply or service. My client reserves the right to approach the Rent Authority for immediate interim restoration under Section 20(2) and to seek the penalty prescribed under Section 20(4). Any attempt to use service disruption as leverage in the ongoing [deposit/rent/renewal] dispute will be treated as coercive and unlawful."

**Suggested WhatsApp message (bilingual):**
"You have stopped [water/electricity/parking] to the flat. Under Section 20 of the TN Tenancy Act, this is unlawful. The Rent Authority can order immediate restoration and impose a penalty. Please restore [service] within 24 hours. / நீங்கள் [தண்ணீர்/மின்சாரம்/பார்க்கிங்] நிறுத்தியுள்ளீர்கள். TN வாடகை சட்டம் பிரிவு 20 இது சட்டவிரோதம். வாடகை ஆணையம் உடனடி மறுசீரமைப்பு உத்தரவிடலாம். 24 மணி நேரத்தில் [சேவை] மீட்டமைக்கவும்."

### Confidence
HIGH

### Example from real agreement
No direct essential-services cut-off clause found in the Estancia lease deed. However, the agreement incorporates association rules by reference (Pattern 10), and association-mediated service denial (e.g., blocking parking access, restricting lift use) is a common escalation path in Chennai apartment complexes during landlord-tenant disputes.

### Edge cases / notes
- The person cutting off services may not be the landlord directly — associations, facility managers, or brokers acting on landlord instructions are all covered by Section 20(1) ("through any person").
- Section 20(5) allows compensation against the tenant if the complaint is frivolous or vexatious — tool should warn users to have evidence before filing.
- Pair with Pattern 9 (utility charges) — a landlord who stops paying association maintenance and causes service denial is still covered.
- Pair with Pattern 10 (association rules) — if termination or service denial is linked to association rule breach, both patterns fire.
- This pattern should also trigger when reviewing WhatsApp messages or user-reported facts, not just agreement text.

---

## Prioritization for Day 2 coding

1. Pattern 1 — Deposit-to-rent ratio  
2. Pattern 4 — Lock-in period with early-exit penalty  
3. Pattern 7 — Missing tenancy registration / no Rent Authority evidence  
4. Pattern 2 — Missing clear refund timeline / weak refund language  
5. Pattern 6 — Broad deduction rights for fixtures / appliances / non-working condition  
6. Pattern 3 — Pre-tenancy advance / booking advance  
7. Pattern 5 — Repair and maintenance burden shifted to tenant  
8. Pattern 10 — Occupancy / use / subletting / association-rules control block  
9. Pattern 8 — Landlord entry / inspection clause without written 24-hour notice  
10. Pattern 9 — Utility / association / ancillary charges passed through to tenant
11. Pattern 11 — Essential services guarantee (urgent relief / Rent Authority interim order)
