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
| section 2 Evaluation pipeline | AC^3 -> T^26 -> CCS -> ELIGIBLE/REFUSE | `evaluate()` ordering | **PARTIAL** | Pipeline order is correct; the third stage in code is `manifest_integrity_valid()` (section 8.1 work, not section 12 CCS). Canonical CCS is UNIMPLEMENTED (G0 build half). |
| section 3 AC^3  -  Authority | "all required authority present, identifiable, properly scoped" | `ac3_valid()` | **FULL** | `AP_set >= AR_set` with string-list type validation. Matches section 11.7. |
| section 3 T^26  -  Coverage | "all required participants, roles, evidence present" | `t26_valid()` | **FULL** | `OP_set >= R_set` with type validation. Matches section 11.8. |
| section 3 CCS  -  Continuity | "identity, structure, semantics consistent across transitions" |  -  | **UNIMPLEMENTED** | **G0 (build half).** Canonical CCS is a transition invariant (section 12). No code implements it. The G0 build track (envelope, Deliverable 05) is scoped to implement it. The rename half of G0 was closed in VL-012: the function formerly mis-named `ccs_valid` no longer occupies this row. |
| section 3 Evaluation Rule | "failure of any invariant -> immediate refusal" | `evaluate()` short-circuit returns | **FULL** | Each failed check returns `REFUSE` immediately. |
| section 4 / section 15 Failure constructs | CDD, SAP, PAD, ILT  -  detection-layer descriptions |  -  | **UNIMPLEMENTED** | **Not a gap.** Canon explicitly states these "do not participate in admissibility determination." Implementation is optional/future. |
| section 6 Lightweight formal model | `evaluate(ctx)` reference pseudocode | `evaluate()` | **PARTIAL** | Matches the pseudocode shape, including the post-VL-012 rename to `manifest_integrity_valid()`. Remains PARTIAL because the pseudocode names `ccs_valid(ctx)` as the third check, while `evaluate()` now calls `manifest_integrity_valid()` plus the section 12 canonical CCS check is UNIMPLEMENTED. |
| section 7 Regulatory alignment | EU AI Act Articles 5/9/10/14 support claims |  -  | **N/A  -  SPEC ONLY** | Positioning claim, not an implementable construct. Should be stated as "can support," not "provides." |
| section 8.1 Manifest-bound authority | governance bound to a deterministic manifest | `load_manifest()`, `safe_manifest()`, `manifest_sha256()`, `manifest_integrity_valid()` | **FULL** | This is, accurately, what the formerly-named `ccs_valid()` was doing  -  it belongs here, not under section 12. VL-012 renamed it to `manifest_integrity_valid()` and made this attribution explicit in code. |
| section 8.2 Proof-of-Existence (PoE) | optional artifact-integrity anchoring |  -  | **UNIMPLEMENTED** | Canon marks it "optional" and "implementation-dependent." Not a gap. Candidate build-outward item. |
| section 8.4 GAE/ARL patterns | non-canonical implementation patterns |  -  | **N/A  -  SPEC ONLY** | Canon marks them non-canonical, introducing no new criteria. |
| section 9 Reproducibility | deterministic derivation, identical results, fail-closed | `evaluate()` determinism; `safe_*` guards | **FULL** | No randomness/state/time in the gate; all invalid inputs fail closed. |
| section 10 Limitations | explicit non-goals | scope text | **N/A  -  SPEC ONLY** | Honest scope statement; the implementation respects it. |
| section 11.1 Interaction model | `I = (A, S, C, t)` | `ctx` dict | **PARTIAL** | `ctx` carries A/C-equivalents; it has **no `S` (system state) or `t` (time)** representation. This absence is the structural root of the section 12 drift. |
| section 11.7 AC^3 definition | `AC^3(I)=1 <=> AP(I) superset-or-equal AR(I)` | `ac3_valid()` | **FULL** | Exact match. |
| section 11.8 T^26 definition | `T^26(I)=1 <=> OP(I) superset-or-equal R(I)` | `t26_valid()` | **FULL** | Exact match. |
| section 11.9 Governing manifest | `M: I -> (AR(I), R(I))`; deterministic, versioned, integrity-verifiable | `manifest.json` + `safe_manifest()` + `manifest_sha256()` | **FULL** | Manifest has `version`, `AR`, `R`; hash-verifiable. Matches. |
| section 12.1 State transition | transition on any change in context/authority/coverage/state |  -  | **UNIMPLEMENTED** | No transition concept in code. Envelope (Deliverable 05) is the planned implementation. |
| section 12.2 Decision variables | `u = AC^3`, `c = T^26`, `d = u AND c` | `evaluate()` computes the conjunction | **PARTIAL** | `d` is computed per-call but never *stored* for cross-transition comparison. |
| section 12.3 Continuity constraint | transitions justified; `d_{t+1} = u_{t+1} AND c_{t+1}` |  -  | **UNIMPLEMENTED** | **G0 core.** Requires the envelope's `condition_results` + `reassert()`. |
| section 12.4 Failure condition | invalid transition -> `CCS = 0` |  -  | **UNIMPLEMENTED** | Envelope `reassert()` -> `INVALIDATED` / `RE-EVALUATE-REQUIRED` is the planned mechanism. |
| section 13 Evaluation function | `G(I) = AC^3 AND T^26 AND CCS`; eligibility not durable | `evaluate()` returns the conjunction | **PARTIAL** | The conjunction is implemented; the CCS operand is UNIMPLEMENTED (G0 build half), and "eligibility not durable" (revalidation) is UNIMPLEMENTED. |
| section 14 Scope clarification | pre-execution, identity-agnostic, non-executing | `pep.py` runs `evaluate()` before forward | **PARTIAL** | Pre-execution: yes, *for routed calls* (bypassability  -  G4). Non-executing: yes. Identity-agnostic: yes. |
| Appendix D.2 Positive case | worked ELIGIBLE example | `test_pep.py::test_governed_call_eligible_forwards_once` | **FULL** | The canon's positive case has a corresponding passing test. |
| Appendix D.3 CCS-isolated failure | ELIGIBLE on AC^3+T^26 but `CCS=0` -> REFUSE |  -  | **UNIMPLEMENTED** | **Telling gap.** The canon has a worked CCS-isolated failure case. No test exercises it, because the code cannot produce a CCS-isolated failure in the section 12 sense. This is G0 visible from the canon's own examples. |

