# Elyon-Sol - Project State

**This file is the entry point. A fresh session - the author, a new Claude
session, Grok, or any collaborator - should read this file first.**

**Session start/end:** see `docs/SESSION_PROTOCOL.md` for the resume and close protocols.
**Governance rules:** see `docs/MAINTENANCE_PROTOCOL.md` for the rules under which the repository is allowed to change (GR-N entries).

Last updated: 2026-05-15 (commit: see `git log` for STATE.md; G0/G6/G10 disambiguation pass complete; last ledger entry VL-012)

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
  entries VL-001 through VL-010.
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
  real repository tree; artifact 04 has been updated through G11 (this
  session: G0 partially resolved, G6 and G10 resolved, G11 added).
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

## What is locked vs. open

- **Locked:** canon v0.9.8.4. Corrected only by version increment, never by
  in-place edit (governance rule GR-1, ledger VL-007).
- **Open:** the honest-base track is complete and the disambiguation pass
  (G0/G6/G10) is complete. The G0 build track has not started. Known
  items recorded but not yet scheduled:
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

Begin the **G0 build track**: implement canonical CCS via the admissibility
envelope (`docs/restructure/05_admissibility_envelope_spec.md`), with
canon-derived tests (G7).

The honest-base track is complete; the disambiguation pass is complete:

1. **Artifact 01 reconciled against HEAD.** Done (commit 148e725).
2. **Maintenance protocol artifact added with GR-1.** Done (commit 6f7f0e7).
3. **MANIFEST/manifest.json committed** (sub-thread surfaced during step 1).
   Done (VL-010, commit c0867a6).
4. **EVIDENCE/ reorganized into proofs/ and archive/.** Done
   (VL-011, commit e6345a5).
5. **G0/G6/G10 disambiguation pass.** Done (VL-012, commit 8ba88cf;
   hash citation corrected in f0df14c).

Priority order for the G0 build track is in
`docs/restructure/04_current_vs_claimed.md` under "Priority order."
With priority item 3 (G0 rename + G6 + G10) now resolved, the remaining
order is: G0 build (canonical CCS via envelope), G7 (canon-derived tests),
G3 (reframe public materials once 06 makes the FULL/PARTIAL/DRIFTED
picture concrete), then bookkeeping batch (G1, G2, G8, G9, G11), then
build-outward scope (G4, G5).

Suggested first move on the G0 build track: build out
`SPEC/request_schema.md` (G2's anchor artifact, also referenced by
G10's documentation requirement and by the envelope spec's build order
step 1). This is the smallest unit of forward motion that unblocks
multiple downstream items.

Known items open but not scheduled (do not block the G0 build track):
- VL-011 process finding on pre-existing non-ASCII bytes in
  `EVIDENCE/archive/` files.
- VL-012 latent inconsistency on `receipt.py` `canonical_json`.

---

## Known open gaps

See `docs/restructure/04_current_vs_claimed.md` for the full list. Summary:

- **G0** - CCS specification/implementation drift. **PARTIALLY RESOLVED**
  (VL-012): rename half closed (function renamed; name reserved in code
  and test IDs). Build half open (canonical CCS implementation is the
  G0 build track).
- **G1** - README test count stale / no commit-pinned source of truth.
- **G2** - request schema drift (interception proofs document a dead API).
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

Resolved this session: G6 (`ccs_valid` field removed), G10 (pinning
fields retained and documented). G0's rename half. See VL-012 and
`docs/restructure/04_current_vs_claimed.md` Resolved gaps section.

---

## Session-close note

This file is updated as the last step of each working session. The "Next open
action" and "Current verified state" sections must reflect reality at the time
of the last commit. If they do not, the repository's continuity is broken -
treat that as the first thing to fix.
