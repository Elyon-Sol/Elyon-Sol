# Elyon-Sol - Project State

**This file is the entry point. A fresh session - the author, a new Claude
session, Grok, or any collaborator - should read this file first.**

**Session start/end:** see `docs/SESSION_PROTOCOL.md` for the resume and close protocols.
**Governance rules:** see `docs/MAINTENANCE_PROTOCOL.md` for the rules under which the repository is allowed to change (GR-N entries).

Last updated: 2026-05-18 (commit: see `git log` for STATE.md; VL-017 (failing schema-shape tests at PEP boundary; 27/27 fail uniformly at Pydantic wire-shape gate; honest G2 signal per schema's build-order step 2) lands in this commit alongside the STATE.md update; last ledger entry is VL-017; next action is the schema validator, proposed VL-018)

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
  entries VL-001 through VL-016.
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
- **Cross-model verification method applied deliberately and repeatedly
  (VL-014 -> VL-015 -> VL-016).** VL-014 drafted SPEC/request_schema.md as
  SINGLE-SOURCE. VL-015 ran cross-model verification of the schema with
  Grok and OpenAI (both procedurally clean), surfaced two new gaps (G12,
  G13), and transitioned VL-014 to DISPUTED. VL-016 ran a second cross-
  model verification on the *premises* beneath proposed corrections
  (Grok and OpenAI both procedurally clean; all three premises classified
  unanimously) and applied the resulting corrections, transitioning
  VL-014 to CORRECTED. Four verifier-runs in back-to-back rounds, all
  procedurally clean; methodology artifact recorded as candidate for
  durability commit.
- **Rev. 2 restructure package committed.** The seven planning artifacts
  (`00_README.md` through `06_spec_to_code_traceability.md`) are in
  `docs/restructure/`. The ASCII-safe standard (VL-006) has been applied
  repo-wide (VL-009). Artifact 01 has been revised to reconcile against the
  real repository tree; artifact 04 has been updated through G13 (VL-016
  session: G12 and G13 added with PARTIALLY ADDRESSED status).
  Artifacts 05 and 06 brought current to VL-012 in the VL-013 freshness
  pass; artifact 05 freshness pass to absorb `context` and `target_url`
  is proposed VL-020.
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
  the schema-layer half of G2). Status SINGLE-SOURCE at the time
  of VL-014.
- **VL-014 cross-model-verified (VL-015, commit 846b97a).** Grok and
  OpenAI both ran procedurally-clean derivations under VL-008. Core
  field set (AP, OP, manifest-pinning) agreed by all three
  derivations. Three-way divergence at three loci surfaced two new
  gap candidates: G12 (canon under-specifies wire-origins of `I`'s
  components) and G13 (manifest-pinning field provenance is mixed
  canon + envelope, not pure canon). VL-014 transitioned
  SINGLE-SOURCE -> DISPUTED. Three corrective decisions parked for
  VL-016 (1A, 2B, 3B), recorded in VL-015's entry.
- **VL-014 corrections applied (VL-016).** The three decisions
  parked in VL-015 (1A: `context` stays caller-supplied required
  with G12 rationale; 2B: `t` stays NOT caller-supplied with G12
  fail-closed rationale; 3B: manifest-pinning fields gain explicit
  layered-provenance note with G13 rationale) were applied to
  `SPEC/request_schema.md`. Prior to application, the *premises*
  beneath the decisions were cross-model-verified (Grok and
  OpenAI, both procedurally clean, unanimous classifications:
  premise 1 Under-specified, premise 2 Supported, premise 3
  Supported). OpenAI's argument-from-contrast framing of G12
  (canon's silence is meaningful because canon elsewhere
  demonstrates capacity to specify wire-origins for AR/R) was
  carried forward into G12's artifact-04 entry. G12 and G13
  added to artifact 04 with PARTIALLY ADDRESSED status (schema-
  layer half closed; canon-layer half open pending canon-version
  event under GR-1). VL-014 transitioned DISPUTED -> CORRECTED.
  The premise verification and the corrections are recorded in
  the single VL-016 entry; combined-entry rationale documented
  there.
- **Methodology artifacts promoted (VL-017a).** Two templates
  extracted from proven session patterns now committed to
  `docs/methodology/`: the verification-request template
  (extracted from `verification_request_vl014.md` and
  `verification_request_vl016_premises.md`; captures the
  VL-008-procedure-bound common structure across both) and the
  apply-script template (extracted from
  `apply_vl016_followup.py`; captures the uniqueness-check +
  atomic-write + per-edit-delta pattern, including the
  CRLF-on-read normalization fix and the always-write-LF
  convention learned from VL-017a's first-run abort). Both
  artifacts close methodology-debt candidate actions from
 VL-015 and the VL-016 follow-up. Classification: efficiency
  move, not trajectory move; recorded in VL-017a's entry with
  explicit framing of the distinction.
- **Failing schema-shape tests committed (VL-017).**
  `TESTS/adversarial/test_request_schema.py` adds 27 tests
  derived from `SPEC/request_schema.md` (post-VL-016,
  CORRECTED) - one per refusal class named in "Rejected
  shapes" plus a positive accepting-shape case. Against
  `IMPLEMENTATION/pep.py` at HEAD, all 27 fail. Uniform-422
  finding: every test fails at the same Pydantic wire-shape
  gate because the schema's `interaction` envelope is
  incompatible with the current `context` top-level field.
  The tests collectively prove wire-shape incompatibility
  but do not, today, discriminate between refusal classes;
  discrimination requires VL-019's wire-shape change.
  Evidence committed as
  `EVIDENCE/proofs/g2_schema_failing_tests_001.log` (raw
  pytest) and `EVIDENCE/proofs/g2_schema_failing_tests_001.md`
  (prose proof). Regression footprint clean:
  `TESTS/test_adversarial_evaluator.py` still 23/23 passing.
  The first artifact of the G2 build track's code half;
  the honest G2 signal that the schema's build-order step
  2 specifies. Classification: trajectory move per VL-017a's
  distinction.

## What is locked vs. open

- **Locked:** canon v0.9.8.4. Corrected only by version increment, never by
  in-place edit (governance rule GR-1, ledger VL-007).
- **Open:** the honest-base track is complete, the disambiguation pass
  (G0/G6/G10) is complete, and the G0 build track is underway with
  the first artifact (SPEC/request_schema.md) drafted (VL-014),
  cross-model-verified (VL-015), and corrected (VL-016). Known
  items recorded but not yet scheduled:
    - VL-009 ASCII-safe standard is violated by pre-existing content
      in the three `EVIDENCE/archive/` files (VL-011 process finding);
      resolution deferred to a follow-up decision (normalize / preserve
      verbatim / repo-wide pass).
    - G11 (manifest-source asymmetry in `manifest_sha256()`) is queued
      with G1, G8, G9 in the bookkeeping batch per artifact 04's
      priority order. (G2 was moved out of the bookkeeping batch in
      VL-016's artifact 04 update; it now has its own active track
      at priority item 4.)
    - G12 and G13 (the canon-layer halves) remain open; both
      require canon-version events under GR-1 to fully resolve.
      Not currently scheduled.
    - Latent VL-009 inconsistency: `IMPLEMENTATION/replay/receipt.py`'s
      `canonical_json` uses `ensure_ascii=False` (VL-012 process
      finding); not a current problem (no receipt currently contains
      non-ASCII bytes) but warrants documentation if scope-creep into
      a follow-up is desired.
    - VL-015 and VL-016 process findings on verification-request
      artifact durability: `verification_request_vl014.md` and
      `verification_request_vl016_premises.md` both prepared in
      chat and used directly without committing. The candidate
      action (commit a generalized verification-request template
      to `docs/`) is reinforced by the second instance but not
      actioned.
    - VL-016 process finding on premise-testing as a distinct
      verification shape (versus artifact verification). Worth
      naming in a methodology-artifact addition; not actioned.

---

## Next open action

Continue the **G0 build track** via the schema-work sub-order
proposed in `SPEC/request_schema.md` under "Build order
(schema-internal)". The schema itself is drafted, cross-model-
verified, and corrected (VL-014 + VL-015 + VL-016). The
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
7. **SPEC/request_schema.md drafted.** Done (d7eddd5, VL-014; ledger
   follow-up in bc83346).
8. **VL-014 cross-model-verified.** Done (VL-015, commit 846b97a).
   Result: SINGLE-SOURCE -> DISPUTED; G12 and G13 surfaced;
   decisions 1A, 2B, 3B parked.
9. **VL-014 corrections applied; premises cross-model-verified.**
   Done (VL-016, this commit). Result: DISPUTED -> CORRECTED;
   G12 and G13 entered in artifact 04 with PARTIALLY ADDRESSED
   status.
10. **Failing schema-shape tests committed.** Done (VL-017, this
    commit). 27 tests at `TESTS/adversarial/test_request_schema.py`,
    all failing uniformly at the Pydantic wire-shape gate against
    current pep.py. Evidence at
    `EVIDENCE/proofs/g2_schema_failing_tests_001.log` and `.md`.

With priority item 3 (G0 rename + G6 + G10) resolved, item
4 (SPEC/request_schema.md drafted + verified + corrected) complete,
and the failing-tests sub-step of item 4 done (VL-017),
the remaining order is:
G2 code-close (validator then PEP wiring; proposed
VL-018/VL-019), then G0 build (canonical CCS via envelope),
G7 (canon-derived tests), G3 (reframe public materials once 06 makes
the FULL/PARTIAL/DRIFTED picture concrete), then bookkeeping batch
(G1, G8, G9, G11), then build-outward scope (G4, G5).

Suggested next move: build the schema validator
`IMPLEMENTATION/request_validator.py` per SPEC/request_schema.md
build-order step 3. The validator implements the boundary behavior
in the order specified (parse, top-level, target_url, fields,
types), emitting one of the seven schema-named refusal codes on
rejection. The validator does NOT touch `pep.py`; wiring the
validator into the PEP boundary is build-order step 4 (proposed
VL-019), separate from the validator itself per VL-011's lesson
that distinct concerns get distinct commits. Once the validator
lands and is wired, the 27 failing tests committed in VL-017
become discriminating diagnostic instruments rather than a
collective wire-shape incompatibility proof. Proposed ledger
entry: VL-018.

Decisions parked for resolution: open question 5 of
SPEC/request_schema.md (artifact 05 absorbs `context` and
`target_url`) remains scheduled as VL-020 (renumbered from VL-018
to absorb the VL-015/VL-016 consumption of the prior numbering).
The other four open questions from VL-014's draft are resolved by
VL-016's corrections.

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
  `interaction` rename, code change deferred to proposed VL-019).
  Candidate governance rule GR-2 (spec-defines-the-rename; code
  change is a separate commit citing the spec entry) flagged in
  the VL-014 entry; not formally proposed and not added to
  `docs/MAINTENANCE_PROTOCOL.md` here. Decision deferred.
- VL-014 process finding: chat-pasted multi-line `git commit -m`
  blocks have now failed twice. Operational lesson recorded in
  the VL-014 entry; the VL-016 commit uses `git commit -F <file>`
  per the handoff's lesson #1.
- VL-015 and VL-016 process finding: verification-request
  artifacts (`verification_request_vl014.md`,
  `verification_request_vl016_premises.md`) prepared in chat,
  used, not committed. Candidate action to commit a generalized
  template to `docs/` is reinforced by the second instance.
  Not actioned.
- VL-016 process finding: premise-testing as a distinct
  verification shape (vs. artifact verification). Worth a
  methodology-artifact addition. Not actioned.
- VL-016 follow-up process finding: third instance of
  chat-paste-eats-content failure (after VL-012's `git commit
  -m` newline loss and VL-014's twice-failed `-m` block).
  This instance: comment-only lines in a pasted execution
  block were silently skipped, leaving the schema and
  artifact-04 edits unapplied. `git status` between operations
  correctly fired the stop signal (lesson 5) but the workflow
  had no pause point for the human to act on it. Two
  generalized lessons recorded in the VL-016 follow-up entry:
  (a) never paste a multi-step block containing comment-form
  action items; paste the actual commands or one tool call
  per step; (b) stop signals require interactive pauses, not
  just printed warnings. Worth promoting the
session-mechanics-lessons file to `docs/` so these
  accumulate durably. Not actioned.
- VL-017 process findings (eight session friction points; false
  stop signal on line count; ledger-entry blank-line stripping
  in VL-017a's committed text). The session-mechanics-lessons
  promotion candidate is now reinforced by a quantified
  threshold per VL-017's entry: if VL-018's session opens with
  three or more friction points in the first hour before
  substantive work begins, pause trajectory work and promote
  the session-mechanics-lessons file as that session's
  deliverable. The threshold is the first attempt in this
  project at making a process-finding candidate self-actuating
  rather than perpetually-deferred.
- VL-017 stale forward-reference in SPEC/request_schema.md.
  The schema's "Build order (schema-internal)" closing
  paragraph lists `VL-014 (this artifact), VL-015 (failing
  tests), VL-016 (validator), VL-017 (PEP wiring + G2 close),
  VL-018 (artifact 05 freshness pass)` but the actual
  numbering, post VL-015's cross-model verification and
  VL-016's corrections, is `VL-014 schema, VL-015 verify,
  VL-016 corrections, VL-017 tests, VL-018 validator,
  VL-019 PEP wiring, VL-020 artifact 05`. The schema's
  closing paragraph is a stale forward reference. Worth one
  focused commit to update; not blocking; not actioned in
  VL-017 (which would muddy the test-file commit).
- VL-017 process finding: inherited-`.gitignore` pattern,
  second instance (after VL-010). The Python-template
  `.gitignore` hid `EVIDENCE/proofs/g2_schema_failing_tests_001.log`
  via the `*.log` rule at line 61; corrected with an explicit
  un-ignore `!EVIDENCE/proofs/*.log` landing in the same commit
  as the file it was hiding (structurally parallel to VL-010).
  Two instances is a pattern. Candidate action: a focused
  audit-commit of `.gitignore` against the repo's actual
  domain directories (`CANON/`, `MANIFEST/`, `EVIDENCE/`,
  `SPEC/`, `IMPLEMENTATION/`, `TESTS/`, `docs/`), adding
  explicit un-ignore rules or comments for every name that
  could collide with a template assumption. Efficiency move
  per VL-017a's classification; not blocking. Not actioned.

---

## Known open gaps

See `docs/restructure/04_current_vs_claimed.md` for the full list. Summary:

- **G0** - CCS specification/implementation drift. **PARTIALLY RESOLVED**
  (VL-012): rename half closed (function renamed; name reserved in code
  and test IDs). Build half open (canonical CCS implementation is the
  G0 build track).
- **G1** - README test count stale / no commit-pinned source of truth.
- **G2** - request schema drift (interception proofs document a dead API).
  **PARTIALLY ADVANCED** (VL-014 + VL-015 + VL-016 + VL-017):
  SPEC/request_schema.md names the rejected and accepting shapes at
  the schema layer, has been cross-model-verified, and the disputed
  interpretive loci have been corrected. VL-017 added 27 failing
  schema-shape tests at `TESTS/adversarial/test_request_schema.py`
  per the schema's build-order step 2. G2 fully closes when the
  schema validator (proposed VL-018) lands and is wired into
  `IMPLEMENTATION/pep.py` at the PEP boundary (proposed VL-019,
  build-order step 4 of the schema's internal build order).- **G3** - public framing overclaims relative to implementation.
- **G4** - the gate is bypassable (opt-in, not enforced).
- **G5** - "external" verification is not durable (ephemeral webhook).
- **G7** - tests are code-derived, not canon-derived.
- **G8** - evidence proofs are narrated, not executable.
- **G9** - `stability_proof_001.md` is truncated.
- **G11** - manifest-source asymmetry: `manifest_sha256()` reads from
  disk via hardcoded path, ignoring the manifest argument passed to
  `manifest_integrity_valid()` (surfaced by VL-012). Bookkeeping
  batch.
- **G12** - canon section 11.1 under-specifies wire-origins of
  `I`'s components. **PARTIALLY ADDRESSED** (VL-016): schema-
  layer interpretive choices for `C` and `t` made explicit with
  rationale. Canon-layer half open; resolution would require a
  canon-version event under GR-1.
- **G13** - manifest-pinning field provenance is mixed canon +
  envelope, not pure canon. **PARTIALLY ADDRESSED** (VL-016):
  schema attribution corrected to make layered provenance
  explicit. Canon-layer half open; section 11.9 specifies
  manifest properties but does not specify wire operationalization.

Resolved in VL-012: G6 (`ccs_valid` field removed), G10 (pinning
fields retained and documented). G0's rename half. See VL-012 and
`docs/restructure/04_current_vs_claimed.md` Resolved gaps section.

---

## Session-close note

This file is updated as the last step of each working session. The "Next open
action" and "Current verified state" sections must reflect reality at the time
of the last commit. If they do not, the repository's continuity is broken -
treat that as the first thing to fix.
