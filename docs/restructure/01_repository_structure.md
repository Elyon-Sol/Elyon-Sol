# Elyon-Sol - Repository Structure: Proposed vs. Actual

**Status:** Revised. Reconciled against HEAD = 2db1807 (after VL-010).
**Supersedes:** the greenfield proposal previously occupying this file
(see "Original proposal" below, retained for record).
**Note on HEAD:** the tree below reflects the state as of commit 2db1807,
which is after the VL-010 closeout (manifest committed, ledger entry
appended). Earlier drafting referenced HEAD = 9f74235; that reference is
preserved in the body where it cites the pre-VL-010 state of specific
files.
**Premise:** Canon is locked. Everything else in the repository is *derivation
from* canon. The repository - not any model's memory - is the continuity
layer.

This artifact is a **diff against reality**. It records what was proposed
during Rev. 2 planning, what the repository actually contains as of HEAD,
where the two agree, where they diverge, and what the reconciled structure
is. It is not a proposal from scratch; the repository is built out, and any
future structural change is a diff against this file.

---

## Design principles (unchanged from original proposal)

These principles guided the original proposal and remain in force. They are
the criteria against which the reconciliation below is judged.

1. **Canon is the fixed point.** It is read-only in normal operation. Nothing
   else may contradict it; everything else must be traceable to it.
2. **Every claim has a location.** Description lives in one place, evidence
   in another, code in another. No claim exists in prose that is not backed
   by a file under `EVIDENCE/` or `TESTS/`.
3. **One source of truth per fact.** Test counts, version numbers, and the
   request schema each appear authoritatively in exactly one file. Everything
   else references it.
4. **Stale artifacts are removed or clearly marked, not left implying
   currency.** A proof describing an API the code no longer accepts is
   rewritten against current code or moved to an archive directory marked
   non-current.
5. **The envelope is the bridge.** The admissibility envelope is the
   versioned object that proves derivation integrity holds as the manifest
   and implementation evolve beneath the locked canon.

---

## Actual structure at HEAD

The committed tree at commit 9f74235 is:

```
Elyon-Sol/
+-- .gitattributes
+-- .gitignore
+-- LICENSE
+-- README.md                          # entry-point doc (still framing issues, G3)
+-- STATE.md                           # entry-point continuity file (added a7de833)
|
+-- CANON/                             # LOCKED. Fixed point.
|   +-- canon_v0.9.8.4.pdf             # immutable source of record
|   +-- canon.md                       # ASCII-safe transcription (VL-006)
|   \-- canon.lock                     # sha256 of canon.md
|
+-- IMPLEMENTATION/
|   +-- evaluator.py                   # three-condition gate
|   +-- pep.py                         # PEP / admission logic
|   +-- server.py                      # HTTP gate
|   +-- target.py                      # downstream target stub
|   \-- replay/
|       \-- receipt.py                 # replay-receipt subsystem
|
+-- MANIFEST/
|   \-- manifest.json                  # committed at c0867a6 (VL-010); cited by VL-003
|
+-- TESTS/
|   +-- ADVERSARIAL_RESULTS.md         # adversarial run record
|   +-- test_adversarial_evaluator.py
|   +-- test_cases.json
|   +-- test_concurrency.py
|   +-- test_pep.py
|   \-- test_replay_receipts.py
|
+-- EVIDENCE/
|   +-- verification_ledger.md         # append-only ledger (VL-001..VL-009)
|   +-- concurrent_replay_equivalence_001.md
|   +-- interception_proof_001.md      # documents flat-key API (stale, see G2)
|   +-- interception_proof_002.md      # documents flat-key API (stale, see G2)
|   +-- manifest_integrity_continuity_001.md
|   +-- mutation_sensitivity_001.md
|   +-- stability_proof_001.md         # truncated (G9)
|   \-- tmp/
|       \-- ac3_mutation_failure.txt   # supporting artifact for mutation proof
|
+-- POE/                               # proof-of-existence layer
|   +-- POE_MANIFEST.md
|   +-- POE_SHA256_HASHES.txt
|   \-- generate_poe_hashes.py
|
+-- docs/
|   +-- SESSION_PROTOCOL.md            # session resume / close protocol
|   \-- restructure/                   # Rev. 2 planning package
|       +-- 00_README.md
|       +-- 01_repository_structure.md   # this file
|       +-- 02_honest_core_description.md
|       +-- 03_vocabulary_ledger.md
|       +-- 04_current_vs_claimed.md     # the gap document (lives here, not docs/)
|       +-- 05_admissibility_envelope_spec.md
|       +-- 06_spec_to_code_traceability.md
|       \-- canon_transcription_verification_report.md
|
\-- scripts/
    +-- establish_ledger.sh
    +-- lock_canon.sh
    +-- append_vl008.sh
    \-- append_vl009.sh
```

