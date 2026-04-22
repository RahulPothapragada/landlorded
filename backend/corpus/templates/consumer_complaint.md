# Consumer Complaint Template — Landlorded

**Purpose:** Template for generating a consumer complaint for filing before the District Consumer Disputes Redressal Commission in Tamil Nadu, in a residential tenancy deposit/unfair terms dispute.  
**Jurisdiction:** Tamil Nadu — District Commission (claim up to Rs. 1 crore under Section 34, CPA 2019)  
**Filed under:** Section 35, Consumer Protection Act, 2019  
**Reference format:** Gujarat State Consumer Commission official format (adapted for TN tenancy disputes)  
**Usage:** The Landlorded agent populates `{{placeholders}}` from pattern extraction output. Conditional blocks marked with `{% if pattern_N %}` activate only when that pattern has fired.

---

## BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION, {{district_name}}, TAMIL NADU

**Consumer Complaint No. __________ of {{year}}**

[Complaint under Section 35 of the Consumer Protection Act, 2019]

---

### 1. Details of the Complainant

| Field | Details |
|-------|---------|
| Full Name | {{tenant_name}} |
| {{tenant_parentage}} | |
| Age | {{tenant_age}} years |
| Full Address | {{tenant_address}} |
| PIN Code | {{tenant_pin}} |
| Mobile No. | {{tenant_mobile}} |
| E-Mail | {{tenant_email}} |

{% if joint_tenants %}
<!-- Repeat for each joint complainant with same fields -->
{{joint_complainant_blocks}}
{% endif %}

**... COMPLAINANT(S)**

### V/s.

### 2. Details of the Opposite Party

**Opposite Party No. 1:**

| Field | Details |
|-------|---------|
| Full Name | {{landlord_name}} |
| {{landlord_relation}} | |
| Full Address | {{landlord_address}} |
| PIN Code | {{landlord_pin}} |
| Phone / Mobile No. | {{landlord_mobile}} |
| E-Mail | {{landlord_email}} |

{% if additional_opposite_parties %}
<!-- E.g., co-owner, broker, association -->
{{additional_op_blocks}}
{% endif %}

**... OPPOSITE PARTY/PARTIES**

---

### 3. Facts of the complaint and cause of action

The Complainant most respectfully submits as follows:

#### A. The tenancy arrangement

(i) That the Complainant entered into a **Lease Deed dated {{lease_date}}** with the Opposite Party No. 1 in respect of **{{premises_description}}** (hereinafter "the premises"), for a period of **{{lease_term}}** commencing from **{{lease_start_date}}** and expiring on **{{lease_end_date}}**.

(ii) That the monthly lease rent agreed under the said Lease Deed was **Rs. {{monthly_rent}} ({{monthly_rent_words}})**.

(iii) That at the commencement of the tenancy, the Complainant paid to the Opposite Party a sum of **Rs. {{deposit_amount}} ({{deposit_amount_words}})** towards **interest-free refundable security deposit**, acknowledged in the Lease Deed, paid through **{{deposit_payment_mode}}** on **{{deposit_payment_date}}**.

{% if pattern_3 %}
(iv) That the Complainant additionally paid an advance of **Rs. {{advance_amount}} ({{advance_amount_words}})** on **{{advance_date}}** to confirm the lease arrangement. The treatment of this advance — whether adjustable against deposit, rent, or separately forfeitable — was not clearly stated in the Lease Deed.
{% endif %}

(v) That throughout the tenancy period, the Complainant regularly paid the monthly lease rent and other agreed charges without default.

#### B. Deficiency of service and unfair trade practices in the lease terms

{% if pattern_1 %}
(vi) **Excessive security deposit:** The security deposit of Rs. {{deposit_amount}} represents **{{deposit_ratio}} months** of the monthly lease rent. Section 11(1) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 (hereinafter "the TN Tenancy Act") establishes three months' rent as the statutory norm. While the Act permits parties to contract to a higher amount, the deposit demanded was substantially above the statutory norm and prevailing Chennai market practice, obtained under conditions of unequal bargaining power.
{% endif %}

{% if pattern_2 %}
(vii) **No transparent refund mechanism:** The Lease Deed does not provide a transparent, itemized refund mechanism. Under Section 11(2) of the TN Tenancy Act, the security deposit is to be refunded at the time of taking over vacant possession after due deduction of tenant liability. The broad and unqualified deduction language in the Lease Deed does not meet this standard.
{% endif %}

{% if pattern_4 %}
(viii) **Oppressive lock-in and penalty:** The Lease Deed imposes a lock-in period of **{{lockin_months}} months** and authorizes recovery of **{{compensation_formula}}** from the security deposit if the Complainant exits before or without completing the notice period. This combines movement restriction with automatic monetary recovery without proof of actual loss.
{% endif %}

