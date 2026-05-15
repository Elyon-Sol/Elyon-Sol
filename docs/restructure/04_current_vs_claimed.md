# Elyon-Sol  -  Current State vs. Claimed State (Rev. 2)

A living document. Left: what the code does, verified against `evaluator.py`, `pep.py`,
`manifest.json`, `test_pep.py`, and the v0.9.8.4 canonical whitepaper. Right: the delta
and the required action.

**Rev. 2 changes:** Added **G0** (CCS spec/implementation drift) as the anchor gap.
Corrected G1 (overstated in Rev. 1). Re-grounded all rows against the now-available canon.

This document's job is to be **uncomfortable and accurate**. A row closes only when code,
tests, or structure change such that the delta no longer exists  -  never by editing prose.

---

## G0  -  CCS specification/implementation drift  *(ANCHOR GAP)*

- **Canon (whitepaper section 12):** CCS is a **temporal invariant over state transitions**  - 
  `CCS(S_t, S_{t+1}, I)`. It requires authority transitions justified by AC^3, coverage
  transitions justified by T^26, and decision consistency `d_{t+1} = u_{t+1} AND c_{t+1}` across
  `S_t -> S_{t+1}`. section 13: "Eligibility does not persist across state transitions without
  revalidation." section 7/section 12.4 list invalid transitions: manifest version change, role/authority
  schema change, identity mapping inconsistency.
- **Code (`ccs_valid()`):** A **point-in-time** check  -  `ccs_valid is True`, version-string
  match, manifest SHA256 match. No `S_t`, no `S_{t+1}`, no prior state, no transition concept.
- **Delta:** The implemented CCS and the canonical CCS are **not the same invariant**. The
  code implements something closer to whitepaper section 8.1 "manifest-bound authority" than to
  section 12 CCS. **Confirmed cause: drift**  -  `ccs_valid()` was built without section 12's transition
  semantics in view; the shared name (input field `ccs_valid`, function `ccs_valid()`,
  invariant CCS) masked the gap; tests were written against the code, not the canon, so
  green tests created false confidence.
- **Status: DRIFTED.**
- **Action:**
  1. Rename the implemented check to its true scope (e.g. `manifest_integrity_valid()`).
  2. **Reserve** the name "CCS"  -  unused in code  -  until section 12 is implemented.
  3. Implement section 12 transition logic via the admissibility envelope (see Deliverable 05).
  4. Add canon-derived tests for section 12 (see G7).
  5. Until step 3 lands, the project must claim only "manifest integrity is enforced," **not**
     "CCS is implemented."

---

## Open gaps

### G1  -  README test count is stale  *(downgraded from Rev. 1)*
- **Code:** `test_pep.py` contains **4** tests (refuse-blocks-upstream, eligible-forwards-once,
  upstream-error-fails-closed, version-drift-refuses).
- **Claimed:** README says "Expected: 3 passed."
- **Delta:** README undercounts its own primary test file. The 30/34/37 figures in evidence
  docs are *plausibly* the same growing suite at different commits  -  not necessarily
  contradictory  -  but there is no commit-pinned source of truth.
- **Correction note:** Rev. 1 framed this as a credibility crisis across four contradictory
  numbers. That was overstated. The real issue is narrower: no single source of truth, and a
  stale README.
- **Action:** Create `EVIDENCE/STATE.md` pinned to a commit hash as the only authoritative
  count. README references it; hardcodes nothing.

### G2  -  Request schema drift
- **Code:** `pep.py` accepts `{target_url, context: {...}}` (nested). Confirmed by
  `test_pep.py`, which posts exactly that shape.
- **Claimed:** `interception_proof_001.md` / `_002.md` send flat top-level `AP`/`OP`.
- **Delta:** Those two proofs document an API the code rejects.
- **Action:** Rewrite both against the nested schema or move to `EVIDENCE/archive/` marked
  NON-CURRENT. `SPEC/request_schema.md` becomes the single source of truth.

### G3  -  Framing vs. mechanism  *(re-grounded against canon)*
- **Canon:** The whitepaper is a legitimate formal specification  -  formal interaction model,
  set-theoretic invariant definitions, explicit scope/non-goals, and a correct "Relation to
  Prior Work" section (RBAC/ABAC/XACML/UCON/reference monitor). The *specification* earns
  serious vocabulary.