This is the structure of record. Subsequent sections show how it relates to
the original proposal.

---

## Reconciliation: proposed vs. actual

For each item in the original proposal, one of: **PRESENT** (exists as
proposed), **DIVERGED** (exists in a different form, with a decision),
**PENDING** (will exist after a named open action), or **DEFERRED** (in the
proposal but no longer planned for the honest-base track).

### CANON/

- `CANON/canon.md` - **PRESENT.** Transcription locked at VL-006.
- `CANON/canon.lock` - **PRESENT.** Hash of canon.md at lock time.
- `CANON/canon_v0.9.8.4.pdf` - **PRESENT (not in original proposal).** The
  immutable source of record, which canon.md is verified against. The
  original proposal omitted it; it must be listed because the ledger
  (VL-006) anchors canon.md to it.

### SPEC/

- `SPEC/admissibility_envelope.md` - **DIVERGED.** Lives at
  `docs/restructure/05_admissibility_envelope_spec.md`. Decision: leave in
  the restructure package for now. It is a *spec for work not yet done*
  (the G0 build track); promoting it to a top-level `SPEC/` directory while
  the G0 build track has not started would imply currency it does not have.
  When the G0 build begins, the envelope spec moves to `SPEC/` and is
  versioned there.
- `SPEC/vocabulary.md` - **DIVERGED.** Lives at
  `docs/restructure/03_vocabulary_ledger.md`. Same reasoning: planning
  artifact until promoted.
- `SPEC/request_schema.md` - **PENDING.** Does not exist in any form. The
  authoritative request/response shape is currently implicit in `pep.py`
  and `server.py`. Closing G2 (request schema drift) requires creating
  this file. Listed under "Pending under honest-base track" below.

The original proposal's `SPEC/` directory is therefore **deferred until the
G0 build track**, except for `request_schema.md` which is honest-base work.

### IMPLEMENTATION/

- `IMPLEMENTATION/evaluator.py` - **PRESENT.**
- `IMPLEMENTATION/pep.py` - **PRESENT.**
- `IMPLEMENTATION/envelope.py` - **DEFERRED.** Original proposal already
  marked this "(future)". It is part of the G0 build track, not the
  honest-base track.
- `IMPLEMENTATION/server.py` - **PRESENT (not in original proposal).** The
  HTTP gate. The original proposal underspecified the HTTP layer.
- `IMPLEMENTATION/target.py` - **PRESENT (not in original proposal).** The
  downstream target stub used by tests.
- `IMPLEMENTATION/replay/receipt.py` - **PRESENT (not in original proposal).**
  The replay-receipt subsystem - an entire concern the original proposal did
  not contemplate. Tested by `TESTS/test_replay_receipts.py` and proved by
  `EVIDENCE/concurrent_replay_equivalence_001.md`.

The implementation layer is materially larger than the original proposal
showed. The proposal's three-file picture (`evaluator.py`, `pep.py`,
`envelope.py`) was an idealization. The real layer has five live files plus
the replay subdirectory, and a future envelope addition.

### MANIFEST/

- `MANIFEST/manifest.json` - **PRESENT.** Committed at c0867a6 during this
  session's honest-base closeout; the corrective ledger entry is VL-010.
  The file was previously hidden by an inherited Python-template
  `.gitignore` rule (bare `MANIFEST` and `*.manifest`); both rules were
  removed and the directory committed. VL-003 references this file as a
  primary source; with the file now tracked, VL-003 is reproducible from
  a fresh clone. The `version` field semantics are documented in VL-010
  (caller-asserted equality, not canon-tied) - candidate for an entry in
  the future vocabulary ledger.

### TESTS/

- `TESTS/test_evaluator.py` - **DIVERGED.** No file by that name; closest
  match is `TESTS/test_adversarial_evaluator.py`, which is the adversarial
  suite (see next item). Whether a non-adversarial `test_evaluator.py` is
  warranted is a question for the G0 build track; for honest-base, the
  observation is just that the proposal's name does not exist.
