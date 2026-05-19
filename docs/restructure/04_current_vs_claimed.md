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
- **Status: PARTIALLY RESOLVED** - rename half closed (VL-012); build half open.
- **Action:**
  1. Rename the implemented check to its true scope (e.g. `manifest_integrity_valid()`).
     **DONE under VL-012.**
  2. **Reserve** the name "CCS"  -  unused in code  -  until section 12 is implemented.
     **DONE under VL-012**; reservation extended to test IDs.
  3. Implement section 12 transition logic via the admissibility envelope (see Deliverable 05).
     **OPEN** - this is the G0 build track.
  4. Add canon-derived tests for section 12 (see G7).
     **OPEN.**
  5. Until step 3 lands, the project must claim only "manifest integrity is enforced," **not**
     "CCS is implemented." **STANDING** - applies until step 3 lands.

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
  NON-CURRENT. `SPEC/request_schema.md` becomes the single source of truth. Per G10, the
  schema must also document the `version` field's caller-assertion semantics.

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

### G11  -  Manifest-source asymmetry in SHA256 check  *(surfaced by VL-012)*
- **Code:** `evaluator.manifest_integrity_valid()` (formerly `ccs_valid()`)
  calls `manifest_sha256()` which reads `MANIFEST/manifest.json` from disk
  via a hardcoded path, ignoring the `manifest` argument passed to the
  function.
- **Delta:** Tests in `TESTS/test_concurrency.py` define inline manifests
  (`TEST_MANIFEST`, `MUTABLE_MANIFEST`) with different schemas from the
  on-disk file. The tests pass because their `expected_manifest_sha256`
  values happen to match the on-disk file, not the inline test fixtures.
  The check is internally inconsistent: AC^3 and T^26 verify against the
  passed manifest argument; SHA256 verifies against disk.
- **Action:** Either (a) `manifest_sha256` should accept the manifest
  argument and hash it in memory; or (b) the API contract should be
  explicit that the manifest parameter is only consulted for AR/R/version
  and the SHA is always read from disk. Resolution deferred; flagged for
  scheduling.
- **Related:** G6/G10 disambiguation pass (VL-012) surfaced this during
  full read of `test_concurrency.py`; not in pass scope.

---

### G12  -  Canon section 11.1 under-specifies wire-origins of `I`'s components  *(surfaced by VL-015)*
- **Canon:** Section 11.1 defines the interaction tuple `I = (A, S, C, t)`
  but does not specify whether `C` (context) or `t` (time) are
  caller-supplied on the wire or system-derived. Section 11.9 explicitly
  specifies that `AR(I)` and `R(I)` are "derived exclusively from M";
  no comparable wire-origin clause exists for `C` or `t`. The silence
  is *meaningful* (not merely absent) because canon elsewhere
  demonstrates capacity to specify wire-origin when it intends to.
- **Code:** `pep.py` accepts `context: Dict[str, Any]` opaquely; no time
  field is on the wire. The interpretive choice (C caller-supplied, t
  PEP-supplied) was made silently in the schema's pre-VL-016 draft.
- **Delta:** Three procedurally-clean derivations (Claude, Grok, OpenAI)
  diverged on `C` and `t` specifically, and only on those components.
  The divergence traces to canon under-specification, not to verifier
  error. VL-016 premise verification confirmed the under-specification
  unanimously (premise 1 classified Under-specified by both Grok and
  OpenAI). OpenAI's argument-from-contrast framing is incorporated.
- **Status: PARTIALLY ADDRESSED** - schema-layer half closed (VL-016);
  canon-layer half open.
- **Action:**
  1. Make the interpretive choices for `C` and `t` explicit in the
     schema with rationale. **DONE under VL-016** (decision 1A:
     context stays caller-supplied required with section-12.1 reasoning;
     decision 2B: t stays NOT caller-supplied with section-9 +
     section-12.4 fail-closed reasoning).
  2. Resolve the canon-layer under-specification via a canon-version
     event under GR-1 (e.g., v0.9.8.5 or v0.10 adding wire-origin
     clauses for `A`, `S`, `C`, `t` analogous to section 11.9's
     clause for `AR`/`R`). **OPEN** - not currently scheduled;
     canon-version events are out of band per GR-1.

### G13  -  Manifest-pinning field provenance is mixed canon + envelope  *(surfaced by VL-015)*
- **Canon:** Section 11.9 requires the manifest to be "deterministic,
  versioned, and integrity-verifiable" as a property of the manifest
  itself. Section 12.4 lists manifest version change as an invalid
  transition. Neither clause specifies that the *request* must carry
  caller-asserted version/hash fields.
- **Code:** `manifest_integrity_valid()` (VL-012) consumes
  `expected_manifest_version` and `expected_manifest_sha256` as
  caller-asserted fields and refuses on mismatch. The fields are
  load-bearing per VL-012's convention.
