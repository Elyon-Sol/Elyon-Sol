# Elyon-Sol - Project State

**This file is the entry point. A fresh session - the author, a new Claude
session, Grok, or any collaborator - should read this file first.**

**Session start/end:** see `docs/SESSION_PROTOCOL.md` for the resume and close protocols.

Last updated: 2026-05-14 (commit: see `git log` for STATE.md; last entry VL-008)

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
   spec-to-code traceability map.
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
  entries VL-001 through VL-008.
- **G0 confirmed (anchor finding).** Canonical CCS (whitepaper sections 12-13)
  is a temporal invariant over state transitions; the implemented `ccs_valid()`
  is a point-in-time manifest-integrity check. They are not the same invariant.
  Confirmed by three independent derivations from primary sources: Claude,
  Grok (clean pass), and OpenAI (ledger VL-002, VL-008).
- **Method on record.** `scripts/establish_ledger.sh`, `scripts/lock_canon.sh`,
  and `scripts/append_vl008.sh` - the scripts that built the ledger, the lock,
  and the VL-008 entry - are committed.
- **Cross-model verification procedure established (VL-008).** A valid
  verification requires the task scoped to primary sources and confirmation the
  response stayed within that scope. A model's prior exposure to the project
  does not disqualify it, provided those hold. Two failed and one successful
  OpenAI attempt are documented in VL-008.

## What is locked vs. open

- **Locked:** canon v0.9.8.4. Corrected only by version increment, never by
  in-place edit (governance rule GR-1, ledger VL-007).
- **Open:** the honest-base track is in progress - canon locked, ledger
  established (VL-001..008); the four remaining honest-base items are listed
  under "Next open action". The G0 build track has not started. See next section.

---

## Next open action

Complete the **honest-base track** before beginning the G0 build track.
Reproducibility and technical rigor require the repository to be clean and
internally consistent first. In order:

1. **Revise restructure artifact 01** (`docs/restructure/01_repository_structure.md`)
   to reconcile with the *real* repository structure. Artifact 01 was drafted
   greenfield; the repository is more built-out (it has `POE/`,
   `IMPLEMENTATION/replay/`, `server.py`, `target.py`, existing tests). Artifact
   01 must become a diff against reality, not a proposal from scratch.
2. **Build the maintenance-protocol artifact** containing governance rule GR-1.
   VL-007 references GR-1; it currently has no home. This closes a dangling
   reference in the committed ledger.
3. **Reorganize the six `EVIDENCE/*.md` docs** into `EVIDENCE/proofs/` and
   `EVIDENCE/archive/` per gaps G2/G7/G8/G9 (see `docs/restructure/04_current_vs_claimed.md`).
   The two interception proofs document a dead (flat-key) API and belong in
   `archive/` marked non-current.
4. **Place the seven restructure-package artifacts** (`00`-`06`) into
   `docs/restructure/`. They exist only as session output and must be committed
   to the repository to be part of the continuity layer.

Only after the honest-base track is complete: begin the **G0 build track** -
implement canonical CCS via the admissibility envelope
(`docs/restructure/05_admissibility_envelope_spec.md`), with canon-derived tests.

---

## Known open gaps

See `docs/restructure/04_current_vs_claimed.md` for the full list. Summary:

- **G0** - CCS specification/implementation drift (anchor gap; confirmed; the
  G0 build track addresses it).
- **G1** - README test count stale / no commit-pinned source of truth.
- **G2** - request schema drift (interception proofs document a dead API).
- **G3** - public framing overclaims relative to implementation.
- **G4** - the gate is bypassable (opt-in, not enforced).
- **G5** - "external" verification is not durable (ephemeral webhook).
- **G6** - `ccs_valid` input field is caller-asserted and circular.
- **G7** - tests are code-derived, not canon-derived.
- **G8** - evidence proofs are narrated, not executable.
- **G9** - `stability_proof_001.md` is truncated.

---

## Session-close note

This file is updated as the last step of each working session. The "Next open
action" and "Current verified state" sections must reflect reality at the time
of the last commit. If they do not, the repository's continuity is broken -
treat that as the first thing to fix.