- `TESTS/test_pep.py` - **PRESENT.**
- `TESTS/adversarial/` subdirectory with three files
  (`test_mutation_sensitivity.py`, `test_bypass.py`, `test_boundary.py`) -
  **DIVERGED.** Reality has one flat file
  `TESTS/test_adversarial_evaluator.py` plus the results record
  `TESTS/ADVERSARIAL_RESULTS.md`. Decision: leave flat for now. The
  subdirectory structure was a planning convenience; splitting one file
  into three has no current benefit and would obscure the actual coverage.
  Revisit if the adversarial suite grows.
- `TESTS/test_cases.json` - **PRESENT.**
- `TESTS/test_concurrency.py` - **PRESENT (not in original proposal).**
  Tests the concurrency / replay-equivalence path.
- `TESTS/test_replay_receipts.py` - **PRESENT (not in original proposal).**
  Tests the replay-receipt subsystem.

### EVIDENCE/

- `EVIDENCE/STATE.md` - **DIVERGED, intentionally.** The original proposal
  put a state file under `EVIDENCE/`. Reality has `STATE.md` at the
  repository root, written after the proposal (commit a7de833). The root
  placement is correct: STATE.md declares itself the entry point on its
  first line. Burying the entry point under `EVIDENCE/` would contradict
  that role. The root placement is endorsed; the proposal's
  `EVIDENCE/STATE.md` location is superseded.
- `EVIDENCE/proofs/` and `EVIDENCE/archive/` subdirectories - **PENDING.**
  This is honest-base track step 3. The two interception proofs
  (`interception_proof_001.md`, `interception_proof_002.md`) document a
  dead flat-key API (G2) and belong in `archive/` marked non-current. The
  other four proofs are candidates for `proofs/` once each is verified
  against current code.
- `EVIDENCE/verification_ledger.md` - **PRESENT (not in original
  proposal).** The ledger itself was added during Rev. 2 work (VL-001) and
  is the highest-order evidence file. Its position directly under
  `EVIDENCE/` is correct and is endorsed.
- Existing proof files - **PRESENT, awaiting reorganization (G2/G7/G8/G9).**
  Six proofs exist:
  `concurrent_replay_equivalence_001.md`,
  `interception_proof_001.md`,
  `interception_proof_002.md`,
  `manifest_integrity_continuity_001.md`,
  `mutation_sensitivity_001.md`,
  `stability_proof_001.md`.
  The original proposal named only the two interception proofs; the
  others were not anticipated. The reorganization (step 3) covers all six.
- `EVIDENCE/tmp/ac3_mutation_failure.txt` - **PRESENT (not in original
  proposal).** Supporting artifact for `mutation_sensitivity_001.md`.
  Decision: keep `tmp/` as is for now; revisit during step 3 whether
  supporting artifacts should live alongside their proofs in `proofs/`
  rather than in a separate `tmp/`.

### docs/

- `docs/current_vs_claimed.md` - **DIVERGED.** Lives at
  `docs/restructure/04_current_vs_claimed.md`. Decision: leave in the
  restructure package. The file's job is the *living gap document*; it
  serves that job from its current location. Promotion to `docs/` is not
  required by any open action.

### POE/

- The entire `POE/` directory - **PRESENT (not in original proposal).**
  `POE_MANIFEST.md`, `POE_SHA256_HASHES.txt`, `generate_poe_hashes.py`. A
  proof-of-existence layer that the original proposal did not contemplate.
  Decision: keep at the top level. POE is not derivation-from-canon
  (`SPEC/` and `EVIDENCE/` are); it is a parallel integrity record over
  the repository's own artifacts. Top-level placement reflects that.

### scripts/

- The entire `scripts/` directory - **PRESENT (not in original proposal).**
  `establish_ledger.sh`, `lock_canon.sh`, `append_vl008.sh`,
  `append_vl009.sh`, `append_vl010.sh`. The method-on-record for the
  ledger and the canon lock. STATE.md treats these as part of what makes
  the ledger reproducible. Top-level placement is correct.

### root-level files

- `README.md` - **PRESENT.** Still has the framing issues the original
  proposal flagged (G3); rewriting per artifact 02 is a separate open
  action, not part of this revision.
- `STATE.md` - **PRESENT (not in original proposal).** See `EVIDENCE/`
  note above.
- `.gitattributes` - **PRESENT (not in original proposal).** Enforces
  text-mode line endings and the ASCII-safe regime (VL-006/VL-009).
- `.gitignore`, `LICENSE` - standard; not material to structure.

---

## Pending under the honest-base track

These are the structural changes that will land before the G0 build track
begins. Each corresponds to an item in STATE.md's "Next open action".

1. **Maintenance-protocol artifact** (STATE.md step 2). A new file in
   `docs/restructure/` (or promoted to `docs/maintenance_protocol.md`)
   recording governance rule GR-1 (canon corrected only by version
   increment, never by in-place edit). Closes the dangling reference from
   VL-007.