---

## Summary by status

- **FULL (8):** section 3 AC^3, section 3 T^26, section 3 Evaluation Rule, section 8.1, section 9, section 11.7, section 11.8, section 11.9, Appendix D.2.
  Authority and Coverage are completely and faithfully implemented. Manifest binding is solid.
- **PARTIAL (6):** section 2, section 6, section 11.1, section 12.2, section 13, section 14. Mostly the pipeline and the formal model  - 
  partial *because* they contain CCS or state/time as an operand.
- **DRIFTED (0):** The rename half of G0 was closed in VL-012; the section 3 CCS row that was DRIFTED is now UNIMPLEMENTED (build half of G0). No remaining DRIFTED rows.
- **UNIMPLEMENTED (7):** section 3 CCS (G0 build half), section 12.1, section 12.3, section 12.4, Appendix D.3 (all CCS-transition logic  -  the
  envelope's scope); section 8.2 PoE and section 4/section 15 failure constructs (canon marks both optional /
  non-participating  -  *not* gaps).
- **N/A  -  SPEC ONLY (3):** section 7, section 8.4, section 10.

**Read of the whole picture:** Two of three canonical invariants (AC^3, T^26) are FULL. The
manifest layer is FULL. CCS is UNIMPLEMENTED in its canonical (transition-invariant) sense; the
dependent sections (12.1, 12.3, 12.4, Appendix D.3) follow. The envelope (Deliverable 05) is
scoped to close exactly that cluster, and the G0 build track is the active work. Post-VL-012,
the project no longer mis-attributes the manifest-integrity check to CCS; the gap is now
honestly named as a missing invariant rather than a misnamed one. This is a faithful
partial implementation of a real specification, with one well-defined missing invariant. That
is an accurate, declarable description of the project.

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
