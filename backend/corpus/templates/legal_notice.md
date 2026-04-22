# Legal Notice Template — Landlorded

**Purpose:** Template for generating a legal notice demanding refund of security deposit and/or addressing unfair lease terms in a Tamil Nadu residential tenancy dispute.  
**Jurisdiction:** Tamil Nadu (Chennai / Chengalpattu / other TN districts)  
**Statutes referenced:** TN Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017; Consumer Protection Act, 2019; Indian Stamp Act, 1899; Transfer of Property Act, 1882  
**Usage:** The Landlorded agent populates `{{placeholders}}` from pattern extraction output. Conditional blocks marked with `{% if pattern_N %}` activate only when that pattern has fired.

---

**{{advocate_letterhead_or_sender_details}}**  
**Ref. No.:** {{ref_number}}  
**Date:** {{notice_date}}

**By Registered Post A/D / Speed Post / Email**

## LEGAL NOTICE

**To,**

{{landlord_block}}
<!-- Format each landlord/opposite party as:
1. **{{landlord_name}}**,
   {{landlord_relation}},
   {{landlord_address}}.
-->

### Subject: Legal notice demanding refund of security deposit of Rs. {{deposit_amount_words}} and addressing unlawful lease terms under the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017

{{salutation}},

Under instructions from and on behalf of my client **{{tenant_name}}**, aged about {{tenant_age}} years, {{tenant_parentage}}, residing at {{tenant_address}}, I hereby issue the present legal notice as follows:

---

### Facts of the tenancy

1. That my client entered into a **Lease Deed dated {{lease_date}}** with you in respect of **{{premises_description}}** (hereinafter "the premises"), for a period of **{{lease_term}}** commencing from **{{lease_start_date}}** and expiring on **{{lease_end_date}}**.

2. That under the said Lease Deed, the monthly lease rent agreed between the parties was **Rs. {{monthly_rent}} ({{monthly_rent_words}})**.

3. That at the commencement of the tenancy, my client paid to you a sum of **Rs. {{deposit_amount}} ({{deposit_amount_words}})** towards **interest-free refundable security deposit**, which amount was duly acknowledged in the Lease Deed.

4. That the said security deposit was paid through **{{deposit_payment_mode}}** on **{{deposit_payment_date}}**.

5. That during the entire period of the tenancy, my client regularly paid the monthly lease rent within time, and there was no wilful default in payment of rent.

---

### Clause-specific issues identified in the Lease Deed

{% if pattern_1 %}
#### Excessive security deposit (Pattern 1)

6. That the security deposit of Rs. {{deposit_amount}} represents **{{deposit_ratio}} months** of the monthly lease rent. Section 11(1) of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 (hereinafter "the Act") establishes **three months' rent** as the statutory norm for security deposits. While the Act permits parties to contract to a higher amount, the deposit of Rs. {{deposit_amount}} deviates substantially from the statutory norm and prevailing Chennai market practice, and the circumstances in which the agreement was executed raise concerns of unequal bargaining power and unconscionability.
{% endif %}

{% if pattern_2 %}
#### Weak or missing refund mechanism (Pattern 2)

7. That the Lease Deed does not provide a transparent, itemized refund mechanism. Under **Section 11(2) of the Act**, the security deposit is to be refunded at the time of taking over vacant possession after due deduction of tenant liability. The broad and unqualified deduction language in the Lease Deed does not meet this standard.
{% endif %}

{% if pattern_3 %}
#### Pre-tenancy advance with unclear treatment (Pattern 3)

8. That prior to commencement of the tenancy, my client paid an advance of **Rs. {{advance_amount}} ({{advance_amount_words}})** on **{{advance_date}}** to confirm the lease arrangement. The Lease Deed does not clearly state whether this amount stands adjusted against the security deposit, against rent, or is separately forfeitable. Such ambiguity must be construed against the drafter under settled principles of contract interpretation.
{% endif %}

{% if pattern_4 %}
#### Oppressive lock-in and early-exit penalty (Pattern 4)

9. That the Lease Deed imposes a lock-in period of **{{lockin_months}} months** and authorizes recovery of **{{compensation_formula}}** from the security deposit if the tenant exits before or without completing the notice period. This clause is oppressive and one-sided, combining movement restriction with automatic monetary recovery from the deposit without proof of actual loss. Reference is made to **Sections 5, 11(2), 21, and 29(2) of the Act**.
{% endif %}

{% if pattern_5 %}
#### Repair burden shifted beyond statutory allocation (Pattern 5)

10. That the Lease Deed seeks to shift repair and maintenance obligations to the tenant beyond what is assignable under **Section 15 of the Act read with the Second Schedule** thereto. To the extent such additional burden is imposed, it is disputed as exceeding the statutory allocation.
{% endif %}

{% if pattern_6 %}
#### Broad deduction rights without proof or standards (Pattern 6)

11. That the Lease Deed permits deductions from the security deposit for alleged damage to fixtures, fittings, and appliances without requiring itemized proof, objective valuation, or a normal-wear-and-tear standard. Any deduction made on this basis, without documented support, will be disputed as unlawful withholding under **Section 11(2) of the Act**.
{% endif %}

{% if pattern_7 %}
#### Non-registration with Rent Authority (Pattern 7)

12. That the Lease Deed does not disclose any Tenancy Registration Number or Rent Authority registration particulars. Under **Sections 4 and 4-A of the Act, read with Rule 3 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Rules, 2019**, registration is mandatory and directly affects the evidentiary use of the document. Your reliance on written terms favourable to you is materially weakened by the apparent non-registration.
{% endif %}