- **Delta:** The schema's pre-VL-016 attribution ("canon basis:
  section 11.9 + section 12.4") implied pure-canon derivation. The
  wire mechanism (caller assertion of expected version + expected hash)
  is in fact an envelope-spec operationalization (Deliverable 05) that
  realizes section 11.9's required manifest properties on the wire,
  not a direct canon-clause requirement. VL-016 premise verification
  confirmed this unanimously (premise 2 classified Supported: canon
  requires manifest properties but does not require wire-level
  caller-asserted fields; premise 3 classified Supported: the
  envelope-spec operationalization is consistent with what canon does
  and does not say).
- **Status: PARTIALLY ADDRESSED** - schema-layer half closed (VL-016);
  canon-layer half open.
- **Action:**
  1. Correct schema attribution for `expected_manifest_version` and
     `expected_manifest_sha256` to make the layered provenance
     explicit (canon required properties + envelope spec
     operationalization). **DONE under VL-016** (decision 3B: both
     the canon mapping table rows and the field-by-field sections
     updated; PROVENANCE NOTE added to the section-11.9 mapping
     section).
  2. Either (a) promote the envelope spec to a status that makes
     the layered provenance explicit in canon's framing, or
     (b) amend canon section 11.9 to explicitly authorize wire-
     level caller assertion of manifest properties. Both routes
     require canon-version event under GR-1. **OPEN** - not
     currently scheduled.

- **G14** - unknown-key refusal code under-determination inside `interaction`. **PARTIALLY ADDRESSED** (VL-018): the spec rejects CCS-shaped fields with `REF_SCHEMA_RESERVED_CCS` and rejects flat-key collisions at the TOP level with `REF_SCHEMA_FLAT_KEYS`, but does not enumerate a refusal code for non-CCS-shaped unknown keys inside `interaction`. Two surface events corroborate the gap: VL-017 (test author's module docstring at `TESTS/adversarial/test_request_schema.py` lines 31-37) and VL-017b (OpenAI's Candidate 2 from the dry-run build-resumption test). VL-018's validator handles such keys provisionally with `REF_SCHEMA_TYPE_MISMATCH` as the closest extant code; the mapping is provisional because TYPE_MISMATCH's natural reading is "field type is wrong," not "field is unexpected." Spec edit pending: either add `REF_SCHEMA_UNKNOWN_KEY` or formalize the TYPE_MISMATCH overload. Separate forthcoming commit per the spec-defines-the-rename pattern (candidate GR-2).
---

## Resolved gaps

### G6 / G10 / G0-rename - disambiguation pass complete
- **Closed:** 2026-05-15 (VL-012).
- **Convention adopted:** caller-asserted fields are REMOVED if redundant
  with system-verified checks; KEPT and DOCUMENTED if load-bearing.
  Asymmetric-by-function, by design.
- **G6 outcome:** `ctx["ccs_valid"]` removed from `ccs_valid()` (renamed to
  `manifest_integrity_valid()`). The field was redundant with the
  SHA256 + version match.
- **G10 outcome:** `ctx["expected_manifest_version"]` and
  `ctx["expected_manifest_sha256"]` retained; caller-assertion semantics
  documented in the `manifest_integrity_valid()` docstring. The G10
  finding extended in scope to cover both pinning fields once full read
  of `evaluator.py` surfaced the SHA256 field as the same pattern.
- **G0-rename outcome:** function renamed; name "CCS" reserved in code
  and in test IDs. G0's substantive (canonical CCS build) portion
  remains open as the G0 build track.
- **Test surface:** four `ccs_flag_*` cases deleted; four `ccs_version_*`
  cases renamed to `manifest_version_*`; one new `manifest_sha256_missing`
  case added to preserve coverage of the SHA-missing REFUSE path.
  Net suite size: 37 -> 34.
- **Related new gap G11:** the manifest-source asymmetry in
  `evaluator.manifest_sha256()` (reads from disk, not from the manifest
  argument) was surfaced by this pass and is recorded as G11 in the
  Open gaps section.

---

## Priority order

1. **G0**  -  the anchor. Everything else is hygiene; this is the substantive finding.
2. **G7**  -  without canon-derived tests, the next G0 is invisible.
3. **G0 rename + G6 + G10**  -  RESOLVED (VL-012). See Resolved gaps.
4. **G2 + G12 + G13**  -  schema-layer work. PARTIALLY closed (VL-014 + VL-015 + VL-016: schema drafted, cross-model-verified, corrected). Full G2 closure pairs with proposed VL-017 (failing schema-shape tests), VL-018 (validator), VL-019 (PEP wiring). G12 and G13 canon-layer halves remain open pending canon-version event under GR-1.
5. **G3**  -  reframe public materials once 06 makes the FULL/PARTIAL/DRIFTED picture concrete.
6. G1, G8, G9, G11  -  bookkeeping; do in a batch. (G11 added VL-012; G2 removed from bookkeeping by VL-016 since it now has its own active track at item 4.)
7. **G4, G5**  -  build-outward scope, after the base is honest.
