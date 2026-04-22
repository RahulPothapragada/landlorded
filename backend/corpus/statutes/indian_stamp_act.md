# Indian Stamp Act, 1899 (as applicable to Tamil Nadu) — Article 35 (Lease) for Landlorded

**Statute family:** Indian Stamp Act, 1899  
**Tamil Nadu amendment used for this extract:** Indian Stamp (Tamil Nadu Amendment) Act, 2004  
**Compilation date:** 22 April 2026  
**Compilation scope:** This is a focused extract for lease-deed stamp duty analysis in Tamil Nadu, centered on Article 35 as substituted for Tamil Nadu.  
**Primary purpose in Landlorded:** To help detect possible under-stamping of residential lease deeds in Chennai and elsewhere in Tamil Nadu.  
**Source note:** The Article 35 text below follows the Tamil Nadu amendment text available through PRS Legislative Research. PRS itself warns users to verify against the latest government publication / gazette before acting. This file should therefore be treated as a working statutory extract, not as the final authority for filing strategy.  
**Interpretation note:** For ordinary fixed-term residential leases, the practical computation question is usually whether duty has been paid on the total amount of rent, fine, premium, or advance payable under the lease, using the slab in Article 35. Final deployment logic should still be cross-checked against current Tamil Nadu registration practice and any later amendment, notification, or departmental guidance.

---

## Definitions note from the parent Act

Under section 2(16) of the Indian Stamp Act, 1899, **"lease"** means a lease of immovable property, and includes a patta, a kabuliyat or other written undertaking to cultivate, occupy, or pay or deliver rent for immovable property, any instrument by which tolls are let, and any writing on an application for a lease intended to signify that the application is granted.

---

## Article 35 — Lease

**35. LEASE**, including an under-lease or sub-lease and any agreement to let or sub-let—

### (a) Where the period of lease is below thirty years
**One rupee for every Rs. 100 or part thereof** of the amount of **rent, fine, premium or advance, if any, payable**.

### (b) Where the period of lease is thirty years and above and up to ninety-nine years
**Four rupees for every Rs. 100 or part thereof** of the amount of **rent, fine, premium or advance, if any, payable**.

### (c) Where the period of lease is above ninety-nine years
**Eight rupees for every Rs. 100 or part thereof** of the amount of **rent, fine, premium or advance, if any, payable**.

**Proviso:**  
Where an agreement to lease is stamped with the ad valorem stamp required for a lease, and a lease in pursuance of such agreement is subsequently executed, the duty on such lease shall not exceed **twenty rupees**.

---

## Working implementation note for Landlorded

For a typical residential lease in Chennai:

- identify the lease term
- place it in the correct Article 35 slab
- identify the amounts payable under the instrument:
  - total rent payable for the term
  - fine, if any
  - premium, if any
  - advance, if any
- apply the Article 35 rate to that amount

### Initial coding heuristic
For **leases below thirty years**, start with this rule:

`stamp duty = 1 rupee for every 100 rupees or part thereof of the amount of rent + fine + premium + advance payable`

### Caution
This file is a statutory working extract. Before treating any mismatch as a legal defect in production, verify against:
- the latest Tamil Nadu amendment position
- current Registration Department practice
- any later circular / notification affecting lease deed duty or classification

---

## Why this matters in Landlorded

This is the provision that lets the tool flag cases where a lease deed appears to have been executed on plainly insufficient stamp value, such as a nominal stamp that does not match the Article 35 ad valorem requirement for the stated rent structure and duration.
