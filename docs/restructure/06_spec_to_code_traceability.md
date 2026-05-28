# Elyon-Sol  -  Spec-to-Code Traceability Map

**Purpose:** Map every section of the v0.9.8.4 canonical whitepaper to the code construct
that implements it, with an explicit fidelity status. This is the artifact that prevents
the next G0  -  the next silent drift between specification and implementation.

**Fidelity status legend:**
- **FULL**  -  code implements the canon section completely and faithfully.
- **PARTIAL**  -  code implements some of the section; named sub-parts remain.
- **DRIFTED**  -  code claims to implement it but implements a different thing (the G0 class).
- **UNIMPLEMENTED**  -  canon defines it; no code implements it. (Not always a gap  -  see notes.)
- **N/A  -  SPEC ONLY**  -  canon section is definitional/scope text; no implementation expected.

**Verified against:** `evaluator.py`, `pep.py`, `manifest.json`, `test_pep.py`, whitepaper
v0.9.8.4. Sections not listed are narrative (Abstract, section 1, section 5) with no implementable content.

---

## Traceability table

| Whitepaper section | What it specifies | Code construct | Status | Notes |
|---|---|---|---|---|
| section 2 Evaluation pipeline | AC^3 -> T^26 -> CCS -> ELIGIBLE/REFUSE | `evaluate()` ordering + `pep.py` envelope construction | **PARTIAL** | Pipeline order is correct; the third stage inside `evaluate()` is `manifest_integrity_valid()` (section 8.1 work). Canonical CCS (section 12) is implemented at the envelope layer downstream of `evaluate()`: `pep.py` calls `build_envelope()` after evaluate()-returned-ELIGIBLE, and `reassert()` performs the section 12 transition check. PARTIAL because canonical CCS is not in the in-evaluate() chain itself, only in the envelope-construction-and-reassertion path. |
| section 3 AC^3  -  Authority | "all required authority present, identifiable, properly scoped" | `ac3_valid()` | **FULL** | `AP_set >= AR_set` with string-list type validation. Matches section 11.7. |
| section 3 T^26  -  Coverage | "all required participants, roles, evidence present" | `t26_valid()` | **FULL** | `OP_set >= R_set` with type validation. Matches section 11.8. |
| section 3 CCS  -  Continuity | "identity, structure, semantics consistent across transitions" | `envelope.build_envelope()` + `envelope.reassert()` | **FULL** | **G0 build half closed at VL-029.** Canonical CCS is implemented at the envelope layer: `build_envelope()` records the system state (canon, manifest, evaluator hashes + decision + condition_results) at decision time; `reassert()` detects section-12.1 transitions via hash comparison and returns `{outcome, ccs}` per the post-VL-026 derivation rule (REASSERTED with ccs=True iff continuity holds; INVALIDATED or RE-EVALUATE-REQUIRED with ccs=False on any violation per section 12.4). The rename half of G0 was closed in VL-012; the build half closes here. |
| section 3 Evaluation Rule | "failure of any invariant -> immediate refusal" | `evaluate()` short-circuit returns | **FULL** | Each failed check returns `REFUSE` immediately. |
| section 4 / section 15 Failure constructs | CDD, SAP, PAD, ILT  -  detection-layer descriptions |  -  | **UNIMPLEMENTED** | **Not a gap.** Canon explicitly states these "do not participate in admissibility determination." Implementation is optional/future. |
| section 6 Lightweight formal model | `evaluate(ctx)` reference pseudocode | `evaluate()` | **PARTIAL** | Matches the pseudocode shape, including the post-VL-012 rename to `manifest_integrity_valid()`. Remains PARTIAL because the canon's pseudocode names `ccs_valid(ctx)` as the third check inside `evaluate()`, while the post-VL-029 architecture has canonical CCS at the envelope layer (`envelope.reassert()`) rather than inside `evaluate()` itself; the canonical invariant is implemented but not at the structural position the section 6 pseudocode names. |
| section 7 Regulatory alignment | EU AI Act Articles 5/9/10/14 support claims |  -  | **N/A  -  SPEC ONLY** | Positioning claim, not an implementable construct. Should be stated as "can support," not "provides." |
| section 8.1 Manifest-bound authority | governance bound to a deterministic manifest | `load_manifest()`, `safe_manifest()`, `manifest_sha256()`, `manifest_integrity_valid()` | **FULL** | This is, accurately, what the formerly-named `ccs_valid()` was doing  -  it belongs here, not under section 12. VL-012 renamed it to `manifest_integrity_valid()` and made this attribution explicit in code. |
| section 8.2 Proof-of-Existence (PoE) | optional artifact-integrity anchoring |  -  | **UNIMPLEMENTED** | Canon marks it "optional" and "implementation-dependent." Not a gap. Candidate build-outward item. |
| section 8.4 GAE/ARL patterns | non-canonical implementation patterns |  -  | **N/A  -  SPEC ONLY** | Canon marks them non-canonical, introducing no new criteria. |
| section 9 Reproducibility | deterministic derivation, identical results, fail-closed | `evaluate()` determinism; `safe_*` guards | **FULL** | No randomness/state/time in the gate; all invalid inputs fail closed. |
| section 10 Limitations | explicit non-goals | scope text | **N/A  -  SPEC ONLY** | Honest scope statement; the implementation respects it. |
| section 11.1 Interaction model | `I = (A, S, C, t)` | `ctx` dict | **PARTIAL** | `ctx` carries A/C-equivalents; it has **no `S` (system state) or `t` (time)** representation. This absence is the structural root of the section 12 drift. |
| section 11.7 AC^3 definition | `AC^3(I)=1 <=> AP(I) superset-or-equal AR(I)` | `ac3_valid()` | **FULL** | Exact match. Canon-derived coverage: `test_evaluator_canonical.py` `test_ac3_*` (VL-034, cites canon 11.7). |
| section 11.8 T^26 definition | `T^26(I)=1 <=> OP(I) superset-or-equal R(I)` | `t26_valid()` | **FULL** | Exact match. Canon-derived coverage: `test_evaluator_canonical.py` `test_t26_*` (VL-034, cites canon 11.8). |
| section 11.9 Governing manifest | `M: I -> (AR(I), R(I))`; deterministic, versioned, integrity-verifiable | `manifest.json` + `safe_manifest()` + `manifest_sha256()` | **FULL** | Manifest has `version`, `AR`, `R`; hash-verifiable. Matches. Canon-derived coverage: `test_evaluator_canonical.py` `test_manifest_*` (VL-034, cites canon 11.9 via artifact-05-layer per Decision C). |
| section 12.1 State transition | transition on any change in context/authority/coverage/state | `envelope.reassert()` hash-mismatch detection | **FULL** | The envelope pins the system-state-defining hashes (canon, manifest, evaluator); `reassert()` detects a section-12.1 transition as any change in those hashes between issuance and reassertion. Each of Rows 1-4 of the reassertion-protocol table corresponds to a class of transition; canon-derived test `test_canon_12_1_state_transition_detected_via_hash_change` (VL-028) exercises Row 1 explicitly. |
| section 12.2 Decision variables | `u = AC^3`, `c = T^26`, `d = u AND c` | `evaluate()` computes the conjunction; `build_envelope()` stores u, c, d in `condition_results` | **FULL** | Post-VL-029, the envelope's `condition_results` block stores `ac3` (u), `t26` (c), and the implicit d via the envelope's `decision` field. At reassertion, the stored values are available for cross-transition comparison: `reassert()` re-derives ccs (d-consistency per section 12.3) and returns True iff the stored decision is still valid against the live state. |
| section 12.3 Continuity constraint | transitions justified; `d_{t+1} = u_{t+1} AND c_{t+1}` | `envelope.reassert()` Row 5 + ccs-derivation rule | **FULL** | **G0 core, closed at VL-029.** `reassert()` Row 5 returns REASSERTED iff all hashes match and decision_sha256 verifies, with ccs=True (canon's `d_{t+1} = u_{t+1} AND c_{t+1}` provably holds because the stored decision is still derivable from the unchanged state). The post-VL-026 forward-looking ccs-derivation rule was implemented in envelope.py at VL-029 per Decision A. Canon-derived test `test_canon_13_eligibility_does_not_persist` (VL-028) exercises Row 5; xfail-removed test `test_canon_12_3_ccs_derived_true_on_REASSERTED` (VL-029) exercises the ccs-derivation. |
| section 12.4 Failure condition | invalid transition -> `CCS = 0` | `envelope.reassert()` Rows 1-4 + ccs-derivation rule | **FULL** | `reassert()` Rows 1-4 each fire on a class of section-12.4 invalid transition (canon-change/tamper/evaluator-change/manifest-change), returning INVALIDATED or RE-EVALUATE-REQUIRED with ccs=False per the post-VL-026 derivation rule (canon's "if any condition is violated: CCS = 0"). Canon-derived tests `test_canon_12_4_evaluator_change_invalidates_continuity` and `test_canon_11_9_manifest_change_invalidates_continuity` (VL-028) exercise Rows 3-4; xfail-removed tests `test_canon_12_4_ccs_derived_false_on_INVALIDATED` and `test_canon_12_4_ccs_derived_false_on_RE_EVALUATE_REQUIRED` (VL-029) exercise the ccs-derivation. |
| section 13 Evaluation function | `G(I) = AC^3 AND T^26 AND CCS`; eligibility not durable | `evaluate()` + `build_envelope()` + `reassert()` together | **FULL** | Per R-trajectory reading: the canon's `G(I) = AC^3 AND T^26 AND CCS` is realized across the post-VL-029 pipeline: `evaluate()` computes AC^3 AND T^26 AND manifest-integrity; `build_envelope()` records the state; `reassert()` checks CCS on revalidation. "Eligibility not durable" is operationalized by `reassert()`'s contract that REASSERTED is the only state in which a past ELIGIBLE may be honored without re-evaluation. |
| section 14 Scope clarification | pre-execution, identity-agnostic, non-executing | `pep.py` runs `evaluate()` before forward | **PARTIAL** | Pre-execution: yes, *for routed calls* (bypassability  -  G4). Non-executing: yes. Identity-agnostic: yes. |
| Appendix D.2 Positive case | worked ELIGIBLE example | `test_pep.py::test_governed_call_eligible_forwards_once` | **FULL** | The canon's positive case has a corresponding passing test. |
| Appendix D.3 CCS-isolated failure | ELIGIBLE on AC^3+T^26 but `CCS=0` -> REFUSE |  -  | **UNIMPLEMENTED** | The canon's worked example describes an in-evaluate CCS-isolated failure (AC^3=1, T^26=1, CCS=0 -> REFUSE). Post-VL-029, CCS is implemented at the envelope layer (downstream of `evaluate()`), so the literal D.3 case cannot occur on first issuance: a fresh envelope records ccs=None (section 12.3 is inapplicable on first issuance). The CCS-isolated failure DOES occur at reassertion (`reassert()` -> INVALIDATED/RE-EVALUATE-REQUIRED with ccs=False), but that is the section-12.4 failure path, not the section 6 pseudocode's in-evaluate D.3 case. Remains UNIMPLEMENTED in D.3's strict reading; a refactor that pulls CCS into the in-evaluate pipeline (or refuses-on-reassert-failure at pep.py) would close it. |

---

## Summary by status

- **FULL (15):** section 3 AC^3, section 3 T^26, section 3 CCS, section 3 Evaluation Rule, section 8.1, section 9, section 11.7, section 11.8, section 11.9, section 12.1, section 12.2, section 12.3, section 12.4, section 13, Appendix D.2.
  All three canonical invariants (AC^3, T^26, CCS) are FULL post-VL-029. Authority, Coverage, and Continuity are completely and faithfully implemented; the manifest layer is solid; the section 12 transition cluster (12.1, 12.2, 12.3, 12.4) and section 13 (the top-level evaluation function) closed at VL-029 via the envelope layer (`envelope.build_envelope()` + `envelope.reassert()`). The previously-listed FULL count was 8 but listed 9 sections; the post-VL-029 count of 15 is verified against the table.
- **PARTIAL (4):** section 2, section 6, section 11.1, section 14. The pipeline (section 2) and the formal model (section 6) remain PARTIAL because canonical CCS is implemented at the envelope layer rather than inside `evaluate()` itself, which is the structural position the canon's pseudocode names. section 11.1 (the interaction tuple) remains PARTIAL because `ctx` carries no `S` (system state) or `t` (time) representation. section 14 (scope clarification) remains PARTIAL because pre-execution enforcement is non-bypassable only for routed calls (G4).
- **DRIFTED (0):** The rename half of G0 was closed in VL-012; the build half closed in VL-029. The section 3 CCS row that was DRIFTED (until VL-012) and then UNIMPLEMENTED (until VL-029) is now FULL. No remaining DRIFTED rows.
- **UNIMPLEMENTED (3):** Appendix D.3 (CCS-isolated failure case, post-VL-029 only at reassertion, not in-evaluate per D.3's strict reading); section 8.2 PoE; section 4/section 15 failure constructs. Canon marks 8.2 and 4/15 "optional" / "non-participating" - *not* gaps. The CCS-transition cluster (section 12.1, section 12.3, section 12.4) that was UNIMPLEMENTED pre-VL-029 is now FULL via the envelope layer.
- **N/A  -  SPEC ONLY (3):** section 7, section 8.4, section 10.

**Read of the whole picture:** All three canonical invariants (AC^3, T^26, CCS) are FULL
post-VL-029. The manifest layer is FULL. The section 12 transition cluster (12.1, 12.3, 12.4)
is FULL via the envelope's `build_envelope()` + `reassert()` pair. The remaining UNIMPLEMENTED
rows are: Appendix D.3 (a structural-position question - canonical CCS is at the envelope
layer, not in-evaluate as D.3's strict reading would require; close-out path is a refactor or
an envelope-on-refuse extension), section 8.2 PoE (canon marks optional), and section 4/section 15
failure constructs (canon marks non-participating). The remaining PARTIAL rows are pipeline-
and-formal-model commentary (section 2, section 6 - canonical CCS is at envelope layer, not
at the structural position the canon's pseudocode names), the interaction tuple's missing
`S`/`t` representation (section 11.1), and bypassability (section 14 / G4). Post-VL-012, the
project no longer mis-attributes manifest-integrity to CCS; post-VL-029, canonical CCS is
deterministic in code, exercised on every ELIGIBLE response, and verifiable via canon-derived
tests at TESTS/adversarial/test_ccs_canonical.py. This is a faithful complete implementation of
the three canonical invariants of a real specification, with one structural-position question
(D.3) and three categories of build-outward / annotation-layer items remaining. That is an
accurate, declarable description of the project.

---

## How this map is maintained

1. **Every new code construct** gets a row here citing the whitepaper section it derives from,
   before it is considered done.
2. **Every status change** is a reviewable event  -  `DRIFTED -> PARTIAL -> FULL` as the envelope
   work lands.
3. **Canon-derived tests (gap G7)** reference this map: a test for section 12.3 cites the row, and
   the row cites the test. Spec <-> map <-> test <-> code form a closed loop.
4. This map is the standing answer to "is the implementation honest about the canon?"  -  it is
   checkable by you, by Grok, by Claude next session, against the whitepaper and the code.