{% if pattern_5 %}
(ix) **Repair burden shifted beyond statute:** The Lease Deed seeks to shift repair and maintenance obligations to the Complainant beyond what is assignable under Section 15 of the TN Tenancy Act read with the Second Schedule thereto.
{% endif %}

{% if pattern_6 %}
(x) **Broad deduction rights without proof:** The Lease Deed permits deductions from the security deposit for alleged damage to fixtures, fittings, and appliances without requiring itemized proof, objective valuation, or a normal-wear-and-tear standard.
{% endif %}

{% if pattern_7 %}
(xi) **Non-registration with Rent Authority:** The Lease Deed does not disclose any Tenancy Registration Number or Rent Authority registration particulars. Under Sections 4 and 4-A of the TN Tenancy Act, read with Rule 3 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Rules, 2019, registration is mandatory.
{% endif %}

{% if pattern_8 %}
(xii) **Landlord entry without proper notice:** The Lease Deed permits landlord entry for inspection without expressly requiring prior written notice of at least twenty-four hours as contemplated under Section 17 of the TN Tenancy Act.
{% endif %}

{% if pattern_9 %}
(xiii) **Unspecified ancillary charges:** The Lease Deed passes through certain utility and association-linked charges without clear billing basis or measurement standards, contrary to Sections 13, 20, and 24(1) of the TN Tenancy Act.
{% endif %}

{% if pattern_10 %}
(xiv) **Vague external rules as termination triggers:** The Lease Deed ties termination to breaches of separate association or club rules that are not fully attached or specified, creating overbroad eviction risk.
{% endif %}

{% if pattern_11 %}
(xv) **Essential services cut off or threatened:** The Opposite Party has {{cut_or_threatened}} {{service_type}} to the premises, in contravention of Section 20(1) of the TN Tenancy Act, which prohibits any landlord — directly or through any person — from cutting off or withholding essential supply or service.
{% endif %}

#### C. The deposit dispute

(xvi) That the Complainant vacated the premises on **{{vacation_date}}** and handed over vacant possession to **{{handover_to}}** on the said date.

(xvii) That from the date of handing over possession, the Opposite Party became liable under Section 11(2) of the TN Tenancy Act to refund the security deposit after lawful and documented deductions only.

(xviii) That despite repeated requests — **{{prior_efforts_summary}}** — the Opposite Party has failed / refused to refund the security deposit of Rs. {{deposit_amount}}.

{% if deductions_claimed %}
(xix) That the Opposite Party has claimed deductions of **Rs. {{deductions_total}}** which are arbitrary, inflated, unsupported by itemized proof, and devoid of legal basis. The purported deductions include: {{deductions_list}}.
{% endif %}

(xx) That the conduct of the Opposite Party in withholding the security deposit without lawful basis, imposing one-sided lease terms, and failing to provide a transparent refund mechanism constitutes **deficiency of service** and **unfair trade practice** within the meaning of **Section 2(47) of the Consumer Protection Act, 2019**.

---

### 4. The Complainant is a "consumer" under the Act

(xxi) That the Complainant hired/availed of a service (residential accommodation) for consideration (rent and security deposit) and is therefore a **"consumer"** within the meaning of **Section 2(7)(ii) of the Consumer Protection Act, 2019**. The premises were used exclusively for residential purposes and not for any commercial purpose.

---

### 5. Prior efforts to resolve the dispute

(xxii) The Complainant made the following efforts to resolve the matter before filing this complaint:

(a) **Verbal requests:** {{verbal_efforts}}

(b) **Written correspondence / legal notice:** A legal notice dated **{{legal_notice_date}}** was sent to the Opposite Party by **{{notice_mode}}** demanding refund of the deposit within 15 days. {{notice_response}}

{% if whatsapp_evidence %}
(c) **WhatsApp / electronic communication:** {{whatsapp_summary}}
{% endif %}

(d) **Result:** Despite the above efforts, the Opposite Party has failed to refund the deposit or provide any legally sustainable justification for withholding.

---

### 6. Jurisdiction

(xxiii) This Hon'ble Commission has jurisdiction to entertain this complaint under **Section 34 of the Consumer Protection Act, 2019** because:

(a) The value of the service (total consideration paid including deposit and rent) does not exceed Rs. 1,00,00,000/- (Rupees One Crore);

(b) The cause of action — execution of the Lease Deed, payment of deposit, occupation of premises, and withholding of deposit — arose wholly within the territorial jurisdiction of this Hon'ble Commission at **{{premises_location}}**;

(c) The Complainant resides / personally works for gain at **{{complainant_jurisdiction_address}}**, which falls within the jurisdiction of this Hon'ble Commission.

---

### 7. Limitation

(xxiv) This complaint is filed within the period of limitation prescribed under **Section 69 of the Consumer Protection Act, 2019**. The cause of action arose on **{{cause_of_action_date}}** when the Opposite Party failed to refund the deposit after vacation and handover of possession.

