# Elyon-Sol - Project State

**This file is the entry point. A fresh session - the author, a new Claude
session, Grok, or any collaborator - should read this file first.**

**Session start/end:** see `docs/SESSION_PROTOCOL.md` for the resume and close protocols.
**Governance rules:** see `docs/MAINTENANCE_PROTOCOL.md` for the rules under which the repository is allowed to change (GR-N entries).

Last updated: 2026-05-17 (commit: see `git log` for STATE.md; SPEC/request_schema.md committed in d7eddd5; VL-014 entry appended in the corrective commit alongside this update; last ledger entry VL-014; next action is G2 schema-shape tests, proposed VL-015)

---

## How to use this repository as continuity

This repository is the continuity layer. It does not depend on any model's
memory. To orient in a fresh session, read in this order:

1. **`git log --oneline`** - what has happened, in order.
2. **`EVIDENCE/verification_ledger.md`** - how each claim about the project
   became trusted. This is the highest-order evidence: the record of what has
   been independently verified, by whom, against what sources.
3. **`docs/restructure/`** - the Rev. 2 restructure package: the reasoning
   behind the current structure, the gap analysis, the envelope spec, and the
   spec-to-code traceability map. Artifact 01 (`01_repository_structure.md`)
   is the reconciled diff against the real repository tree; artifact 04
   (`04_current_vs_claimed.md`) is the living gap document.
4. **This file's "Next open action" section** - the ordered starting point.

Pass *artifacts*, never *verdicts*. A rating or an approval is not evidence;
a derivation from primary sources (canon, code) is.

---

## What Elyon-Sol is

Elyon-Sol is a deterministic, fail-closed HTTP admission gate, derived from a
formal specification (the v0.9.8.4 canonical whitepaper). Given a request and
a SHA256-pinned manifest, it returns ELIGIBLE only if the caller's authority
set and operation set each satisfy the manifest's required sets and the
manifest hash and version match; otherwise REFUSE. On ELIGIBLE the request is
forwarded to the target; on REFUSE or any exception the target is not called.

The canon defines three invariants: Authority (AC^3), Coverage (T^26), and
Continuity (CCS). The implementation faithfully realizes AC^3 and T^26 and the
manifest layer. CCS has drifted - see G0 below.

---

## Current verified state

- **Canon locked.** v0.9.8.4 is locked: `CANON/canon_v0.9.8.4.pdf` (immutable
  source of record), `CANON/canon.md` (ASCII-safe transcription, verified
  against the PDF - see ledger VL-006), `CANON/canon.lock` (sha256 of canon.md).
- **Verification ledger established.** `EVIDENCE/verification_ledger.md`,
  entries VL-001 through VL-014.
- **G0 confirmed (anchor finding).** Canonical CCS (whitepaper sections 12-13)
  is a temporal invariant over state transitions; the implemented `ccs_valid()`
  is a point-in-time manifest-integrity check. They are not the same invariant.
  Confirmed by three independent derivations from primary sources: Claude,
  Grok (clean pass), and OpenAI (ledger VL-002, VL-008).
- **Method on record.** `scripts/establish_ledger.sh`, `scripts/lock_canon.sh`,
  `scripts/append_vl008.sh`, `scripts/append_vl009.sh`, and
  `scripts/append_vl010.sh` - the scripts that built the ledger, the lock, and
  the VL-008/VL-009/VL-010 entries - are committed.
- **Cross-model verification procedure established (VL-008).** A valid
  verification requires the task scoped to primary sources and confirmation the
  response stayed within that scope. A model's prior exposure to the project
  does not disqualify it, provided those hold. Two failed and one successful
  OpenAI attempt are documented in VL-008.
- **Rev. 2 restructure package committed.** The seven planning artifacts
  (`00_README.md` through `06_spec_to_code_traceability.md`) are in
  `docs/restructure/`. The ASCII-safe standard (VL-006) has been applied
  repo-wide (VL-009). Artifact 01 has been revised to reconcile against the
  real repository tree; artifact 04 has been updated through G11 (VL-012
  session: G0 partially resolved, G6 and G10 resolved, G11 added).
  Artifacts 05 and 06 brought current to VL-012 in the VL-013 freshness
  pass.