{% if pattern_8 %}
#### Landlord entry without written notice (Pattern 8)

13. That the Lease Deed permits landlord entry for inspection without expressly requiring prior written notice of at least twenty-four hours as contemplated under **Section 17 of the Act**. Any attempt at informal or unannounced entry will be treated as unlawful interference with my client's possession.
{% endif %}

{% if pattern_9 %}
#### Unspecified or open-ended ancillary charges (Pattern 9)

14. That the Lease Deed passes through certain utility and association-linked charges to the tenant without clear billing basis or measurement standards. My client disputes any charge not specifically listed and objectively measurable under the Lease Deed. Reference is made to **Sections 13, 20, and 24(1) of the Act**.
{% endif %}

{% if pattern_10 %}
#### Vague external rules incorporated as termination triggers (Pattern 10)

15. That the Lease Deed ties termination to breaches of separate association or club rules that are not fully attached or specified. Any attempt to terminate the tenancy or forfeit the deposit on the basis of unspecified or unattached external rules will be disputed as vague and overbroad under **Sections 7, 21(2)(c), 21(2)(d), and 29 of the Act**.
{% endif %}

{% if pattern_11 %}
#### Essential services cut off or threatened (Pattern 11)

16. That you have {{cut_or_threatened}} {{service_type}} to the premises. This is in direct contravention of **Section 20(1) of the Act**, which prohibits any landlord — directly or through any person — from cutting off or withholding any essential supply or service. Under **Section 20(2)**, the Rent Authority is empowered to pass an interim order directing immediate restoration pending inquiry. Under **Section 20(4)**, a penalty may be levied on the person responsible. My client reserves the right to approach the Rent Authority for immediate relief under Section 20.
{% endif %}

---

### Unfair trade practice under the Consumer Protection Act, 2019

{{cpa_paragraph_number}}. That the conduct described above, individually and collectively, amounts to **unfair trade practice** within the meaning of **Section 2(47) of the Consumer Protection Act, 2019**. The withholding of the security deposit without lawful basis, the imposition of one-sided lease terms, and the failure to provide transparent refund mechanisms constitute deceptive and unfair practices in the provision of a service (housing/accommodation) to a consumer as defined under **Section 2(7) of the said Act**.

---

### Demand

{{demand_paragraph_number}}. In the circumstances set out above, I hereby call upon you to:

**(a)** Refund to my client the sum of **Rs. {{deposit_amount}} ({{deposit_amount_words}})**, less only such amount, if any, as may be lawfully adjusted and specifically supported by itemized proof of actual damage beyond normal wear and tear or documented arrears of rent;

{% if pattern_3 %}
**(b)** Additionally refund the pre-tenancy advance of **Rs. {{advance_amount}} ({{advance_amount_words}})** to the extent not lawfully adjusted against rent or deposit;
{% endif %}

**({{next_sub}})** In case you claim any deduction whatsoever, furnish within the same period a full and document-supported statement of such deductions, along with copies of invoices, bills, repair estimates, proof of payment, photographs, inspection records, and the precise contractual clause on which you rely;

{% if pattern_11 %}
**({{next_sub}})** Immediately restore all essential services to the premises, including {{service_type}};
{% endif %}

within **15 (fifteen) days** from the date of receipt of this legal notice.

---

### Consequence of non-compliance

{{consequence_paragraph_number}}. Take notice that if you fail to comply with the above demand within the stipulated period, my client shall be constrained to initiate appropriate legal proceedings against you, including but not limited to:

(a) Filing a **consumer complaint** before the **District Consumer Disputes Redressal Commission, {{district_name}}**, under **Section 35 of the Consumer Protection Act, 2019**, seeking refund, compensation, costs, and all reliefs available under **Section 39** of the said Act, including punitive damages;

{% if pattern_7 %}
(b) Filing a complaint before the **Rent Authority, {{rent_authority_jurisdiction}}**, under the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017, regarding non-registration and related violations;
{% endif %}

{% if pattern_11 %}
(c) Filing an application before the **Rent Authority** under **Section 20** of the Act for interim restoration of essential services and imposition of penalty;
{% endif %}

(d) Such other civil and legal proceedings as may be advised,

entirely at your risk as to costs and consequences.

This notice is issued without prejudice to all other rights and remedies available to my client in law and equity.

A copy of this notice is retained for record and future action.

**Yours faithfully,**

{{sender_signature_block}}
<!-- Format:
[________________________]
**{{advocate_name}}**
Advocate / Sender
-->

---

## Suggested annexures

1. Copy of Lease Deed dated {{lease_date}}
2. Proof of security deposit payment (bank transfer receipt / acknowledgment)
3. Rent payment proof / bank statements
{% if pattern_3 %}
4. Proof of pre-tenancy advance payment
{% endif %}
5. Vacation / handover communication (email, WhatsApp, letter)
6. Any correspondence with landlord regarding deposit refund or disputes
{% if pattern_11 %}
7. Evidence of essential services interruption (photos, WhatsApp messages, association notices)
{% endif %}
8. Photographs of premises at the time of handover

---

## Template metadata

**Patterns that activate conditional blocks:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11  
**Minimum patterns needed for a valid notice:** At least one of Patterns 1–6 (deposit/refund related)  
**Agent responsibility:** Populate all `{{placeholders}}`, activate relevant `{% if %}` blocks, remove inactive blocks, renumber paragraphs sequentially before PDF generation  
**Review note:** This is a tool-generated draft. The user should review all facts and consider obtaining independent legal advice before dispatch.