{% if delay_condone_needed %}
In the alternative, the Complainant submits an application for condonation of delay of **{{delay_days}} days**, which is annexed herewith, on the ground that **{{delay_reason}}**.
{% endif %}

---

### 8. Prayer

In the facts and circumstances stated above, the Complainant most respectfully prays that this Hon'ble Commission may be pleased to:

**(a)** Direct the Opposite Party to **refund** to the Complainant the sum of **Rs. {{deposit_amount}} ({{deposit_amount_words}})**, together with interest at **{{interest_rate}}% per annum** from **{{cause_of_action_date}}** until the date of actual payment, after deducting only such amounts as are lawfully sustainable and supported by itemized proof;

{% if pattern_3 %}
**(b)** Direct the Opposite Party to additionally refund the pre-tenancy advance of **Rs. {{advance_amount}} ({{advance_amount_words}})** to the extent not lawfully adjusted, with interest;
{% endif %}

**({{next_sub}})** Direct the Opposite Party to pay **Rs. {{compensation_amount}}** as compensation for deficiency of service, mental agony, harassment, and financial loss suffered by the Complainant;

**({{next_sub}})** Direct the Opposite Party to **discontinue the unfair trade practice** and not to repeat the same, under **Section 39(1)(g)** of the Consumer Protection Act, 2019;

{% if pattern_11 %}
**({{next_sub}})** Direct the Opposite Party to **immediately restore** all essential services to the premises, including {{service_type}};
{% endif %}

**({{next_sub}})** Award **punitive damages** in such amount as this Hon'ble Commission deems fit, under the proviso to **Section 39(1)(d)** of the Consumer Protection Act, 2019;

**({{next_sub}})** Award **costs of this complaint** to the Complainant;

**({{next_sub}})** Grant such other and further relief as this Hon'ble Commission deems fit and proper in the facts and circumstances of the case.

---

### 9. Fee details

| Field | Details |
|-------|---------|
| Claim amount | Rs. {{claim_amount}} |
| Fee payable | Rs. {{fee_amount}} |
| Payment mode | {{fee_payment_mode}} |
| DD / RTGS / NEFT reference | {{fee_reference}} |
| Date | {{fee_date}} |

---

{% if authorized_representative %}
### 10. Authorized representative / Advocate

| Field | Details |
|-------|---------|
| Name | {{representative_name}} |
| Full Address (with PIN) | {{representative_address}} |
| Mobile No. | {{representative_mobile}} |
| E-Mail | {{representative_email}} |
{% endif %}

---

### 11. Verification and declaration

I, **{{tenant_name}}**, the Complainant above-named, do hereby solemnly declare that the facts stated in paragraphs (i) to ({{last_para}}) above are true and correct to the best of my knowledge and belief, and nothing material has been concealed.

**Place:** {{place}}  
**Date:** {{verification_date}}

**Signature of Complainant**

---

### Enclosures

1. Copy of Lease Deed dated {{lease_date}}
2. Proof of security deposit payment (bank transfer receipt / acknowledgment)
{% if pattern_3 %}
3. Proof of pre-tenancy advance payment
{% endif %}
4. Rent payment proof / bank statements for the tenancy period
5. Copy of legal notice dated {{legal_notice_date}} with postal receipt / AD card
6. Proof of service of legal notice (AD card / tracking receipt / email read receipt)
{% if notice_response_exists %}
7. Reply to legal notice from the Opposite Party, if any
{% endif %}
{% if deductions_claimed %}
8. Email / letter from Opposite Party showing purported deduction breakup
{% endif %}
{% if whatsapp_evidence %}
9. Exported WhatsApp chat records with the Opposite Party / broker
{% endif %}
{% if pattern_11 %}
10. Evidence of essential services interruption (photos, association notices, WhatsApp messages)
{% endif %}
11. Photographs of premises at the time of handover
12. Any other relevant documentary evidence
13. Vakalatnama, if Advocate is engaged
14. Index of documents

---

## Template metadata

**Patterns that activate conditional blocks:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11  
**Minimum patterns needed for a valid complaint:** At least one of Patterns 1–6 (deposit/refund related) + prior legal notice sent  
**CPA sections used:** 2(7), 2(47), 34, 35, 39, 69  
**TN Act sections potentially cited:** 4, 4-A, 5, 11(1), 11(2), 13, 15, 17, 20, 21, 24(1), 29  
**Agent responsibility:** Populate all `{{placeholders}}`, activate relevant `{% if %}` blocks, remove inactive blocks, renumber paragraphs sequentially, compute fee from claim amount before PDF generation  
**Review note:** This is a tool-generated draft. The user should review all facts and consider obtaining independent legal advice before filing. The complaint must be supported by an affidavit — the agent should flag this to the user.