- **MANIFEST/manifest.json committed (VL-010).** Previously hidden by a
  `.gitignore` rule inherited from a Python-project template. Both the
  manifest and the `.gitignore` correction landed at commit c0867a6;
  corrective ledger entry VL-010. VL-003's derivation is now reproducible
  from a fresh clone.
- **EVIDENCE/ reorganized (VL-011).** Six proof-style files split into
  `EVIDENCE/proofs/` (three current proofs plus the raw pytest log
  backing the AC^3 mutation experiment) and `EVIDENCE/archive/` (two
  interception proofs of the dead flat-key API, plus the truncated
  stability proof). Each archived file carries a prepended NON-CURRENT
  header citing the gaps that retired it (G2/G5/G9). `EVIDENCE/tmp/`
  removed. `EVIDENCE/verification_ledger.md` is unchanged at
  `EVIDENCE/` root. The honest-base track is now complete.
- **G0/G6/G10 disambiguation pass complete (VL-012, commit 8ba88cf).**
  Function `ccs_valid()` renamed to `manifest_integrity_valid()`; the
  redundant caller-asserted `ctx["ccs_valid"]` input removed; the load-
  bearing pinning fields (`expected_manifest_version`,
  `expected_manifest_sha256`) retained and their caller-assertion
  semantics documented in the function docstring. The name "CCS" is
  reserved in code and in test IDs until envelope.py implements
  section 12. Test surface: four `ccs_flag_*` cases deleted; one new
  `manifest_sha256_missing` added to preserve coverage; four
  `ccs_version_*` renamed to `manifest_version_*`. Suite size: 37 -> 34.
  EVIDENCE/proofs/manifest_integrity_continuity_001.md renamed to
  manifest_integrity_001.md and body rewritten. New gap G11 surfaced
  (manifest-source asymmetry: `manifest_sha256()` reads from disk,
  ignoring the manifest argument). The hash citation in the VL-012
  ledger entry was corrected from the pre-amend hash to the actual
  commit hash in follow-up commit f0df14c; process finding on
  self-referencing-hash workflow recorded there.
- **Planning artifacts 05 and 06 brought current to VL-012 (VL-013,
  commit 606ddc1).** Forward-tense references to `ccs_valid()` in
  `docs/restructure/05_admissibility_envelope_spec.md` updated to
  past tense citing VL-012. In
  `docs/restructure/06_spec_to_code_traceability.md`, canonical CCS
  reclassified from DRIFTED (one row, the function in the wrong slot)
  to UNIMPLEMENTED (no code implements it; the rename half of G0
  closed in VL-012; the build half is the G0 build track). DRIFTED
  count: 1 -> 0. UNIMPLEMENTED count: 6 -> 7. The artifacts'
  substantive content was preserved; only statements about current
  state that became false after VL-012 were touched. No code, canon,
  manifest, or test change.
- **SPEC/request_schema.md committed (d7eddd5; VL-014 follow-up).**
  First artifact of the G0 build track. Canon-derived from sections
  11, 12, 13. Locks the on-the-wire request shape; maps the
  canonical interaction tuple I = (A, S, C, t) and the caller-supplied
  sets AP, OP to wire fields; names AR(I) and R(I) as manifest-derived
  (not caller-supplied); documents the load-bearing caller-asserted
  manifest-pinning fields per VL-012's convention; reserves "CCS" and
  defines a refusal rule for caller attempts to assert it
  (REF_SCHEMA_RESERVED_CCS); names the flat-key payload from
  EVIDENCE/archive/interception_* as REFUSED (REF_SCHEMA_FLAT_KEYS,
  the schema-layer half of G2). Status SINGLE-SOURCE; transitions to
  CONFIRMED on independent re-derivation from canon + envelope spec
  per VL-008 procedure. The schema file landed in d7eddd5 ahead of
  the VL-014 ledger entry due to a chat-pasted-block collision at
  session close; the corrective commit (this STATE.md update + the
  VL-014 entry) repairs the split. Schema-work build order proposed
  in the artifact: VL-015 (failing schema-shape tests), VL-016
  (request validator), VL-017 (PEP wiring + G2 close in code),
  VL-018 (artifact 05 freshness pass to absorb `context` and
  `target_url`).

