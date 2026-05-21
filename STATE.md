# Elyon-Sol - Project State

**This file is the entry point. A fresh session - the author, a new Claude
session, Grok, or any collaborator - should read this file first.**

**Session start/end:** see `docs/SESSION_PROTOCOL.md` for the resume and close protocols.
**Governance rules:** see `docs/MAINTENANCE_PROTOCOL.md` for the rules under which the repository is allowed to change (GR-N entries).

Last updated: 2026-05-21 (commit: see `git log` for STATE.md; VL-025 follow-up cross-model verification of envelope.py against artifact 05 and canon section 12-13 (methodology / analysis entry: two-bundle, two-recipient cross-model verification under VL-008 + Lesson 6 with Grok and OpenAI as recipients; Bundle A verifies envelope.py against artifact 05 spec; Bundle B verifies reassert() behavior against canon section 12-13; all four verifier-runs procedurally clean with one re-request for response-mechanism truncation; substantive convergence across all four runs: no Divergence and no Code-absent classifications anywhere - envelope.py honors the intent of both artifact 05 and canon section 12-13; VL-024 Implication 2 fully confirmed: Row 3 evaluator_sha256 mismatch -> RE-EVALUATE-REQUIRED directly authorized by canon section 12.4 per both Bundle B verifiers, inference flag retired; classification divergence on Match-vs-Spec-undetermined rigor produces six gap candidates (five spec-clarification + one non-spec implementation pattern), batchable into a single pre-VL-027 artifact 05 spec-revision commit; four methodology process findings for verification request template revision (Match-criterion ambiguity, absence-of-Divergence as signal, response truncation handling, scope-check enumeration discipline); methodology / analysis classification per VL-017a; no code/canon/test/spec/structural-doc change in this commit) lands in this commit; prior ledger entry VL-025 at commit 096c933; G0 build half remains PARTIALLY RESOLVED with envelope.py verified correct; next trajectory action is VL-026 (canon-derived tests) per existing session opener) plus VL-025 G0 build half: canonical CCS implementation via envelope.py (trajectory entry: IMPLEMENTATION/envelope.py lands per docs/restructure/05_admissibility_envelope_spec.md build-order step 3; two functions implemented - build_envelope() constructs the envelope per artifact 05's Envelope structure section, reassert() implements the five-row Reassertion protocol table with VL-024 Implication 2's evaluator-versioning fail-closed posture converted from inference to direct citation at Row 3; Option A integration locked pre-build (condition booleans as parameters; envelope.py imports only manifest_sha256 from evaluator.py and is not imported by evaluator.py or pep.py at VL-025); reassert() pure with respect to envelope (reads live file hashes, does not modify input); ensure_ascii=True per VL-009 with divergence from receipt.py recorded as gap candidate 4; condition_results.ccs None on first issuance per artifact 05 open question 1 locked by opener constraint (e); five gap candidates surfaced (reassert-time ccs semantic, evaluate aggregate return vs condition needs, c_{t+1} vs T^26 relationship, ensure_ascii divergence, canon_sha256 source choice) none blocking; smoke test verified end-to-end pre-commit (validator -> conditions -> build_envelope -> reassert across all 5 table rows in order plus determinism plus timestamp-invariance plus purity); build-resumption template's second behavioral instance and first with Claude as executing agent, two-instance threshold met per session_mechanics_lessons.md line 47; G0 build half transitions from OPEN to PARTIALLY RESOLVED with envelope.py landed and tests + pep.py wiring still open for VL-026 and VL-027 respectively; canonical CCS in 06_spec_to_code_traceability.md transitions from UNIMPLEMENTED to PARTIALLY IMPLEMENTED with structured artifact 06 update deferred to a follow-up commit paralleling VL-018's pattern; trajectory move per VL-017a's distinction; no canon/manifest/schema/structural-doc change in this commit) (methodology / analysis entry deriving whether and how the cross-model run at VL-023 follow-up strengthens the framework's claim of recursive continuity discipline - outcome: STRENGTHENS, bounded to layers B (epistemic discipline) and C (reading-aid track) of the framework's purposes; not layer A (declared purpose / gate behavior); three load-bearing sub-meanings derived after source-of-truth enumeration per Lesson 5 substituted opener candidates: confidence in the recursive-continuity claim strengthens materially on both the abstract shape and the per-layer verdicts including the load-bearing request-layer exclusion; scope expands by one fitting layer (evaluator versioning) with one artifact-recoverable inference caveat, PARTIAL HOLDS unchanged with fitting set now five; methodology-pattern durability strengthens with the cross-model evaluate template now meeting the two-instance threshold per session_mechanics_lessons.md line 47 and the methodology layer's recursive-continuity instance now operative rather than merely observable; five downstream implications recorded covering `07_continuity_recursion.md` composition, VL-025 envelope.py build attention to `evaluator` block `reassert()` semantics, external defensibility bounded by current readership scope, cross-model evaluate template single-instance language removable, and derivation-over-absorption verdict-refinement as the first instance of a candidate methodology pattern; methodology / analysis classification per VL-017a; no code/canon/test/spec/structural-doc change) lands in this commit; prior ledger entry VL-023 follow-up at commit 49b797a; G2 still closed in code at VL-019; next trajectory action is VL-025 (G0 build half: envelope.py))

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
  entries VL-001 through VL-019.
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
- **Build-resumption invocation tested against two models
  (VL-017b).** A dry-run test of the invocation artifact for
  VL-018 (`IMPLEMENTATION/request_validator.py` per
  `SPEC/request_schema.md` build-order step 3) was run against
  Grok and OpenAI with identical six-file primary-source
  bundles. Both models produced procedurally-clean output per
  VL-008-adapted-for-build (scope confirmation, spec-citation
  maps, no out-of-scope artifacts). Both validators converged
  on six refusal codes (`REF_SCHEMA_TOP_LEVEL`,
  `REF_SCHEMA_BAD_URL`, `REF_SCHEMA_FLAT_KEYS`,
  `REF_SCHEMA_MANIFEST_PINNING_MISSING`,
  `REF_SCHEMA_TYPE_MISMATCH`, `REF_SCHEMA_RESERVED_CCS`) with
  identical trigger semantics. They diverged on a seventh code
  (parse-error: Grok handles externally, OpenAI names but does
  not trigger). Three candidate spec-gap findings recorded:
  seventh-code disambiguation, generic-unknown-key handling,
  parse-order API-vs-procedure separation. Build-resumption-
  request template extracted from the test prompt and promoted
  to `docs/methodology/build_resumption_request_template.md`,
  paralleling VL-017a's verification-request-template
  promotion. Classification: test result with incidental
  trajectory findings (new category; distinct from VL-017a's
  pure-efficiency and VL-017's pure-trajectory). The three
  candidate findings carry explicit citation discipline: they
  may be confirmed, superseded, or revised by VL-018's
  live-build commit, but must not be cited as established spec
  gaps without that confirmation.
- **Schema validator committed (VL-018).**
  `IMPLEMENTATION/request_validator.py` lands per
  `SPEC/request_schema.md` build-order step 3. The validator
  accepts an already-parsed Python dict and returns either a
  normalized interaction dict (AP/OP sorted and deduplicated)
  or one of six refusal codes (`REF_SCHEMA_TOP_LEVEL`,
  `REF_SCHEMA_BAD_URL`, `REF_SCHEMA_FLAT_KEYS`,
  `REF_SCHEMA_MANIFEST_PINNING_MISSING`,
  `REF_SCHEMA_RESERVED_CCS`, `REF_SCHEMA_TYPE_MISMATCH`). The
  seventh code (`REF_SCHEMA_PARSE_ERROR`) is named at module
  level but emitted by `pep.py` at the PEP boundary in
  VL-019. All three VL-017b candidates were resolved with
  explicit rationale per the citation discipline: Candidate 3
  (parse-order API contract) superseded by spec+test direct
  read (parsed-dict contract); Candidate 1 (seventh code
  status) superseded by Candidate-3 coupling (named-but-not-
  emitted approach taken); Candidate 2 (generic unknown keys
  inside `interaction`) upgraded to real spec gap (G14) with
  provisional `REF_SCHEMA_TYPE_MISMATCH` mapping pending spec
  edit. Validator verified in-container against 26/27
  discriminating tests plus the positive case; the 27th
  (parse-error) is structurally VL-019's domain. Validator
  does NOT touch `pep.py`; G2 closes on VL-019.
- **PEP wired to validator; G2 closed in code (VL-019).**
  `IMPLEMENTATION/pep.py` replaced wholesale per
  `SPEC/request_schema.md` build-order step 4. The endpoint
  reads the raw JSON body (no Pydantic body model), parses
  with `json.loads` (emitting `REF_SCHEMA_PARSE_ERROR` on
  decode failure), calls `validate_request()` on the parsed
  dict, and passes the normalized interaction to
  `evaluate()` only after schema acceptance. The seven-code
  schema vocabulary is fully realized: six codes emitted by
  the validator (VL-018), the seventh
  (`REF_SCHEMA_PARSE_ERROR`) emitted by the PEP boundary.
  Architectural deviation from the VL-019 session intent
  documented in the ledger entry: the planned
  Pydantic-model-with-RequestValidationError-handler
  architecture failed 4/27 tests because Pydantic silently
  drops extra top-level keys, making the validator's flat-
  key and top-level-CCS-shaped-key refusals structurally
  unreachable. Raw-body architecture sidesteps the
  Pydantic-as-filter concern. In-container verification:
  27/27 schema tests passing; 23/23 evaluator regression
  passing; TESTS/test_pep.py migrated to new wire shape (4/4
  passing; three of four previously passing-by-accident at
  schema-layer 403 rather than at the evaluator/upstream
  behavior they were written to test); 54/54 in-container,
  61/61 in repo. Evidence at
  `EVIDENCE/proofs/g2_pep_wiring_001.log` (raw pytest
  output). The evaluator-layer refusal payload is preserved
  from pre-VL-019 pep.py (`{terminal_state: REFUSE}` without
  a `refusal_reason_code`) because VL-019's scope is
  schema-layer wiring; evaluator-layer refusal vocabulary is
  not specified by SPEC/request_schema.md and is not
  introduced here.
- **VL-020 artifact 05 freshness pass; methodology Lesson 5
  promoted; schema stale forward-reference corrected
  (commit d81de1d).** `docs/restructure/05_admissibility_envelope_spec.md`
  absorbs the canonical wire shape locked by VL-014..VL-019.
  The envelope's `request_context` block gains `context`
  (canon section 11.1 `C`) between `OP` and
  `expected_manifest_version`; the envelope top level gains
  `target_url` between `decision` and `canon`. Two
  field-rationale bullets appended in JSON-block-order.
  Two queue-drain items bundled per VL-013's freshness-pass
  scope rule: `docs/methodology/session_mechanics_lessons.md`
  gains Lesson 5 (set-exhaustiveness claims require explicit
  enumeration; three VL-019 surface events: Pydantic
  architecture skip, 23/23 regression-set scope claim,
  `grep -P` MINGW64 flag-set rejection; failure mode
  characterized distinctly from Lesson 3 source-first);
  `SPEC/request_schema.md` "Build order (schema-internal)"
  closing paragraph corrected from pre-VL-015 numbering plan
  (VL-014..VL-018) to actual numbering (VL-014..VL-020).
  Single focused str_replace in the schema per session intent;
  second stale forward-reference at the schema's line 457
  surfaced as a process finding and deferred to a separate
  small commit. No code/canon/test change. Repo test set
  61/61, unchanged from VL-019.
- **VL-020 follow-up STATE.md and ledger append; delivery-
  omission repair (this commit).** VL-020's commit d81de1d
  landed the three structural-edit files but omitted the
  STATE.md update and the ledger entry append; the Step 8
  paste contained comment-form action items for both that
  were silently skipped at execution. This follow-up commit
  applies the STATE.md edits and appends both the VL-020 and
  VL-020 follow-up ledger entries. Third instance of the
  chat-paste-eats-content failure mode named in
  `docs/methodology/session_mechanics_lessons.md` (VL-016
  follow-up lessons (a) and (b)). No code/canon/test change.
- **VL-021 schema line-457 stale forward-reference
  correction (commit cbb428b).** The second stale
  forward-reference in `SPEC/request_schema.md`, surfaced
  by VL-020's source-read pass and deferred per
  strict-scope discipline, is corrected. The "Decided
  downstream tasks / Feed-back to envelope spec
  (Deliverable 05)" section's parenthetical reference is
  rewritten from forward-tense pre-VL-020 numbering
  ("proposed VL-018, after the VL-014..VL-017 schema-work
  entries below") to past-tense citing the actual landing
  ("recorded at VL-020, after the VL-014..VL-019
  schema-work entries"). Single focused str_replace; same
  family as VL-020's closing-paragraph correction. No
  code/canon/test/structural-doc change. Repo test set
  61/61, unchanged from VL-020 follow-up.
- **VL-021 follow-up STATE.md and ledger append;
  delivery-omission repair (commit 79feab9).** VL-021's
  commit cbb428b landed the schema edit but omitted the
  STATE.md update and the ledger entry append. This
  follow-up commit applies the STATE.md edits with
  anchors verified against the actual file content and
  appends both the VL-021 and the VL-021 follow-up ledger
  entries. Items 15 and 16 of "Next open action" landed
  in 79feab9; this current-verified-state bullet pair and
  the last-updated parenthetical landed in a separate
  follow-up commit after edits 1 and 2 of the original
  apply-script were observed to apply to disk but not
  survive to staging in 79feab9 (mechanism undiagnosed;
  treated as a session-mechanics finding for a future
  ledger entry). Fifth instance of the chat-paste-eats-
  content failure mode family. No code/canon/test change.
- **VL-022 throwaway-session methodology promotion (this
  commit).** Two deliverables from the bridge document of
  2026-05-19: (1) new file
  `docs/methodology/cross_model_evaluate_template.md` - a
  fourth methodology template for framework-level
  evaluation under derivation discipline, paralleling the
  three existing methodology templates and incorporating
  the constraint-bounding caveat Lesson 6 motivates; (2)
  Lesson 6 appended to
  `docs/methodology/session_mechanics_lessons.md` - the
  presentation-indistinguishability failure mode
  (constraint enforcement in cross-model output is
  prompt-bounded, not model-bounded) and its corrective
  rule (verify scope discipline within the response body,
  not just at its opening confirmation). Both deliverables
  promoted on single-instance basis with explicit
  acknowledgment; rationale recorded in the VL-022 ledger
  entry. Finding 3 from the bridge (recursive-continuity
  hypothesis) NOT in this commit's scope; parked for
  VL-023, which requires fresh artifact reading without
  reference to the bridge document or surface-event model
  phrasing per the bridge's prescription. This entry also
  absorbs the audit trail for commit 37a4390 (the VL-021
  follow-up 2 recovery) per option B of the VL-022
  scoping decision; the disappearance mechanism that
  necessitated 37a4390 is documented in the VL-022 ledger
  entry as an open methodology investigation.
  Classification: efficiency move per VL-017a's
  distinction. No code/canon/test/spec/structural-doc
  change. Repo test set 61/61, unchanged from 37a4390.
- **VL-023 recursive-continuity hypothesis derivation:
  PARTIAL HOLDS (this commit).** Finding 3 from the bridge
  document of 2026-05-19, deferred to VL-023 by VL-022 per
  the bridge's prescription that the model's phrasing not
  be imported. Derivation conducted in a fresh session
  without the bridge document, the throwaway chat
  transcript, or the outside model's output in working
  context. A four-part abstract shape extracted from canon
  section 12 (state + enumerated transitions +
  invalidation/revalidation mechanism + fail-closed on
  unverified continuation) applied to the five candidate
  layers the session opener named: decision layer
  (definitionally; build half open per G0), manifest layer
  (with the transition-shape being part of canonical CCS,
  not a separate invariant), methodology layer (procedural
  detector via ledger discipline plus no-prose-promotion
  rule), and session layer (procedural detector via close
  + resume protocols) all fit. Request layer does NOT fit:
  no transition concept; it is a precondition layer, not a
  continuity layer. Hypothesis closes with PARTIAL HOLDS;
  downstream-artifact candidate
  (`docs/restructure/07_continuity_recursion.md` naming
  the four fitting layers) flagged in process findings,
  NOT committed in this entry, with recommendation to
  schedule post-G0-build. Classification: methodology /
  analysis entry per VL-017a's distinction. No
  code/canon/test/spec/structural-doc change. Repo test
  set 61/61, unchanged from 37a4390 (VL-022).
- **VL-023 follow-up cross-model evaluation: convergent
  on PARTIAL HOLDS; one supplementary finding (this commit).**
  First framework-level cross-model evaluation under the
  VL-022 template (drafted from inference about the template
  structure; Lesson 3 inference flag at top of the request).
  Recipient model produced a procedurally-clean response per
  VL-008 + Lesson 6 within-body discipline. Four-part abstract
  shape extracted independently from canon section 12 matches
  VL-023's extraction exactly in components and citations. All
  five original per-layer verdicts converge: decision fits
  definitionally, manifest fits with CCS-application
  refinement, request does NOT fit, methodology fits via
  procedural detector, session fits via procedural detector.
  Outcome classification: PARTIAL HOLDS, matching VL-023.
  One supplementary divergence finding: evaluator versioning
  layer added as a sixth fitting layer per artifact 05's
  `evaluator` block field rationale citing canon section
  12.4-class transition, with one minor inference caveat on
  its fail-closed component (artifact-recoverable from the
  envelope's overall fail-closed posture; flagged for
  precision). VL-023's PARTIAL HOLDS strengthened from
  single-model to two-model converged derivation; the
  `07_continuity_recursion.md` artifact candidate (if/when
  eventually drafted post-G0-build) should incorporate the
  evaluator versioning layer per this entry's recommendation.
  Classification: methodology / analysis entry per VL-017a's
  distinction. No code/canon/test/spec/structural-doc change.
  Repo test set 61/61, unchanged from 83fa5a7 (VL-023).
- **VL-024 strengthening derivation: STRENGTHENS bounded to
  layers B and C (this commit).** Methodology / analysis entry
  deriving whether the cross-model run at VL-023 follow-up
  strengthens the framework's claim of recursive continuity
  discipline. Four-step structure per session opener: Step 1
  decomposed `strengthen` against VL-023 follow-up's stated
  accomplishments (Passages A, B, C of that entry) per Lesson 5
  set-exhaustiveness, producing three load-bearing sub-meanings
  (confidence, scope, methodology-pattern durability) after
  collapsing opener-(iii) risk-reduction into (i) and deferring
  opener-(iv) external defensibility to Step 4. Step 2 derived
  each sub-meaning with citations: (i) confidence strengthens
  materially on the abstract shape and the load-bearing
  request-layer exclusion, bounded by the shared-bundle caveat
  which is the strongest test the framework's methodology
  specifies; (ii) scope expands by one fitting layer (evaluator
  versioning) with one artifact-recoverable inference caveat,
  PARTIAL HOLDS verdict unchanged with fitting set now five;
  (iii) methodology-pattern durability strengthens with two
  effects - cross-model evaluate template now meets two-instance
  threshold per session_mechanics_lessons.md line 47, and the
  methodology layer's recursive-continuity instance is now
  operative rather than merely observable. Step 3 synthesized
  via Layer A/B/C decomposition of framework purposes (Layer A
  = declared purpose per canon sections 1, 6, 14; Layer B =
  epistemic discipline per VL-008 plus the no-prose-promotion
  rule plus SESSION_PROTOCOL.md lines 84-86; Layer C =
  reading-aid track per the `07_continuity_recursion.md`
  candidate and STATE.md's entry-point role). Verdict:
  STRENGTHENS, bounded to layers B and C; explicitly does NOT
  extend to layer A. The verdict refines VL-023 follow-up's
  unqualified `strengthened` framing (entry line 5237) to an
  explicit layer-bounded form. Step 4 recorded five implications:
  (1) `07_continuity_recursion.md` composition to include
  evaluator-versioning as fifth fitting layer with detector-type
  distinction made explicit; (2) VL-025 envelope.py build
  attention to `reassert()`'s handling of `evaluator_sha256` as
  load-bearing for the evaluator-versioning layer's fit; (3)
  external defensibility strengthens in proportion to current
  readership scope (bounded), becomes load-bearing contingent on
  G3 status change; (4) cross-model evaluate template's
  single-instance language now removable per two-instance
  threshold met, efficiency move queue-drain candidate; (5)
  derivation-over-absorption verdict-refinement as first
  instance of candidate methodology pattern (VL-024 itself is
  the first instance), two-instance threshold not yet met.
  Classification: methodology / analysis entry per VL-017a's
  distinction. No code/canon/test/spec/structural-doc change.
  Repo test set 61/61, unchanged from 49b797a (VL-023 follow-up).
- **VL-025 G0 build half: canonical CCS implementation via envelope.py (this commit).** `IMPLEMENTATION/envelope.py` lands per
  `docs/restructure/05_admissibility_envelope_spec.md` build-order
  step 3. Two functions: `build_envelope()` constructs the envelope
  dict matching artifact 05's Envelope structure section, with every
  field cited to a specific artifact 05 passage or canon clause (see
  VL-025's Spec-citation map). `reassert()` implements the five-row
  Reassertion protocol table with each branch cited to its table row
  in table order (see VL-025's Reassertion-protocol mapping).
  Integration boundary one-sided per opener risk-reduction observation
  1: envelope.py imports `manifest_sha256` from evaluator.py and is
  not imported by evaluator.py or pep.py in this commit. Option A
  integration locked pre-build: condition booleans (ac3, t26,
  manifest_integrity) are caller-supplied parameters; envelope.py
  does NOT call the condition functions itself. `reassert()` is pure
  with respect to the envelope (reads live file hashes, does not
  modify input). `ensure_ascii=True` per VL-009 with divergence from
  receipt.py's `ensure_ascii=False` recorded as gap candidate 4 (second
  instance of the VL-012 receipt.py finding; methodology two-instance
  threshold now met). `condition_results.ccs` is None on first issuance
  per artifact 05 open question 1, locked by opener constraint (e);
  the reassert-time ccs boolean's owner is recorded as gap candidate 1
  for spec edit before VL-027. **VL-024 Implication 2 converted from
  inference to direct citation in code**: reassert() Row 3 (evaluator
  _sha256 mismatch -> RE-EVALUATE-REQUIRED, canon basis section 12.4)
  resolves the evaluator-versioning fail-closed inference flag from
  VL-023 follow-up lines 5200-5210; the inference caveat dissolves on
  direct read of artifact 05's reassertion table and the build
  instantiates the exact mapping. Five gap candidates total recorded
  (none blocking): (1) condition_results.ccs reassertion semantic, (2)
  evaluate aggregate return shape vs condition_results needs, (3)
  canon section 12.3 c_{t+1} vs T^26 relationship, (4) ensure_ascii
  divergence from receipt.py, (5) canon_sha256 lockfile-read vs
  canon.md hash recomputation design choice. Pre-commit smoke test
  exercised the integration boundary end-to-end (validator ->
  evaluator condition functions -> build_envelope -> reassert across
  all 5 table rows plus determinism plus timestamp-invariance plus
  purity); 7/7 checks passed; smoke test not committed (VL-026 owns
  test artifacts). Repo test set 61/61, unchanged from c944a76
  (VL-024); envelope.py has no callers in pep.py yet so no test
  regression possible. Build-resumption template's second behavioral
  instance and first with Claude as executing agent; two-instance
  threshold per session_mechanics_lessons.md line 47 met for
  build-resumption-as-protocol (paralleling VL-024's threshold met
  for cross-model evaluate template). G0 build half transitions from
  OPEN to PARTIALLY RESOLVED with the envelope-construction-and-
  reassertion portion landed; pep.py wiring remains open for VL-027.
  Canonical CCS in 06_spec_to_code_traceability.md transitions from
  UNIMPLEMENTED to PARTIALLY IMPLEMENTED for the envelope.py portion;
  structured artifact 06 update deferred to a follow-up commit
  paralleling VL-018's pattern. Layer A change per VL-024's bridge
  proposition; canon section 12 has a deterministic implementation
  in code for the first time in the project's history. Classification:
  trajectory move per VL-017a's distinction.
- **VL-025 follow-up cross-model verification of envelope.py against artifact 05 and canon section 12-13 (this commit).** Two-bundle, two-recipient cross-model verification of VL-025 under VL-008 + Lesson 6 with Grok and OpenAI as recipients. Bundle A verifies
  envelope.py's structural fidelity to
  `docs/restructure/05_admissibility_envelope_spec.md`; Bundle B
  verifies `reassert()`'s behavior against `CANON/canon.md`
  sections 12.1-12.4 and 13. Four verifier-runs total; all
  procedurally clean per VL-008 (a)+(b) and Lesson 6 within-body
  discipline. One re-request for response-mechanism truncation
  (OpenAI Bundle A first run truncated mid-section-4; re-requested
  with explicit "respond in full" instruction; re-run clean).
  **Substantive convergence across all four runs**: no Divergence
  and no Code-absent classifications anywhere; envelope.py honors
  the intent of both artifact 05 and canon section 12-13. **VL-024
  Implication 2 fully confirmed**: Row 3 (evaluator_sha256
  mismatch -> RE-EVALUATE-REQUIRED) directly authorized by canon
  section 12.4 per both Bundle B verifiers; the inference flag at
  the methodology layer on evaluator-versioning's fail-closed
  component (VL-023 follow-up lines 5200-5210) is now two-model-
  converged and can be retired in any subsequent
  `07_continuity_recursion.md` draft. **Classification divergence**:
  Grok's Match outcomes (both bundles) vs. OpenAI's Different-set
  outcomes (both bundles) reflect a Match-criterion divergence,
  not a substantive divergence: Grok treats authorization-by-
  design-space as Match; OpenAI treats only authorization-by-
  direct-naming as Match. The pattern is structural across both
  bundles; two-instance threshold per session_mechanics_lessons.md
  line 47 met for a verification-request-template Match-criterion
  clarification. **Six gap candidates surfaced**, none blocking:
  (1) artifact 05 should specify `ensure_ascii=True` per VL-009 -
  this is VL-025 gap candidate 4 confirmed by OpenAI Bundle A; (2)
  artifact 05 should specify `reassert()` purity contract - new,
  not in VL-025's gap-candidate list; (3) artifact 05 could specify
  defensive AP/OP copy semantics - new, minor; (4) module-level
  path constants `CANON_LOCK_PATH`/`EVALUATOR_PATH` recorded as
  deliberate non-spec choice per VL-012 discipline pattern; (5)
  artifact 05's Canon-mapping table Row 2 (tamper detection) needs
  rewording to acknowledge artifact-05-layer mechanism rather than
  direct canon-clause instantiation - new, load-bearing; (6)
  first-issuance ccs initialization semantic is canon-underdetermined
  - overlaps with VL-025 gap candidate 1 and resolvable via same
  spec edit. **Four methodology process findings**: (i) verification
  request template Match-criterion ambiguity is load-bearing across
  both bundles; (ii) absence-of-Divergence and absence-of-Code-absent
  are themselves derivation outcomes worth elevating in the template's
  rubric language; (iii) response truncation handling needs explicit
  length instruction in submission-format wording; (iv) scope check
  enumeration discipline (per-concept vs grouped) needs clarification.
  **Status implications**: no code-correction needed (envelope.py is
  verified correct); one spec-clarification batch needed before
  VL-027, combining VL-025 gap candidate 1 plus this entry's gap
  candidates 1, 2, 3, 5, 6 into a single artifact 05 spec-revision
  commit; VL-026 (canon-derived tests) is not blocked and may use
  Bundle B verifier-runs' per-branch canon citations as the
  authoritative source for `test_ccs_canonical.py` docstrings.
  Verifier responses recorded by reference per VL-015/VL-016/VL-023
  follow-up precedent (not committed as standalone artifacts).
  Classification: methodology / analysis entry per VL-017a's
  distinction. No code/canon/test/spec/structural-doc change in
  this commit. Repo test set 61/61, unchanged from 096c933
  (VL-025).

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
11. **Schema validator committed.** Done (VL-018, commit
    cc08844; follow-up f24c837).
    `IMPLEMENTATION/request_validator.py` per the schema's
    build-order step 3. Validator accepts a parsed dict and
    emits six refusal codes; the seventh (parse-error) is
    structurally VL-019's domain. Three VL-017b candidates
    resolved with rationale; G14 surfaced as a new gap.
12. **PEP wired to validator; G2 closed in code.** Done
    (VL-019, this commit). `IMPLEMENTATION/pep.py` replaced
    wholesale per `SPEC/request_schema.md` build-order step
    4. Raw-body endpoint architecture (not the Pydantic-model
    architecture the session intent specified; rationale in
    the VL-019 ledger entry). TESTS/test_pep.py migrated to
    the new wire shape (4/4 passing; three of four previously
    passing-by-accident; corrected in this commit). 54/54
    in-container; 61/61 in repo.
    Evidence at `EVIDENCE/proofs/g2_pep_wiring_001.log`.
13. **Artifact 05 freshness pass; methodology Lesson 5; schema
    stale-ref.** Done (VL-020, commit d81de1d).
    `docs/restructure/05_admissibility_envelope_spec.md`
    absorbs `context` (canon section 11.1 `C`) and `target_url`
    from the schema work track. Two bundled queue-drain items:
    `docs/methodology/session_mechanics_lessons.md` Lesson 5
    promotion, and `SPEC/request_schema.md` closing-paragraph
    stale-reference correction. No code/canon/test change.
14. **VL-020 follow-up: STATE.md and ledger append;
    delivery-omission repair.** Done (VL-020 follow-up,
    this commit). Commit d81de1d landed the three structural
    files but omitted STATE.md and the ledger entry; the
    Step 8 paste's comment-form action items were silently
    skipped. This commit applies the STATE.md edits and
    appends both the VL-020 and VL-020 follow-up ledger
    entries. Third instance of the chat-paste-eats-content
    failure mode.
15. **VL-021 schema line-457 stale forward-reference
    correction.** Done (VL-021, commit cbb428b). Single
    str_replace in `SPEC/request_schema.md` rewriting the
    "record the pass in the ledger" parenthetical from
    forward-tense pre-VL-020 numbering to past-tense
    citing VL-020. Bookkeeping commit; the schema edit
    landed correctly but the STATE.md update and ledger
    append did not (see item 16). Trajectory orthogonal
    to G0 build half and to the in-flight throwaway-
    session methodology promotion (VL-022 next).
16. **VL-021 follow-up: STATE.md and ledger append;
    delivery-omission repair.** Done (VL-021 follow-up,
    this commit). cbb428b's apply-script for STATE.md
    aborted at edit 2 because its anchor was reconstructed
    from session-opener terminal scrollback rather than
    from disk; edit 1's on-disk change was lost in
    between-edits before staging; the ledger-append cat
    failed on a path that did not exist locally. This
    follow-up commit applies the STATE.md edits with
    anchors verified against the actual file content and
    appends both the VL-021 and this VL-021 follow-up
    ledger entries. Fifth instance of the chat-paste-eats-
    content failure mode family.
17. **VL-022 throwaway-session methodology promotion.**
    Done (VL-022, this commit). Two deliverables from
    the bridge document of 2026-05-19: new file
    `docs/methodology/cross_model_evaluate_template.md`
    (Finding 1, cross-model evaluate template refined
    with the constraint-bounding caveat) and Lesson 6
    appended to
    `docs/methodology/session_mechanics_lessons.md`
    (Finding 2, presentation-indistinguishability
    failure mode). Single-instance promotion with
    explicit acknowledgment. Finding 3 (recursive-
    continuity hypothesis) NOT in scope; parked for
    VL-023 (requires fresh session per bridge
    prescription). VL-022 ledger entry also absorbs the
    37a4390 disappearance-mechanism finding per option
    B of the scoping decision. Classification:
    efficiency move per VL-017a's distinction. No
    code/canon/test/spec/structural-doc change.
18. **VL-023 recursive-continuity hypothesis derivation.**
    Done (VL-023, this commit). Finding 3 from the bridge
    document of 2026-05-19, conducted in a fresh session
    per the bridge's prescription. Outcome: PARTIAL HOLDS
    (four of five candidate layers fit the four-part
    continuity shape extracted from canon section 12;
    request layer does not). Downstream-artifact candidate
    (`docs/restructure/07_continuity_recursion.md` naming
    the four fitting layers) flagged for post-G0-build
    scheduling; NOT committed in this entry per session
    opener's "Outcome and submission" rule. Classification:
    methodology / analysis entry per VL-017a's distinction.
    No code/canon/test/spec/structural-doc change.
19. **VL-024 strengthening derivation.** Done (VL-024,
    this commit). Methodology / analysis entry deriving the
    strengthening claim implicit in VL-023 follow-up's
    self-description. Four-step structure: Step 1 decomposed
    `strengthen` against the source-of-truth (Passages A, B,
    C of VL-023 follow-up) per Lesson 5 set-exhaustiveness,
    producing three load-bearing sub-meanings (confidence,
    scope, methodology-pattern durability) after collapsing
    opener-(iii) risk-reduction into (i) and deferring
    opener-(iv) external defensibility to Step 4. Step 2
    derived each sub-meaning with citations. Step 3
    synthesized via Layer A/B/C decomposition of framework
    purposes. Step 4 recorded five downstream implications.
    Outcome: STRENGTHENS, bounded to layers B (epistemic
    discipline) and C (reading-aid track); explicitly does
    NOT extend to layer A (declared purpose / gate behavior).
    The verdict refines VL-023 follow-up's unqualified
    `strengthened` framing (entry line 5237) to an explicit
    layer-bounded form. First instance of a derivation-
    over-absorption methodology-layer entry; Implication 5
    of this entry's Step 4 records the pattern as a
    candidate for `session_mechanics_lessons.md` addition on
    the next instance (two-instance threshold not yet met).
    Classification: methodology / analysis entry per
    VL-017a's distinction. No code/canon/test/spec/
    structural-doc change.
20. **G0 build half: canonical CCS implementation via the
    envelope spec.** Done at the envelope-construction-and-
    reassertion layer (VL-025, this commit); PARTIALLY
    RESOLVED overall. `IMPLEMENTATION/envelope.py` lands per
    `docs/restructure/05_admissibility_envelope_spec.md`
    build-order step 3 with `build_envelope()` and
    `reassert()`. Option A integration locked pre-build:
    condition booleans (ac3, t26, manifest_integrity) are
    caller-supplied parameters; envelope.py imports only
    `manifest_sha256` from evaluator.py and is not imported
    by evaluator.py or pep.py at VL-025. `reassert()` is
    pure with respect to the envelope (reads live file
    hashes, does not modify input). `ensure_ascii=True` per
    VL-009 with divergence from receipt.py's
    `ensure_ascii=False` recorded as gap candidate 4 (second
    instance of the VL-012 receipt.py finding).
    `condition_results.ccs` is None on first issuance per
    artifact 05 open question 1, locked by opener constraint
    (e); the reassert-time ccs boolean's owner is gap
    candidate 1 for spec edit before VL-027. VL-024
    Implication 2 (evaluator-versioning fail-closed posture)
    converted from inference to direct citation at
    `reassert()` Row 3 (evaluator_sha256 mismatch ->
    RE-EVALUATE-REQUIRED, canon basis section 12.4). Five
    gap candidates total recorded, none blocking. Pre-commit
    smoke test exercised the integration boundary end-to-end
    (validator -> conditions -> build_envelope -> reassert
    across all 5 table rows in order plus determinism plus
    timestamp-invariance plus purity); 7/7 checks passed.
    Tests are VL-026's domain (item 21); pep.py wiring is
    VL-027's domain (item 22). After VL-027 the G0 build
    half closes completely and the
    `07_continuity_recursion.md` artifact candidate becomes
    schedulable per VL-023's post-G0-build recommendation.
21. **G0 build half (cont.): canon-derived tests for the
    envelope.** OPEN. Next trajectory action after VL-025.
    Per artifact 05 build-order step 4:
    `TESTS/adversarial/test_envelope.py` (construction
    determinism, the reassertion table, tamper detection)
    plus a canon-derived `test_ccs_canonical.py` citing
    canon section 12 directly (the honest G0 signal that
    should fail until VL-025 lands - now eligible to pass).
    The smoke test patterns demonstrated at VL-025
    (determinism, timestamp-invariance, the five-row
    reassertion table, reassert() purity) translate into
    the pytest surface for VL-026. G7 (tests are code-
    derived, not canon-derived) partially closes for the
    envelope domain via the canon-derived test file.
    Proposed ledger entry: VL-026.
22. **G0 build half (cont.): pep.py wires to emit envelopes
    per decision; G7 close.** OPEN. Per artifact 05
    build-order step 5. Resolves gap candidate 1 from VL-025
    (the condition_results.ccs reassertion semantic; spec
    edit to artifact 05 named there as a prerequisite for
    this entry) and gap candidate 2 (the evaluate aggregate
    return vs condition_results needs; the choice between
    pep.py-calls-condition-functions vs. evaluator-refactor-
    to-structured-return is made here). After VL-027,
    canonical CCS in
    `docs/restructure/06_spec_to_code_traceability.md`
    transitions from PARTIALLY IMPLEMENTED to IMPLEMENTED;
    G0 closes completely; G7 closes for the envelope domain.
    The `07_continuity_recursion.md` artifact candidate
    becomes eligible for scheduling. Proposed ledger entry:
    VL-027.

With priority item 3 (G0 rename + G6 + G10) resolved, item
4 (SPEC/request_schema.md drafted + verified + corrected)
complete, the failing-tests sub-step of item 4 done (VL-017),
the build-resumption invocation tested against two models
(VL-017b), the validator committed (VL-018), and the PEP wired
to the validator with G2 closed in code (VL-019), the
remaining order is:
VL-020 artifact 05 freshness pass (absorbs `context` and
`target_url` into the envelope spec), then G0 build (canonical
CCS via envelope), G7 (canon-derived tests), G3 (reframe public
materials once 06 makes the FULL/PARTIAL/DRIFTED picture
concrete), then bookkeeping batch (G1, G8, G9, G11, G14), then
build-outward scope (G4, G5).

Suggested next move: a small queue-drain commit correcting the
second stale forward-reference in `SPEC/request_schema.md` at
line 457 of the post-VL-020 file (the "Decided downstream tasks
/ Feed-back to envelope spec (Deliverable 05)" section's
parenthetical "proposed VL-018, after the VL-014..VL-017
schema-work entries below" -> actual "proposed VL-020, after
VL-014..VL-019"). Surfaced by VL-020's source-read pass;
deferred per strict-scope discipline. Single focused
str_replace; same family as VL-019's deferred artifact-04
G2-RESOLVED row update and the still-pending G14 spec edit.
Bundle one or more of these into a small bookkeeping commit
if convenient; otherwise schedule each individually. After the
queue drain, the next trajectory action is the G0 build half:
canonical CCS implementation via the envelope spec (now
current at VL-020). Proposed ledger entry for the next
queue-drain: VL-021.

Decisions parked for resolution: open question 5 of
SPEC/request_schema.md (artifact 05 absorbs `context` and
`target_url`) was resolved by VL-020 (commit d81de1d). The
other four open questions from VL-014's draft were resolved
by VL-016's corrections. No VL-014-originated open questions
remain.

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
- VL-017b candidate finding 1: seventh refusal code's status.
  RESOLVED in VL-018 via Candidate-3 coupling: validator names
  all seven codes at module level; emits six; the seventh
  (`REF_SCHEMA_PARSE_ERROR`) is named here for VL-019's
  pep.py import. SUPERSEDED status; no artifact-04 row.
- VL-017b candidate finding 2: generic-unknown-key handling
  inside `interaction`. UPGRADED in VL-018 to real spec gap
  G14 (two surface events: VL-017 test author + VL-017b
  OpenAI). Validator handles provisionally with
  `REF_SCHEMA_TYPE_MISMATCH`. Spec edit pending; separate
  forthcoming commit per spec-defines-the-rename pattern.
- VL-017b candidate finding 3: parse-order API-vs-procedure
  separation. RESOLVED in VL-018 by spec+test direct read:
  validator accepts already-parsed dict; parse-error handling
  is VL-019's domain at the FastAPI/Pydantic layer.
  SUPERSEDED status; no artifact-04 row.
- VL-017b process finding: verbosity-as-deflection in
  methodology questions. The decision to record this test ran
  longer in methodology argument than the test produced
  findings. Claude-side behavior pattern worth flagging;
  candidate addition to a future session-mechanics-lessons
  artifact, distinct from VL-017's environment-side
  friction-point findings.
- VL-017b process finding: build-resumption template revision
  from first use. Item 5 of Submission format now requires
  explicit 'None' enumeration when no gap candidates exist,
  rather than allowing the section to be skipped. The first
  use surfaced this because one model reported 'None' and the
  other reported two gap candidates; the asymmetry is
  procedurally informative only when both cases are explicit.
  Revision incorporated into the committed template; recorded
  here for traceability.
- VL-020 process finding: a second stale forward-reference
  exists in `SPEC/request_schema.md` at line 457 of the
  post-VL-020 file ("proposed VL-018, after the VL-014..VL-017
  schema-work entries below"; actual: "proposed VL-020, after
  VL-014..VL-019"). VL-020 corrected the closing-paragraph
  stale reference per strict-scope discipline; this second
  reference is deferred to a small queue-drain commit. Not
  blocking.
- VL-020 process finding: Lesson 3 fire pre-commit. The first
  draft of `apply_vl020.py` was written from inference about
  the apply-script template pattern, without viewing the
  actual template source. The template was uploaded
  mid-session; comparison surfaced eight structural
  divergences from the established pattern. The script was
  rewritten from scratch against the template; the rewritten
  script preserves the template's signature and calling
  convention. Did not materialize as committed divergence
  (caught pre-commit). Adding the VL-020 surface event to
  Lesson 3's "Surface events" subsection of
  `docs/methodology/session_mechanics_lessons.md` is deferred
  per VL-020's strict-scope discipline; the ledger entry's
  process findings hold the authoritative record until a
  future methodology-file update lands.
- VL-020 follow-up process finding: third instance of the
  chat-paste-eats-content failure mode (VL-012, VL-014,
  VL-016 follow-up are the prior instances; this is the
  third named in session-mechanics terms). VL-020's Step 8
  paste contained two comment-form action items (apply
  STATE.md edits; cat ledger entry) that were silently
  skipped at execution. The commit d81de1d landed with the
  three structural-edit files but without STATE.md or the
  ledger entry. Recovery via follow-up commit per VL-018 /
  VL-019 follow-up precedent (no history rewrite). The
  lessons in `docs/methodology/session_mechanics_lessons.md`
  on this failure mode (VL-016 follow-up lessons (a) and
  (b)) fired correctly when the divergence was diagnosed
  post-commit but did not prevent the divergence at execution
  time. Calibration finding: lessons currently structured as
  "don't paste multi-step blocks with comment-form action
  items" require Claude-side discipline in *generating* the
  Step 8 instructions; a complementary discipline (workflow
  steps that fail loud if skipped, not silently) would catch
  the case where the discipline is forgotten. Candidate
  methodology update: when generating multi-step recovery
  or workflow instructions, prefer apply-scripts (which
  exit nonzero on skip) over prose comments in pasted shell
  blocks. Not actioned in this commit per strict-scope.

---

## Known open gaps

See `docs/restructure/04_current_vs_claimed.md` for the full list. Summary:

- **G0** - CCS specification/implementation drift. **PARTIALLY RESOLVED**
  (VL-012): rename half closed (function renamed; name reserved in code
  and test IDs). Build half open (canonical CCS implementation is the
  G0 build track).
- **G1** - README test count stale / no commit-pinned source of truth.
- **G2** - request schema drift (interception proofs document a dead API).
  **RESOLVED** (VL-014 + VL-015 + VL-016 + VL-017 + VL-018 + VL-019):
  SPEC/request_schema.md names the rejected and accepting
  shapes at the schema layer (VL-014), has been
  cross-model-verified (VL-015), and the disputed interpretive
  loci have been corrected (VL-016). VL-017 added 27 failing
  schema-shape tests at
  `TESTS/adversarial/test_request_schema.py` per the schema's
  build-order step 2. VL-018 added the schema validator at
  `IMPLEMENTATION/request_validator.py` per step 3, emitting
  six refusal codes. VL-019 wired the validator into
  `IMPLEMENTATION/pep.py` per step 4, emitting the seventh
  refusal code (`REF_SCHEMA_PARSE_ERROR`) at the boundary;
  the 27 discriminating tests transition from uniform-422
  (VL-017) to per-code discrimination (27/27 passing). The
  artifact-04 update reflecting G2's RESOLVED status is
  deferred to a follow-up commit (paralleling VL-018's
  artifact-04-as-separate-commit choice).
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
- **G14** - unknown-key refusal code under-determination inside
  `interaction`. **PARTIALLY ADDRESSED** (VL-018): the spec
  rejects CCS-shaped fields with `REF_SCHEMA_RESERVED_CCS` and
  rejects flat-key collisions at the TOP level with
  `REF_SCHEMA_FLAT_KEYS`, but does not enumerate a refusal
  code for non-CCS-shaped unknown keys inside `interaction`.
  Two surface events: VL-017 (test author's module docstring)
  and VL-017b (OpenAI's Candidate 2). VL-018's validator
  refuses such keys with `REF_SCHEMA_TYPE_MISMATCH` as the
  closest extant code; the mapping is provisional. Spec edit
  pending: either add `REF_SCHEMA_UNKNOWN_KEY` or formalize
  the TYPE_MISMATCH overload. Separate forthcoming commit per
  the spec-defines-the-rename pattern (candidate GR-2).

Resolved in VL-012: G6 (`ccs_valid` field removed), G10 (pinning
fields retained and documented). G0's rename half. See VL-012 and
`docs/restructure/04_current_vs_claimed.md` Resolved gaps section.

---

## Session-close note

This file is updated as the last step of each working session. The "Next open
action" and "Current verified state" sections must reflect reality at the time
of the last commit. If they do not, the repository's continuity is broken -
treat that as the first thing to fix.
