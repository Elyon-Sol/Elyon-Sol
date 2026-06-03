# Elyon-Sol Restructure Package  -  Read Me First (Rev. 2)

This package is the first deliverable of the restructure: the **organized, honest base**
the project builds outward from. Eleven reviewable artifacts, not prose to be edited again.

Premise carried throughout: **canon is locked.** Everything here is derivation from it.
The repository  -  not any model  -  is the continuity layer.

**Rev. 2** incorporates the v0.9.8.4 canonical whitepaper, `manifest.json`, and the real
`test_pep.py`. This materially changed the assessment  -  see "What the canon changed" below.

## The eleven artifacts

1. **`01_repository_structure.md`**  -  proposed directory layout. Canon as locked fixed
   point; everything else derivation.
2. **`02_honest_core_description.md`**  -  description derived strictly from `evaluator.py`
   and `pep.py`. (Holds at Rev. 1; the canon confirms rather than contradicts it.)
3. **`03_vocabulary_ledger.md`**  -  every term mapped to a code construct. KEEP / DEFINE /
   CUT. (Holds at Rev. 1.)
4. **`04_current_vs_claimed.md` (Rev. 2)**  -  now anchored by **G0**, the CCS
   spec/implementation drift. G1 corrected (Rev. 1 overstated it). All rows re-grounded
   against the canon.
5. **`05_admissibility_envelope_spec.md` (Rev. 2)**  -  reframed: the envelope is **the
   implementation of canonical CCS** (whitepaper section 12-section 13), not a new feature. Every field
   justified by a canon clause.
6. **`06_spec_to_code_traceability.md` (new)**  -  every whitepaper section mapped to its
   code construct with a fidelity status (FULL / PARTIAL / DRIFTED / UNIMPLEMENTED). The
   artifact that prevents the next G0.

7. **`07_continuity_recursion.md` (new)**  -  reading-aid naming the recursive
   continuity-discipline pattern visible at five layers of the framework
   (decision, manifest, methodology, session, evaluator-versioning), with
   the request-layer non-fit, layer A/B/C bounding per VL-024, and direct
   citation of the post-VL-029 envelope.py + pep.py implementation. No new
   invariant, claim, or vocabulary; reading-aid track only.
8. **`08_enforcement_design.md` (new)**  -  design analysis (reading-aid / design
   track, paralleling 07) for gap G4 non-bypassable enforcement: a threat model, the
   adversary classes derived by construction, the envelope-delivery mechanism, and the
   G4/G5 boundary. Designed at VL-036; built outward at VL-037/VL-038.
9. **`09_key_record_spec.md` (new)**  -  spec for the published signed key record
   (B-prime-2): issuer-key revocation, rotation-representation, and the publisher/root
   trust floor. Spec-defines-the-change; built at VL-042 (opt-in).
10. **`10_readiness_spec.md` (new)**  -  spec for the WIRING-track readiness gate
   (T-readiness): a machine-checked, fail-closed deployment-readiness instrument
   tracking built / wired / exercised / transported. A governance instrument, not a
   capability; built at VL-043 (0 of 3 predicates green by design).
11. **`11_root_record_spec.md` (new)**  -  spec for root succession and per-root status
   (B-prime-3): planned root rotation, retired/revoked status, and the bootstrap floor.
   Spec-defines-the-change; built at VL-044 (opt-in, build-then-wire).

## What the canon changed

Before the whitepaper, I assessed Elyon-Sol as a small validator wrapped in oversized
language. **That was wrong, and it is retracted.** The canon is a legitimate formal
specification  -  formal interaction model, set-theoretic invariant definitions, explicit
scope, and a correct "Relation to Prior Work" section situating it against RBAC/ABAC/
XACML/UCON/reference-monitor.

The accurate finding is narrower and more useful: **the implementation faithfully realizes
two of three canonical invariants (AC^3, T^26) and the manifest layer, but the third
invariant  -  CCS  -  has drifted.** Whitepaper section 12 defines CCS as a temporal invariant over
state transitions; the implemented `ccs_valid()` is a point-in-time manifest-integrity
check. The shared name masked the gap. That is G0, and it is the substantive result of
this whole review.

The good news in that finding: the gap is specific, nameable, and buildable  -  and the
admissibility envelope you independently reached for **is** the construct that closes it.

## How to review this

- Check each artifact against the actual repo and the whitepaper. Structure, description,
  ledger, gaps, envelope spec, traceability map  -  all are falsifiable against
  `evaluator.py`, `pep.py`, `manifest.json`, `test_pep.py`, and the v0.9.8.4 canon.
- This is the cross-model surface working as intended: concrete artifacts you, Grok, and
  the code can each check. Pass the *artifacts*, never the verdicts.
- Nothing here closes a gap by editing prose. Gaps in artifact 04 close only when code,
  tests, or structure change.

## What comes after sign-off

Two tracks, deliberately separate:

- **Honest base**  -  execute artifacts 01-04 and 06: restructure the repo, replace the
  README, apply the ledger, open `EVIDENCE/STATE.md`, archive stale proofs, stand up the
  traceability map, rename the mis-named `ccs_valid` constructs. This makes the project
  technically sound and accurately described  -  the stated objective.
- **Build outward**  -  execute artifact 05: implement canonical CCS via the envelope, with
  canon-derived tests. Then the threads that let "governance" stay an earned word
  (non-bypassable enforcement, durable external proofs, PoE).

The order matters. A faithful partial implementation of a real specification can grow into
a full one. An implementation that misrepresents which invariants it has built can only be
corrected.