## What is locked vs. open

- **Locked:** canon v0.9.8.4. Corrected only by version increment, never by
  in-place edit (governance rule GR-1, ledger VL-007).
- **Open:** the honest-base track is complete, the disambiguation pass
  (G0/G6/G10) is complete, and the G0 build track is underway with
  the first artifact (SPEC/request_schema.md, VL-014) committed.
  Known items recorded but not yet scheduled:
    - VL-009 ASCII-safe standard is violated by pre-existing content
      in the three `EVIDENCE/archive/` files (VL-011 process finding);
      resolution deferred to a follow-up decision (normalize / preserve
      verbatim / repo-wide pass).
    - G11 (manifest-source asymmetry in `manifest_sha256()`) is queued
      with G1, G2, G8, G9 in the bookkeeping batch per artifact 04's
      priority order.
    - Latent VL-009 inconsistency: `IMPLEMENTATION/replay/receipt.py`'s
      `canonical_json` uses `ensure_ascii=False` (VL-012 process
      finding); not a current problem (no receipt currently contains
      non-ASCII bytes) but warrants documentation if scope-creep into
      a follow-up is desired.

---

## Next open action

Continue the **G0 build track** via the schema-work sub-order
proposed in `SPEC/request_schema.md` under "Build order
(schema-internal)". The schema itself is done (d7eddd5, VL-014); the
remaining steps close G2 in code and reconcile the envelope spec.

The honest-base track is complete; the disambiguation pass is complete;
the G0 build track is underway:

1. **Artifact 01 reconciled against HEAD.** Done (commit 148e725).
2. **Maintenance protocol artifact added with GR-1.** Done (commit 6f7f0e7).
3. **MANIFEST/manifest.json committed** (sub-thread surfaced during step 1).
   Done (VL-010, commit c0867a6).
4. **EVIDENCE/ reorganized into proofs/ and archive/.** Done
   (VL-011, commit e6345a5).
5. **G0/G6/G10 disambiguation pass.** Done (VL-012, commit 8ba88cf;
   hash citation corrected in f0df14c).
6. **Planning artifacts 05 and 06 brought current to VL-012.** Done
   (VL-013, commit 606ddc1).
7. **SPEC/request_schema.md drafted.** Done (d7eddd5, VL-014; this
   STATE.md update and the VL-014 ledger entry land in the
   corrective commit alongside).

Priority order for the G0 build track is in
`docs/restructure/04_current_vs_claimed.md` under "Priority order."
With priority item 3 (G0 rename + G6 + G10) resolved and item
4-start (SPEC/request_schema.md) committed, the remaining order is:
G2 code-close (failing tests then validator then PEP wiring; proposed
VL-015/VL-016/VL-017), then G0 build (canonical CCS via envelope),
G7 (canon-derived tests), G3 (reframe public materials once 06 makes
the FULL/PARTIAL/DRIFTED picture concrete), then bookkeeping batch
(G1, G8, G9, G11), then build-outward scope (G4, G5).