- **Code:** Faithfully implements AC^3 and T^26. **Partially** implements CCS (see G0). Does
  not implement the section 4/section 15 failure constructs (CDD/SAP/PAD/ILT)  -  but the canon says those
  "do not participate in admissibility determination," so that is consistent, not a gap.
- **Delta:** The gap is **not** "prose oversells a toy." It is narrower and more precise: the
  *implementation* under-implements the *specification* on CCS, and the public framing claims
  the whole canon is realized. Rev. 1's "validator with delusions of grandeur" framing was
  wrong and is retracted.
- **Action:** Reframe public materials as "a formal admissibility specification (v0.9.8.4)
  with a faithful partial implementation." Use Deliverable 06 to state exactly which
  invariants are FULL / PARTIAL / DRIFTED. Apply the vocabulary ledger.

### G4  -  Bypassability
- **Code:** `pep.py` forwards via plain `requests.post`. The target cannot verify a call
  came through the gate.
- **Canon:** section 14 says Elyon-Sol "operates pre-execution" and "governs legitimacy." section 2 calls
  it a "non-executing governance substrate." The canon does not explicitly claim
  non-bypassability  -  but a reader reasonably infers enforcement.
- **Delta:** The gate is opt-in. A caller can hit the target directly and bypass it.
- **Action:** State the property plainly in README now. Add `TESTS/adversarial/test_bypass.py`
  demonstrating the bypass honestly. Schedule non-bypassable enforcement in build-outward
  scope; note the envelope-on-forwarded-call thread (Deliverable 05, open question 3).

### G5  -  "External" verification is not durable
- **Code/evidence:** Interception proofs rely on a local process (`127.0.0.1:9000`) or an
  ephemeral, now-dead `webhook.site` URL.
- **Claimed:** "Externally verified interception."
- **Delta:** Neither is a persistent, reproducible, third-party artifact.
- **Action:** Build a target-side logging receiver; commit its log to `EVIDENCE/proofs/`.
  Until then, downgrade the claim to "observable at the PEP."

### G6  -  `ccs_valid` input field is caller-asserted and circular
- **Code:** `ccs_valid()` checks `ctx["ccs_valid"] is True`  -  that the caller *claimed*
  continuity is valid. The real enforcement is the SHA256 + version match.
- **Delta:** The boolean is caller-controlled; it is not independent system verification.
  Combined with G0, the field name is actively misleading on two axes.
- **Action:** Remove the boolean (rely on SHA256 + version) **or** rename it to mark it
  clearly as a caller assertion. Resolve alongside the G0 rename so all three "ccs" names
  are disambiguated in one pass.

### G7  -  Tests are code-derived, not canon-derived
- **Code:** `test_pep.py` asserts the *implemented* behavior  -  version drift, SHA256 match,
  fail-closed forwarding. All four pass.
- **Canon:** No test in the repo is derived from a whitepaper section and cites it.
- **Delta:** Code-derived tests confirm the code; they cannot detect drift *from canon*  - 
  this is precisely how G0 went unnoticed. Green tests certified "CCS" that does not match section 12.
- **Action:** Add `TESTS/adversarial/` with a distinct category of **canon-derived tests**,
  each citing the whitepaper section it verifies. A section 12 test should currently **fail or be
  marked expected-fail**  -  that failure is the honest signal that CCS is not yet implemented.

### G8  -  Proof docs are narrated, not executable
- **Code:** The real evidence is the pytest suite.
- **Claimed:** `EVIDENCE/*.md` describe outcomes in prose.
- **Delta:** No proof is machine-checkable.
- **Action:** Each proof in `EVIDENCE/proofs/` names the test(s) backing it and the commit
  they passed at. Add CI; make `STATE.md` regenerable.

### G9  -  `stability_proof_001.md` is truncated
- **Claimed:** Sets up a 50-iteration stability test, ends mid-JSON with no results.
- **Delta:** The one stability proof contains no proof.
- **Action:** Finish it or delete it.

---

## Resolved gaps

*(none yet  -  populated as gaps close)*

---

## Priority order

1. **G0**  -  the anchor. Everything else is hygiene; this is the substantive finding.
2. **G7**  -  without canon-derived tests, the next G0 is invisible.
3. **G6 + G0 rename**  -  done together: disambiguate all three "ccs" names in one pass.
4. **G3**  -  reframe public materials once 06 makes the FULL/PARTIAL/DRIFTED picture concrete.
5. G1, G2, G8, G9  -  bookkeeping; do in a batch.
6. **G4, G5**  -  build-outward scope, after the base is honest.