2. **`EVIDENCE/proofs/` and `EVIDENCE/archive/`** (STATE.md step 3). The
   two interception proofs move to `archive/` marked non-current. The
   remaining four proofs are evaluated: each verified against current
   code moves to `proofs/`; any that cannot be verified moves to
   `archive/`.
3. **Request schema** (closes G2). Create the authoritative request
   schema as a single source of truth - location to be decided when the
   work begins (top-level `SPEC/request_schema.md` per the proposal, or
   somewhere lighter-weight if `SPEC/` is not yet warranted).

**Done during this session (artifact 01 revision):**
- Commit `MANIFEST/manifest.json` and correct the `.gitignore` overmatch
  hiding it - landed at commit c0867a6 with corrective ledger entry
  VL-010. This was raised as a fourth pending item in an earlier draft
  of this artifact; it was closed in the same session that drafted the
  reconciliation.

When each of these lands, this file is updated to reflect the new state.

---

## Deferred to the G0 build track

These items from the original proposal are real intentions, but are not
honest-base work and should not be created until the G0 build track begins.
Creating them earlier would imply readiness the project does not have.

- `SPEC/admissibility_envelope.md` (promoted from
  `docs/restructure/05_admissibility_envelope_spec.md`).
- `SPEC/vocabulary.md` (promoted from
  `docs/restructure/03_vocabulary_ledger.md`).
- `IMPLEMENTATION/envelope.py`.
- `TESTS/test_evaluator.py` as a non-adversarial unit suite, if needed.
- `TESTS/adversarial/` as a subdirectory, if the adversarial suite grows
  to justify the split.

---

## Why this serves the stated objective

The original proposal's "why" section still holds. Restated against the
reconciled structure:

- **"Organization."** Every committed file has a location that reflects
  its job. Where the proposal and reality diverged, the reconciliation
  picked the side that better matched each file's actual role (root-level
  STATE.md, flat adversarial test file, restructure-package home for
  planning artifacts).
- **"Adversarial and external proofs."** The adversarial layer exists
  (`test_adversarial_evaluator.py` + `ADVERSARIAL_RESULTS.md`); the
  evidence layer exists. Step 3 sharpens the evidence layer by separating
  current proofs from archived ones.
- **"Assimilate everything into the core."** The restructure package
  (`docs/restructure/`) is where scattered prose became derivation
  artifacts. Canon under `CANON/` is the core they derive from.
- **"Declare it as what it should be."** STATE.md (root) and
  `04_current_vs_claimed.md` (in the restructure package) carry that
  burden. README still does not (G3), and that is an open action.
- **"Envelope that can be reasserted for continuity."** The envelope
  spec exists as a planning artifact
  (`05_admissibility_envelope_spec.md`); the implementation is the G0
  build track.
- **Continuity without relying on a model.** A fresh reviewer can read
  STATE.md, the ledger, this artifact, and the restructure package and
  orient from the tree alone. The repository is the continuity layer.

---

## Original proposal (retained for record)

The text below is the original Rev. 2 proposed structure, kept verbatim
inside this artifact so the reconciliation has a referent. It is no
longer the proposal; it is the prior version of this file's substance,
preserved.

> ```
> Elyon-Sol/
> +-- README.md                      # Entry point. Honest core description.
> |
> +-- CANON/                         # LOCKED.
> |   +-- canon.md
> |   \-- canon.lock
> |
> +-- SPEC/                          # Derivation from canon.
> |   +-- admissibility_envelope.md
> |   +-- vocabulary.md
> |   \-- request_schema.md
> |
> +-- IMPLEMENTATION/
> |   +-- evaluator.py
> |   +-- pep.py
> |   \-- envelope.py                # (future)
> |
> +-- MANIFEST/
> |   \-- manifest.json
> |
> +-- TESTS/
> |   +-- test_evaluator.py
> |   +-- test_pep.py
> |   +-- adversarial/
> |   |   +-- test_mutation_sensitivity.py
> |   |   +-- test_bypass.py
> |   |   \-- test_boundary.py
> |   \-- test_cases.json
> |
> +-- EVIDENCE/
> |   +-- STATE.md
> |   +-- proofs/
> |   \-- archive/
> |
> \-- docs/
>     \-- current_vs_claimed.md
> ```

The reconciliation above records, for each line of the proposed tree,
whether it is present, diverged (with decision), pending under the
honest-base track, or deferred to the G0 build track.