Suggested next move: build the failing schema-shape tests proposed
in SPEC/request_schema.md build-order step 2
(`TESTS/adversarial/test_request_schema.py`, one test per refusal
class in the schema's "Rejected shapes" section). These tests MUST
fail against the current `IMPLEMENTATION/pep.py` (which performs no
schema validation) - that failure is the honest G2 signal, same
shape as the failing canon-derived test the envelope spec proposes
for G7. Proposed ledger entry: VL-015.

Decisions parked for resolution before VL-014 becomes CONFIRMED:
the four open questions in SPEC/request_schema.md ("Open questions
for review"). Decision already recorded for open question 5
(artifact 05 absorbs `context` and `target_url`); scheduled as
VL-018.

Known items open but not scheduled (do not block the G0 build track):
- VL-011 process finding on pre-existing non-ASCII bytes in
  `EVIDENCE/archive/` files.
- VL-012 latent inconsistency on `receipt.py` `canonical_json`.
- VL-013 commit 606ddc1 contains one incidental whitespace-only edit
  to `docs/restructure/05_admissibility_envelope_spec.md` (the line
  ending "Lock and envelope are mutually reinforcing -") introduced
  by terminal-paste reconstruction during the session. VL-013
  enumerates three semantic edits to artifact 05 but the commit
  contains four diff-level changes. Same family as VL-012's em-dash
  normalization in `manifest_integrity_001.md`. Acknowledged here
  rather than as a new ledger entry because the ledger documents
  verification claims, not cosmetic process artifacts. No action.
- VL-014 process finding: the spec-defines-the-rename pattern has
  occurred twice now (VL-012 for `ccs_valid` ->
  `manifest_integrity_valid`; VL-014 for outer `context` ->
  `interaction` rename, code change deferred to proposed VL-017).
  Candidate governance rule GR-2 (spec-defines-the-rename; code
  change is a separate commit citing the spec entry) flagged in
  the VL-014 entry; not formally proposed and not added to
  `docs/MAINTENANCE_PROTOCOL.md` here. Decision deferred.
- VL-014 process finding: chat-pasted multi-line `git commit -m`
  blocks have now failed twice in the same session; the second
  failure landed only the schema commit and lost the ledger and
  STATE.md edits, requiring the corrective commit. Durable lesson
  recorded in the VL-014 entry; future session-close work should
  prefer `git commit` (no `-m`) for multi-paragraph messages and
  the `cat entry.md >>` technique for ledger appends. Not a
  governance rule, just an operational lesson; no action beyond
  the lesson being on the record.

---

## Known open gaps

See `docs/restructure/04_current_vs_claimed.md` for the full list. Summary:

- **G0** - CCS specification/implementation drift. **PARTIALLY RESOLVED**
  (VL-012): rename half closed (function renamed; name reserved in code
  and test IDs). Build half open (canonical CCS implementation is the
  G0 build track).
- **G1** - README test count stale / no commit-pinned source of truth.
- **G2** - request schema drift (interception proofs document a dead API).
  **PARTIALLY ADVANCED** (VL-014, d7eddd5): SPEC/request_schema.md names
  the rejected and accepting shapes at the schema layer. G2 fully closes
  when `IMPLEMENTATION/pep.py` enforces the schema at the PEP boundary
  (proposed VL-017, build-order step 4 of the schema's internal build
  order).
- **G3** - public framing overclaims relative to implementation.
- **G4** - the gate is bypassable (opt-in, not enforced).
- **G5** - "external" verification is not durable (ephemeral webhook).
- **G7** - tests are code-derived, not canon-derived.
- **G8** - evidence proofs are narrated, not executable.
- **G9** - `stability_proof_001.md` is truncated.
- **G11** - manifest-source asymmetry: `manifest_sha256()` reads from
  disk via hardcoded path, ignoring the manifest argument passed to
  `manifest_integrity_valid()` (surfaced by VL-012). Bookkeeping
  batch.

Resolved in VL-012: G6 (`ccs_valid` field removed), G10 (pinning
fields retained and documented). G0's rename half. See VL-012 and
`docs/restructure/04_current_vs_claimed.md` Resolved gaps section.

---

## Session-close note

This file is updated as the last step of each working session. The "Next open
action" and "Current verified state" sections must reflect reality at the time
of the last commit. If they do not, the repository's continuity is broken -
treat that as the first thing to fix.
