# Elyon-Sol - Verification Ledger

Append-only record of how claims about Elyon-Sol became trusted.

## Rules
- A claim enters as SINGLE-SOURCE when first derived.
- A claim becomes CONFIRMED only when independently re-derived FROM PRIMARY
  SOURCES (canon, code) - never from an artifact that merely asserts it.
- A verdict or rating ("approved", "8.7/10") is NEVER a confirmation event
  and is never recorded here as one. Only derivations against primary sources are.
- Entries are append-only. Corrections are new entries, not edits.
- Each entry cites the sources and, where one exists, the commit hash.

## Status values
SINGLE-SOURCE | CONFIRMED | DISPUTED | RETRACTED | CORRECTED

---

## Entries

### VL-001 - Ledger established
- Date: 2026-05-14
- Event: Verification ledger created.
- Note: Entries VL-002..VL-005 record verification work performed during the
  Rev. 2 restructure session, which PREDATES this ledger. Those verifications
  reference primary sources by version, not by commit hash, because they were
  performed before the ledger and commit-anchoring existed. All future entries
  cite a commit hash.

### VL-002 - G0 (CCS specification/implementation drift)
- Date: 2026-05-14
- Claim: Canonical CCS (whitepaper v0.9.8.4 sections 12-13) is a temporal
  invariant over state transitions; implemented ccs_valid() is a point-in-time
  manifest-integrity check. They are not the same invariant.
- Status: CONFIRMED
- Derived by: Claude, from whitepaper section 12 + IMPLEMENTATION/evaluator.py
- Independently re-derived by: Grok, from the same primary sources (whitepaper
  sections 12-13 + evaluator.py), reaching the same localization including the
  section 8.1 comparison.
- Basis for CONFIRMED: two independent derivations from primary sources, not
  from each other's artifacts.

### VL-003 - G1 (README test count) corrected
- Date: 2026-05-14
- Claim (Rev. 1): Test counts 3/30/34/37 constitute a four-way contradiction.
- Status: CORRECTED
- Correction: Verified against test_pep.py (contains 4 tests) and manifest.json.
  The 30/34/37 figures are plausibly one growing suite at different commits.
  Real issue downgraded to: no commit-pinned source of truth; stale README.
- Derived by: Claude, against test_pep.py + manifest.json + repo README.

### VL-004 - "Validator wrapped in oversized language" read retracted
- Date: 2026-05-14
- Claim (earlier): Elyon-Sol is a ~100-line validator with oversized framing.
- Status: RETRACTED
- Reason: Retracted after reading whitepaper v0.9.8.4. The canon is a
  legitimate formal specification (formal interaction model, set-theoretic
  invariant definitions, prior-work positioning). Accurate finding: faithful
  partial implementation of a real specification, one drifted invariant (G0).
- Derived by: Claude, against whitepaper v0.9.8.4.

### VL-005 - Grok first review (rating) - NOT a confirmation event
- Date: 2026-05-14
- Event: Grok produced a rated review ("8.7/10", "Approved") of the Rev. 2
  package, working from the package artifacts only - not primary sources.
- Status: recorded for history; carries NO verification weight.
- Reason: Per ledger rules, a verdict/rating is not a confirmation event. The
  review did not derive claims from canon or code. Grok's LATER clean-room
  pass against primary sources is the entry that counts - see VL-002.

### VL-006 - canon.md transcribed and locked
- Date: 2026-05-14
- Event: v0.9.8.4 canon transcribed from CANON/canon_v0.9.8.4.pdf to
  CANON/canon.md and locked via CANON/canon.lock.
- Status: CONFIRMED
- Sources: CANON/canon_v0.9.8.4.pdf (immutable source of record).
- Transcription by: Claude. Verified by: Justin Laporte, against the PDF.
- Verified points:
    F4 - Section 3 Notation Clarification: confirmed faithful.
    F5 - Sections 12.1-12.4 and 13 (the G0 sections), checked section by
         section: confirmed faithful. G0 therefore rests on a verified
         transcription.
    F6 - Abstract "ElyonSol" -> "Elyon-Sol": a line-wrap artifact in the PDF,
         normalized in canon.md by decision (kept, not reverted).
- Representation decision (F3): canon.md uses ASCII-safe notation (AC^3, T^26,
  S_{t+1}, <=>, AND, superset-or-equal, etc.) as a representation choice, NOT a
  content change. Per Section 3 the notation is nominal; ASCII forms denote the
  identical constructs. A Transcription Note in canon.md records this and is
  marked non-canonical. Pure-ASCII confirmed by automated byte check.
- Lock: see CANON/canon.lock (sha256 of canon.md at commit time).
- Effect: canon.md is now the working canonical reference, anchored to the PDF.

### VL-007 - v0.9.8.4 known canonical properties (numbering gaps)
- Date: 2026-05-14
- Event: Two structural gaps identified in canon v0.9.8.4 during transcription:
    1. Section 8 has subsections 8.1, 8.2, 8.4 - no 8.3.
    2. Appendix D begins at D.2 - no D.1.
  Both are present in the source PDF; they are not transcription errors.
- Status: CONFIRMED (properties of the locked version, not defects under repair)
- Decision: v0.9.8.4 is locked AS-IS, including these gaps. They are recorded
  known properties of this canonical version. Any correction is a future
  canon-version event - a new version, new hash, new lock, new ledger entry -
  never an in-place edit of v0.9.8.4.
- Decided by: Justin Laporte
- Establishes governance rule GR-1: canon is corrected only by version
  increment, never by in-place edit. (To be recorded in the maintenance
  protocol artifact.)

### VL-008 - Cross-model verification: task-to-source binding is the operative variable
- Date: 2026-05-14
- Event: OpenAI was asked three times to derive specification/implementation
  fidelity from CANON/canon.md + IMPLEMENTATION/evaluator.py.
- Attempts 1 and 2: NOT derivations. Both ranged outside the supplied
  artifacts (referencing project history - "Claude's posture", prior
  iterations, "compression" - none of which is derivable from the two files)
  and characterized the code rather than checking it against the canon.
  Attempt 1 located the CCS mismatch as code-vs-prose rather than code-vs-canon.
  Attempt 2 transcribed canonical CCS(S_t, S_{t+1}, I) and then asserted the
  implementation "collapses cleanly into the canonical function" - actively
  smoothing over the gap.
- Attempt 3: GENUINE INDEPENDENT DERIVATION. Given the same instruction but
  with the model explicitly binding itself to the sources ("treat the canon
  and evaluator as evidence, not terminology to preserve"), it identified that
  CCS "does not fully model state transition consistency" - the G0 gap - and
  independently reached the framing/mechanism gap (G3): "the strongest accurate
  claim is narrower than the whitepaper language".
- Finding: OpenAI's memory context was equally contaminated across all three
  attempts. The variable that produced a real derivation was the model
  honoring the scope of the task, not memory cleanliness. This is corroborated
  by Grok's clean pass (VL-002): Grok also carried prior cross-model context,
  yet derived G0 correctly when given the instruction "derive a conclusion
  from canon.md and evaluator.py". The operative variable is task-to-source
  binding - whether the task is scoped to primary sources AND the model stays
  within that scope - not the cleanliness of the model's memory.
- Status of G0: CONFIRMED by three independent derivations - Claude, Grok
  (clean pass, VL-002), OpenAI (attempt 3). This strengthens VL-002.
- Procedure established for future cross-model verification:
    (a) Scope the task explicitly to the primary sources.
    (b) Confirm the response stayed within that scope - any response
        referencing material not derivable from the supplied artifacts is
        discarded regardless of its conclusion.
    (c) A model's prior exposure to the project does NOT disqualify it as a
        verifier, provided (a) and (b) hold.
- Note: ratings, verdicts, and approval-shaped language in any response
  (present in all three OpenAI attempts to varying degrees) carry no
  verification weight and are not recorded as confirmation - per ledger rules.

### VL-009 - ASCII-safe standard applied repo-wide; prior inconsistency corrected
- Date: 2026-05-15
- Event: The ASCII-safe standard set by VL-006 (canon.md) was applied to all
  files in docs/restructure/. The process discovered two classes of issue:
    (a) The seven Rev. 2 package files (00_README.md through
        06_spec_to_code_traceability.md), generated yesterday before the
        standard was fully internalized, were UTF-8. They would have been
        committed in that form had the precondition grep not been run on
        placement. Caught and corrected before commit.
    (b) canon_transcription_verification_report.md, committed in 3bca97d
        on 2026-05-14, was UTF-8 throughout. This was a pre-existing
        violation of the standard set by VL-006 in 99ac12a. Caught by the
        same grep applied across the directory rather than just the new
        files.
- Status: CORRECTED
- Method: Two throwaway Python scripts (convert_to_ascii.py and
  fix_section_spacing.py) executed the conversion with two-pass safety
  (scan + simulate, then write only if no unexpected non-ASCII remained).
  The substitution map was iterated three times against discovered evidence:
  initial draft, then +section-sign and +en-dash, then +left-right-arrow and
  encoding-safe reporting. The section-sign substitution itself required a
  follow-up fix to insert spacing (section12 -> section 12, sectionAbstract
  -> section Abstract), discovered post-conversion. All scripts deleted
  after use; the conversion is recorded here, not the scripts.
- Identifier rename: test_ccs_section12.py (proposed in artifact 05)
  renamed to test_ccs_canonical.py, removing a filename that would
  perpetually trigger the section-spacing grep. The new name is also more
  descriptive: tests the canonical CCS property, not "the file named after
  section 12."
- Result: confirmed by `file` (all eight files in docs/restructure/ report
  "ASCII text") and POSIX-class grep (LC_ALL=C grep -n
  '[^[:print:][:space:]]' returns nothing).
- Commit: 9c48a1d.
- Process finding: the verification grep in lock_canon.sh's preconditions
  is the same check that caught both (a) and (b). The check works as
  designed. The lesson is broader: any new file added to the repository
  should pass this check before commit, not just files entering CANON/.
  Candidate for inclusion in SESSION_PROTOCOL.md's close protocol.

### VL-010 - VL-003 reproducibility restored: MANIFEST/manifest.json committed
- Date: 2026-05-15
- Event: During honest-base track step 1 (revision of
  docs/restructure/01_repository_structure.md to reconcile against HEAD),
  the reconciliation surfaced that MANIFEST/manifest.json - cited in
  VL-003 as a primary source against which test counts were verified -
  was not present in the committed tree at HEAD = 9f74235. The file
  existed on disk locally but `git ls-files MANIFEST/` returned empty
  and `git status` reported a clean working tree.
- Cause: .gitignore contained a bare `MANIFEST` rule and a `*.manifest`
  rule, both inherited from a Python-project template
  (https://github.com/github/gitignore Python.gitignore). The `MANIFEST`
  rule targets the file Python's setuptools `sdist` auto-generates from
  `MANIFEST.in` during package builds; the `*.manifest` rule targets
  Windows application manifests PyInstaller emits. Neither applies in
  this repository. The bare `MANIFEST` rule matched the domain directory
  MANIFEST/ by name, hiding its entire contents from git.
- Status: CORRECTED
- Method: One-shot fixup script fix_manifest_gitignore.sh (run from
  outside the repository tree, deleted after use per VL-009 precedent
  for one-shot fixups). Script behavior verified against three synthetic
  fixtures before execution against the real repository: clean-tree
  happy path, dirty-tree refusal, replay-safety refusal. Script
  preflight checks: repo-root location, clean working tree,
  MANIFEST/manifest.json exists on disk, both target lines present in
  .gitignore (refuses to operate otherwise). Edit performed with awk
  using full-line equality matching ($0 == "MANIFEST", $0 == "*.manifest")
  to anchor on the exact lines and avoid substring collision with
  comment lines or POE/POE_MANIFEST.md references. Both removed lines
  were replaced with explanatory comment blocks naming the original
  rule, why it does not apply, and the ledger entries that document
  the deviation (VL-003, VL-010). ASCII-safe regime preserved.
- Result: MANIFEST/manifest.json now tracked. .gitignore narrowed.
  VL-003's derivation, previously not reproducible from a fresh clone
  (one of its three cited primary sources was unreachable), is now
  reproducible. VL-003 is unchanged - the ledger is append-only; this
  entry amends the reachability of its sources, not its content.
- Commit: c0867a6.
- Process finding (version-semantics): While reading the manifest
  before commit, the meaning of its `version` field relative to the
  canon version was not documented anywhere reachable from the
  repository. Manifest contains `"version": "1.0"`; canon is
  v0.9.8.4. Resolved by grep against IMPLEMENTATION/evaluator.py
  (lines 31, 37, 67-73): the field is compared by string equality
  against ctx["expected_manifest_version"], a caller-asserted value.
  The two version numbers are independently scoped - manifest version
  is a caller-pinning tag, not a reference to the canon. This is the
  same caller-assertion pattern G6 names for the ccs_valid input
  field, in a different code path. Candidate actions: (a) expand G6's
  scope to cover the version path as well, or (b) record a sibling
  gap; and add a `version` entry to the vocabulary ledger
  (docs/restructure/03_vocabulary_ledger.md) when that artifact is
  promoted. The manifest value `"1.0"` is correct given the gate's
  semantics; no edit to manifest.json is warranted.
- Process finding (line endings): The fixup script wrote the edited
  .gitignore through Git Bash stdout redirection, producing LF line
  endings while the working-tree file had CRLF (Windows checkout).
  The raw `diff -u` shown by the script reported every line as
  changed; git's index view (via `git diff --cached --ignore-cr-at-eol`
  and via .gitattributes normalization `* text=auto eol=lf`) showed
  the substantive 4-line change correctly. Lesson: scripts that show
  their own diffs should prefer `git diff` over `diff -u` on Windows
  checkouts, so the displayed diff matches what will enter the commit.
- Process finding (script placement): The fixup script could not be
  placed in scripts/ before running, because doing so dirtied the
  working tree and the script's own preflight refused to operate. The
  script was instead run from outside the repository tree and deleted
  after use. This is consistent with VL-009's distinction: scripts
  that are part of the durable method (establish_ledger.sh,
  lock_canon.sh, append_vl00X.sh) are committed; one-shot fixups are
  recorded in prose and discarded.

### VL-011 - EVIDENCE/ reorganized into proofs/ and archive/; honest-base track complete
- Date: 2026-05-15
- Event: The six proof-style files in EVIDENCE/ and the raw pytest log
  under EVIDENCE/tmp/ were reorganized into EVIDENCE/proofs/ (current)
  and EVIDENCE/archive/ (non-current, with prepended ARCHIVED header)
  per STATE.md's "Next open action" and gaps G2/G5/G9 in
  docs/restructure/04_current_vs_claimed.md. EVIDENCE/tmp/ removed.
  EVIDENCE/verification_ledger.md unchanged at EVIDENCE/ root.
- Status: CORRECTED. Closes the EVIDENCE/ reorganization item on the
  honest-base track; the honest-base track is complete. G9's
  "finish or delete" choice is resolved as "archive with citation" -
  completing the proof would produce a proof of a dead API against
  a dead endpoint.
- Per-file disposition (derived from each file's content against
  IMPLEMENTATION/pep.py, IMPLEMENTATION/evaluator.py, and the pytest
  output captured in ac3_mutation_failure.txt - not from the gap
  document's prescription alone):
    EVIDENCE/proofs/concurrent_replay_equivalence_001.md
      - Claim verifiable against current code under un-mutated AC^3.
    EVIDENCE/proofs/manifest_integrity_continuity_001.md
      - Describes the implemented ccs_valid() check at HEAD; current.
        The file's use of "CCS continuity" in its title is the G0
        naming problem and will be addressed in the G0/G6/G10
        disambiguation pass, not here.
    EVIDENCE/proofs/mutation_sensitivity_001.md
      - Record of a successful mutation experiment; the "2 failed"
        line is the expected and desired outcome of an intentional
        code mutation that was subsequently reverted. Current.
    EVIDENCE/proofs/ac3_mutation_failure.txt
      - Raw pytest output backing mutation_sensitivity_001.md.
        Relocated from EVIDENCE/tmp/. Co-located with the proof it
        substantiates. Resolves G8 for this proof - named backing
        evidence now exists.
    EVIDENCE/archive/interception_proof_001.md
      - Documents the flat-key API rejected by pep.py at HEAD (G2);
        relies on a now-dead webhook.site URL (G5).
    EVIDENCE/archive/interception_proof_002.md
      - Same: G2, G5.
    EVIDENCE/archive/stability_proof_001.md
      - Truncated mid-JSON (G9); uses flat-key payload (G2); relies
        on dead webhook.site URL (G5).
- Archive header: each archived file received a 13-line prepended
  block marking it NON-CURRENT, citing the gap reasons, dating the
  archival (2026-05-15), naming this ledger entry, and pointing to
  docs/restructure/04_current_vs_claimed.md for full gap citations.
  Header bytes pure-ASCII; pre-existing non-ASCII bytes in the three
  files' original content are noted below as an open process item.
- Method: One-shot fixup script reorganize_evidence.sh, run from
  outside the repository tree, deleted after use per VL-010 precedent
  for one-shot fixups. Five preflight gates: clean working tree, on
  main, all eight expected EVIDENCE/ files tracked, target directories
  do not exist yet (replay safety), EVIDENCE/tmp/ contains exactly the
  one expected file (tracked and on disk). The script was vetted
  against four synthetic fixtures before execution: happy path
  (passed), dirty tree (refused), replay attempt with proofs/ already
  present (refused), missing expected file (refused), untracked file
  in EVIDENCE/tmp/ (refused at the clean-tree gate - defense in
  depth, since the tmp-disk-check is downstream of the clean-tree
  check).
- Commit: e6345a5.
- Process finding (staging vs. direct-write in mixed-mode scripts):
  reorganize_evidence.sh ran `git mv` (which auto-stages renames) for
  seven files and direct file writes (header prepends) for three
  archive files. The direct writes were not auto-staged. The first
  commit attempt staged only the renames and produced a diff stat of
  "0 insertions, 0 deletions" - the signal that the headers were
  absent from the commit. The commit landed as a pure-rename commit;
  correction was straightforward because the commit was local-only
  and unpushed: `git add` of the three archive files followed by
  `git commit --amend --no-edit` produced the correct combined
  commit. Lesson: scripts that produce a mix of git-mv changes and
  direct-write changes should either (a) explicitly `git add` the
  direct-write changes themselves before exiting, or (b) print an
  explicit reminder to `git add -A` before commit. Same family as
  VL-010's "trust git diff over diff -u on Windows checkouts" -
  the diff-stat-as-signal point. Always check what git is actually
  about to commit, not what the script appeared to do.
- Process finding (pre-existing ASCII violations in archived files):
  The reorganize_evidence.sh postcheck grep
  (LC_ALL=C grep '[^[:print:][:space:]]') surfaced non-ASCII bytes
  in the original content of all three archived files:
  AC^3 superscript glyphs in interception_proof_001.md (lines 51,
  52, 81); T^26 superscript and arrow glyphs in
  interception_proof_002.md (line 38); em-dash, arrow, and emoji
  glyphs in stability_proof_001.md (lines 17, 20, 27, 28, 43).
  These bytes were present at HEAD before this commit; they are
  pre-existing violations of the VL-009 repo-wide ASCII-safe
  standard, not damage caused by VL-011's reorganization. The bytes
  were not normalized in this commit because reorganization and
  content-normalization are distinct concerns and conflating them
  muddies the diff. The violations remain open as a known item.
  Three options for resolution: (a) apply the VL-009 substitution
  map to the three archived files; (b) leave them verbatim as
  historical artifacts and document an exception to VL-009 for
  EVIDENCE/archive/; (c) repo-wide ASCII pass extended to all of
  EVIDENCE/. Recorded here, not resolved. Resolution is a decision,
  not a blocking task on the G0 build track.
- Process finding (untracked working-tree file caught at preflight):
  scripts/session_start.sh was an untracked working-tree file
  present from session start. It blocked reorganize_evidence.sh's
  clean-tree gate. On inspection it was a personal resume
  convenience script (git pull + git log + git status), not part
  of the durable session protocol referenced in
  docs/SESSION_PROTOCOL.md, and the author deleted it rather than
  committing or gitignoring it. Same family as VL-010's
  MANIFEST/manifest.json: a file present in the working tree that
  the repository's stated state did not account for. The preflight
  caught it before any damage. Same lesson as VL-009 about applying
  the canon.lock precondition grep broadly - the clean-tree check
  is the same shape, applied to every fixup script's preflight.
- Process finding (per-file disposition required full reads, not
  headers): An initial disposition table was drafted from file
  headers alone. Two files were misclassified to archive on header
  evidence; the misclassification inverted on full read.
  mutation_sensitivity_001.md's "2 failed, 35 passed" line in its
  Observed Failure Surface section reads as a current defect from
  the header; the file's Integrity Restoration section makes clear
  the failure was the expected outcome of an intentional mutation
  that was subsequently reverted. concurrent_replay_equivalence_001.md
  was almost misclassified as contradicted by the
  ac3_mutation_failure.txt log; the log is actually that proof's
  raw backing evidence under the same mutation, not evidence of a
  current defect. Both corrections came from reading file bodies,
  not headers. Lesson: disposition decisions about evidence files
  require the full file. Headers can invert under full reads when
  the file's narrative is structured as setup-observation-restoration.

### VL-012 - G0 rename + G6 + G10 disambiguation pass; convention decided and applied
- Date: 2026-05-15
- Event: The G0/G6/G10 disambiguation pass (STATE.md "Next open action",
  priority item 3 in docs/restructure/04_current_vs_claimed.md) was
  performed. The pass renames the implemented point-in-time check away
  from the drifted name "CCS"; removes one redundant caller-asserted
  input field; documents the caller-assertion semantics of the
  remaining load-bearing pinning fields; renames four test IDs to
  honor the same reservation. Decisions were made before any file
  was touched.
- Status: CORRECTED.
- Convention decided: caller-asserted fields are REMOVED if redundant
  with system-verified checks; KEPT and DOCUMENTED if load-bearing.
  This is asymmetric-by-function by design: G6's field is redundant
  with the SHA256 + version match; G10's fields are load-bearing
  (the pinning mechanism itself). Treating them under one symmetric
  rule would paper over a real distinction.
- Considered and rejected: (b) keep both fields, prefix both with
  caller_asserts_*. Rejected because renaming a useless input field
  does not give it meaning; it only adds verbosity.
- Reservation of "CCS" name: extended in this pass to test IDs in
  addition to code identifiers. Artifact 04's G0 action 2 reads
  "unused in code"; this pass interprets that to include test IDs
  on the rationale that a green pytest line citing ccs_version_*
  perpetuates the same misclassification artifact 04 names.
- Changes (commit 8ba88cf):
    (1) IMPLEMENTATION/evaluator.py: function ccs_valid() renamed to
        manifest_integrity_valid(); docstring added documenting the
        caller-assertion semantics of expected_manifest_version and
        expected_manifest_sha256, and explicitly distinguishing the
        function from canonical CCS (whitepaper section 12). The
        ctx.get("ccs_valid") guard at the top of the function was
        removed (G6 - redundant with the SHA256 + version match
        below it). Call site at line 97 updated.
    (2) IMPLEMENTATION/pep.py: no change. pep.py imports evaluate
        and load_manifest, not ccs_valid; the rename is transparent
        across the module boundary.
    (3) IMPLEMENTATION/replay/receipt.py: no change. Standalone
        receipt module; no ccs_valid references.
    (4) TESTS/test_pep.py: the inert "ccs_valid" key removed from
        all four test context fixtures. test_governed_call_refuse_
        blocks_upstream still refuses (over-determined: AC^3 refuses
        on empty AP before manifest integrity is reached); the other
        three tests pass unchanged.
    (5) TESTS/test_adversarial_evaluator.py: 26 cases -> 23 cases.
        Four ccs_flag_* cases deleted; one new manifest_sha256_missing
        case added to preserve coverage of the SHA-missing REFUSE
        path (would have been lost under naive deletion). Four
        ccs_version_* cases renamed to manifest_version_*. Inert
        "ccs_valid" keys removed from the 16 remaining ap_*/op_*
        cases. The intentional Cyrillic byte in ap_lookalike_unicode
        (rol-U+0435 at the second list element) expressed as a
        \u-escape (rol\u0435) to preserve uniform ASCII postcheck
        across all files; runtime-equivalent. This is the VL-006
        representation-decision precedent ("ASCII forms denote the
        identical constructs") applied to a test fixture.
    (6) TESTS/test_concurrency.py: inert "ccs_valid": True line
        removed from three context constants (AUTHORIZED_CTX,
        UNAUTHORIZED_CTX, BAD_SHA_CTX). No behavior change.
    (7) TESTS/test_replay_receipts.py: no change. Standalone
        receipt-determinism tests.
    (8) EVIDENCE/proofs/manifest_integrity_continuity_001.md renamed
        via git mv to EVIDENCE/proofs/manifest_integrity_001.md and
        body rewritten to remove the "CCS continuity" framing per
        VL-011's deferred item. The historical commit citation
        (8fddb4e) preserved with explanatory note. Em-dash in the
        original commit line incidentally normalized to ASCII
        hyphen by the rewrite. Stale "30/30 tests passing" count
        left as-is and explicitly flagged as G1-scope, not this
        pass's concern.
    (9) docs/restructure/04_current_vs_claimed.md: G6 and G10
        removed from open list; new "Resolved gaps" section populated
        with the consolidated entry; G0 reworded as PARTIALLY
        RESOLVED (rename half closed, build half open); priority
        order item 3 marked RESOLVED. New gap G11 added (manifest-
        source asymmetry, surfaced by this pass).
    (10) EVIDENCE/verification_ledger.md: this entry appended.
- VL-011 path reference (VL-011 names the proof file as
  EVIDENCE/proofs/manifest_integrity_continuity_001.md): this is
  the previous filename. VL-011 is unchanged - the ledger is
  append-only; this entry records the rename to the new path
  EVIDENCE/proofs/manifest_integrity_001.md.
- Process finding (full-test-tree-read): Initial Phase 2 plan
  was drafted against test_pep.py alone, on the strength of
  artifact 04's citation of it for G1. Preflight pytest -v
  surfaced 37 tests across four test files. The plan rewound
  once. Subsequent reads of test_adversarial_evaluator.py and
  test_concurrency.py surfaced (a) the ccs_flag_* coverage-loss
  issue (resolved by adding manifest_sha256_missing) and (b)
  the manifest-source asymmetry (recorded as G11). Lesson:
  before drafting a multi-file pass, list every file the pass
  plausibly touches and read all of them. The list here should
  have started with `find IMPLEMENTATION TESTS EVIDENCE -type f`
  before drafting Phase 2. Same family as VL-011's per-file
  disposition lesson.
- Process finding (ccs_flag_* discriminator-shift): Tests
  named for one discriminator can pass post-edit via a different
  discriminator, masking what they no longer test. Discovered
  by trace, not by pytest output - pytest would have shown the
  cases still passing post-G6 and that would have been the
  wrong signal. Lesson: test name changes are real reviewable
  events, not cosmetic; tests should name what they actually
  test under current code, not what they tested historically.
- Process finding (IMPLEMENTATION/replay/ subpackage not in
  planning artifact set): The replay/receipt module was not
  named in artifact 04 and was surfaced only by pytest -v's
  test discovery. Subsystem is internally consistent and was
  not touched by this pass, but its absence from the planning
  artifacts represents the same blind spot the test-file count
  did. Fix is the same: enumerate the real file set, not work
  from artifact summaries.
- Process finding (expected_manifest_sha256 caller-assertion):
  Full read of evaluator.py surfaced that the SHA256 pinning
  field is the same caller-assertion pattern as the version
  field (G10) in the same function. Artifact 04 named only the
  version field. The pattern applies identically; the convention
  decided for G10 extends to it. The function docstring
  documents both. Recorded as an extension of G10's scope under
  the same convention, not a new gap, because the resolution is
  identical.
- Process finding (artifact-vs-code line-number discrepancy):
  Artifact 04 cited lines 67-73 for the version-check code path.
  Full read showed the comparison spans lines 63-73 (function
  spans lines 62-84). Minor; not material. Recorded as a
  VL-011-family lesson: prefer reading the file when acting on
  it, even when an artifact summarizes it accurately.
- Process finding (manifest-source asymmetry, G11): During
  read of test_concurrency.py the inline TEST_MANIFEST and
  MUTABLE_MANIFEST were observed to have different AR/R schemas
  from MANIFEST/manifest.json on disk. evaluator.manifest_sha256()
  ignores its manifest argument and always reads disk. The
  concurrent tests pass because their expected_manifest_sha256
  values happen to be the disk file's hash. Recorded as gap G11
  in artifact 04. Not in this pass's scope.
- Process finding (receipt.py canonical_json ensure_ascii=False):
  IMPLEMENTATION/replay/receipt.py's canonical_json uses
  ensure_ascii=False, allowing raw UTF-8 bytes in serialized
  receipts. Current tests produce ASCII receipts only, so this
  is not a current problem. Latent inconsistency with VL-009
  ASCII-safe regime; warrants documentation rather than fix.
  Not in this pass's scope.
- Process finding (em-dash incidentally normalized): The em-dash
  (U+2014) in the original manifest_integrity_continuity_001.md
  line 7 was incidentally normalized to an ASCII hyphen by the
  rewrite. Not a deliberate VL-009 enforcement step; consequence
  of rewriting the line. Recorded for attribution. Same family
  as VL-011's pre-existing non-ASCII findings in
  EVIDENCE/archive/; those remain awaiting the VL-011 deferred
  decision.
- Process finding (Cyrillic byte preserved as \u-escape, not
  allow-listed): The intentional Cyrillic 'e' (U+0435) in
  test_adversarial_evaluator.py's ap_lookalike_unicode case was
  expressed as a Python string-literal \u-escape (rol\u0435)
  rather than allow-listed in the ASCII postcheck. Runtime
  semantics preserved exactly; postcheck remains uniform across
  all files. VL-006 representation-decision precedent applied
  to a test fixture: ASCII forms denote the identical constructs.
- Process finding (CRLF working-tree drift surfaced by exact-byte
  matching): The pass script aborted at Edit 1 because
  IMPLEMENTATION/evaluator.py was CRLF in the working tree while
  the script's match patterns were LF-encoded. Investigation
  revealed .gitattributes declared eol=lf for *.py, *.md, etc.,
  but 10 working-tree files were CRLF; the index for all 10 was
  already LF. Cause: .gitattributes was added to the repo after
  these files were last checked out; git does not retroactively
  renormalize the working tree on .gitattributes change. The
  inconsistency was working-tree-only, not stored. Fixed by
  rm + checkout HEAD -- <files> for the 10 affected files, as
  a one-shot prerequisite immediately before the pass. The fix
  produced no commit (the index was already correct); it is
  recorded here as a prerequisite operation, not a separate
  ledger entry. Same family as VL-010's MANIFEST/manifest.json
  hidden-state finding: a state on the author's machine that
  the repository's stored state did not reflect.
- Process finding (git add --renormalize is the wrong operation
  for working-tree-only EOL drift): `git add --renormalize .`
  updates the index, not the working tree. When the index is
  already LF (as it was here) --renormalize is a no-op. The
  operation that actually refreshes the working tree to honor
  .gitattributes is `rm <files>` followed by
  `git checkout HEAD -- <files>`, which applies .gitattributes
  rules at checkout time. Confirmed against a happy-path
  fixture during script vetting; --renormalize left the
  working tree CRLF, rm+checkout fixed it. Documented here so
  the next pass encountering working-tree EOL drift does not
  waste cycles on --renormalize first.
- Process finding ("outside the repo tree" specification):
  Phase 2 instructions said "run the script from outside the
  repo tree" and showed `cp disambiguation_pass.sh ~/...`.
  The user's home directory contains the repo as a
  subdirectory, so copying to `~/` placed the script inside
  the repo tree and Gate 4 refused on the untracked file.
  "Outside the repo tree" must be specified as "not in any
  subdirectory of the repo tree" - home directories are
  commonly parents of repo directories. Caught by Gate 4
  without harm; documenting for future fixup-script
  instructions. Same family as VL-010's script-placement
  finding and VL-011's session_start.sh finding: one-shot
  scripts must live outside the tree they operate on.
- Process finding (self-referencing commit hash):
  VL-012's entry was drafted with a `<hash>` placeholder for the
  commit hash. The workflow was: commit, capture the new hash,
  substitute into the ledger, amend. This is the same pattern
  prior entries (VL-010, VL-011) used and that has worked. What
  it missed: `git commit --amend` produces a new hash because the
  tree content changes during the amend (the placeholder gets
  replaced). The pre-amend hash captured is therefore the wrong
  hash. A second amend changes the hash again because of timestamp
  metadata. There is no fixed point for a commit that contains
  its own hash. The correct workflow for self-referencing hash is
  one of: (a) capture the post-amend hash and accept the drift
  (the ledger lags by one amend); (b) commit once with `<hash>`,
  then make a separate corrective commit citing the previous
  commit's actual hash (this entry's approach); or (c) drop the
  self-reference and cite the commit indirectly via date and
  description only. Prior entries (VL-010, VL-011) likely
  accepted small drift, since their cited hashes match the
  reachable commits but the underlying chicken-and-egg cannot be
  fully resolved. This finding documents the impossibility and
  proposes (b) as the cleanest convention.
- Commit: 8ba88cf.
### VL-013 - Planning artifacts 05 and 06 brought current to VL-012
- Date: 2026-05-16
- Event: Planning artifacts `docs/restructure/05_admissibility_envelope_spec.md`
  and `docs/restructure/06_spec_to_code_traceability.md` contained
  forward-tense references to `ccs_valid()` and a DRIFTED status for
  canonical CCS - statements that were correct when the artifacts were
  drafted (2026-05-14) but became false at VL-012 (2026-05-15, commit
  8ba88cf), when `ccs_valid()` was renamed to `manifest_integrity_valid()`
  and canonical CCS was reclassified from DRIFTED (wrong code in the slot)
  to UNIMPLEMENTED (no code in the slot). This freshness pass corrects
  the stale statements. No code change; no canon change; no test change.
- Status: CORRECTED
- Scope rule applied: edits restricted to statements about current state
  that became false after VL-012. Substantive content of the artifacts
  preserved. Specifically NOT touched:
    - the "What changed from Rev. 1, and why" section of artifact 05,
      including its `ccs_valid()` references on lines 6 and 14, because
      the section is an explicit historical-narrative frame about Rev. 1
      vs. Rev. 2 and the section header carries the temporal framing;
    - artifact 05's "Open questions for review," which remain legitimately open;
    - artifact 05's G7 reference and reassertion protocol;
    - all FULL rows in artifact 06's table;
    - artifact 06's "How this map is maintained" section.
- Edits to 05 (3):
    (1) Envelope-structure JSON block, `manifest_integrity` comment:
        forward-tense "the renamed point-in-time check (was 'ccs_valid')"
        replaced with past-tense citing VL-012 and the current function
        name `manifest_integrity_valid`.
    (2) Field rationale bullet for `condition_results`: forward-tense
        "the renamed point-in-time check (formerly mis-named ccs_valid -
        gap G6/G0)" replaced with past-tense citing VL-012, explicit
        function name and source file, and an explicit note that
        implementing canonical `ccs` is the G0 build track (open).
    (3) Build-order step 2: appended "Done in VL-012 (commit 8ba88cf)"
        to the rename-and-reserve step.
- Edits to 06 (5):
    (1) Section 2 Evaluation pipeline row Notes cell: replaced
        "CCS stage is DRIFTED (see section 12)" with explicit current
        state - third stage in code is `manifest_integrity_valid()`
        (section 8.1 work), canonical CCS is UNIMPLEMENTED (G0 build half).
    (2) Section 3 CCS row: replaced in place. Code-construct cell
        changed from `ccs_valid()` to ` - ` (no implementing code);
        status changed from DRIFTED to UNIMPLEMENTED; Notes cell
        rewritten to name this as the G0 build half, cite VL-012's
        closing of the rename half, and reference Deliverable 05.
    (3) Section 6 Lightweight formal model row Notes cell: updated
        to reflect the post-VL-012 rename and to record the residual
        canon-vs-code naming tension (canon section 6 pseudocode
        names `ccs_valid(ctx)`; `evaluate()` calls
        `manifest_integrity_valid()`). The tension is real and now
        explicitly named; it will resolve either by canon-version
        event or by an implementation note. Not this pass's call.
    (4) Section 8.1 row: code-construct cell extended to include
        `manifest_integrity_valid()`. Notes cell updated to past
        tense ("formerly-named `ccs_valid()` was doing") and to
        cite VL-012 as making the section 8.1 attribution explicit
        in code.
    (5) Section 13 row Notes cell: replaced "the CCS operand is
        DRIFTED" with "the CCS operand is UNIMPLEMENTED (G0 build
        half)" - same staleness pattern as edits (1), (3), and the
        section 3 CCS row, surfaced during the post-edit residual
        scan rather than during planning, and folded into this pass
        because the root cause is identical.
- Edits to 06 summary block:
    DRIFTED count: 1 -> 0, with an explanatory line replacing the
    prior "section 3 CCS. The single anchor gap (G0)" entry.
    UNIMPLEMENTED count: 6 -> 7, with section 3 CCS added as the
    first item (G0 build half).
    "Read of the whole picture" paragraph rewritten: the bottom-line
    framing ("a faithful partial implementation of a real specification,
    with one well-defined missing invariant") preserved verbatim. The
    intermediate sentences updated to name CCS as UNIMPLEMENTED rather
    than as "the drift," and to record the VL-012 framing shift:
    post-VL-012, the gap is honestly named as a missing invariant
    rather than a misnamed one.
- Method: direct in-place edits via str_replace anchored on exact-byte
  unique strings. No script. Both files re-verified ASCII-clean against
  the VL-009 standard after edits. Both files re-scanned for residual
  stale references (e.g., live-tense `ccs_valid()` or in-row DRIFTED
  status notes) before commit; the residual scan surfaced edit (5) to 06
  during execution and it was added to the pass under the same scope rule.
- Process finding (residual scan caught one omission): The pre-edit
  plan enumerated four edits to 06. The post-edit residual scan
  (`grep -n "DRIFTED" 06_spec_to_code_traceability.md`) surfaced a
  fifth occurrence on line 44 (section 13 row Notes cell) that the
  plan had missed. The grep is the same shape as VL-009's lock_canon.sh
  preconditions and VL-011's per-file disposition lesson: don't trust
  the plan, scan the actual file. Adding the scan as a post-edit step
  for any future freshness pass is the durable lesson.
- Process finding (judgment call on historical-narrative sections):
  Artifact 05 lines 6 and 14 contain forward-tense `ccs_valid()`
  references inside the "What changed from Rev. 1, and why" section.
  These are inside an explicit historical-narrative frame and were
  preserved as-is by author decision. The freshness-pass scope rule
  ("does this edit correct a statement that became false after
  VL-012?") was applied with the section header as context: a
  historical-narrative section's claims are scoped to the moment the
  narrative is about, not to the present. Recorded as a precedent for
  future freshness passes: section-level temporal framing dominates
  individual-line tense.
- Process finding (no self-referencing hash): Per VL-012's
  self-referencing-hash finding, this entry deliberately avoids citing
  its own commit hash. It cites VL-012's hash (8ba88cf) as the
  triggering event, the dates of both artifacts' last substantive
  edit, and the file paths. The commit hash for VL-013 itself is
  reachable via `git log` and is implicit in the entry's position
  in the ledger. This is convention (c) from VL-012's process
  finding: drop the self-reference entirely.
- Files changed:
    docs/restructure/05_admissibility_envelope_spec.md
    docs/restructure/06_spec_to_code_traceability.md
    EVIDENCE/verification_ledger.md (this entry)
- No code, canon, manifest, or test change.

### VL-014 - SPEC/request_schema.md drafted; G0 build track started
- Date: 2026-05-17
- Event: SPEC/request_schema.md authored as the first artifact of
  the G0 build track (STATE.md "Next open action" after VL-013).
  Derivation from locked canon v0.9.8.4 sections 11.1, 11.3-11.8,
  11.9, 12.1, with cross-references to sections 12 and 13.
  Build-order step 1 of
  docs/restructure/05_admissibility_envelope_spec.md.
- Status: SINGLE-SOURCE
- Derived by: Claude, from CANON/canon.md (section 11 in particular),
  docs/restructure/05_admissibility_envelope_spec.md, and
  IMPLEMENTATION/pep.py (current request-handling surface).
- Basis for SINGLE-SOURCE: one derivation pass; awaiting independent
  re-derivation from primary sources (canon + envelope spec) for
  CONFIRMED. Candidate re-deriver: Grok or OpenAI under the
  task-scoping procedure established in VL-008 ("derive the
  canonical request shape from CANON/canon.md sections 11, 12, 13;
  the only other source is
  docs/restructure/05_admissibility_envelope_spec.md for the
  embedding context"). If the re-derivation produces the same field
  set with the same canon-clause attributions, the entry becomes
  CONFIRMED.
- Scope of the artifact:
    - Maps canonical interaction tuple I = (A, S, C, t) and the
      caller-supplied sets AP(I), OP(I) to on-the-wire fields.
    - Names AR(I) and R(I) as manifest-derived, NOT caller-supplied
      (section 11.9 + section 11.3/11.4).
    - Documents expected_manifest_version and
      expected_manifest_sha256 as load-bearing caller-asserted
      fields per VL-012's convention (closes the documentation
      requirement of G10 at the schema layer; the function-level
      documentation in manifest_integrity_valid()'s docstring is
      already in place from VL-012).
    - Reserves the name "CCS" per VL-012; defines a refusal rule
      for caller attempts to assert it (REF_SCHEMA_RESERVED_CCS).
    - Names the flat-key payload from EVIDENCE/archive/interception_*
      as REFUSED (REF_SCHEMA_FLAT_KEYS). This is the schema-layer
      half of G2.
- What this artifact closes:
    - Nothing fully, because no gap is closed by a spec alone.
    - PARTIALLY ADVANCES G2: the schema names the rejected shape
      and the accepting shape; G2 fully closes only when the code
      enforces this at the PEP boundary (build-order step 4,
      proposed VL-017).
    - PARTIALLY ADVANCES G0 BUILD TRACK: schema is step 1 of the
      envelope spec's build order. G0's build half closes when the
      envelope's reassertion protocol is implemented (build-order
      step 3 of artifact 05, separate work from this schema).
    - PARTIALLY ADVANCES G10: at the schema layer, caller-assertion
      semantics are now documented at the field. G10 was already
      considered resolved at the function-docstring layer in
      VL-012; this entry adds the schema-layer documentation as a
      defensive duplicate.
- What this artifact does NOT close:
    - G0 build half (canonical CCS implementation; envelope still
      unimplemented).
    - G7 (canon-derived tests for invariants, distinct from the
      schema-shape tests proposed in step 2 of the schema's build
      order).
    - G11 (manifest_sha256() reads from disk via hardcoded path;
      noted under expected_manifest_sha256 with a forward reference
      but not resolved).
    - G4 (non-bypassability; out of scope for this artifact).
    - G1, G3, G5, G8, G9 (no overlap with the schema).
- Decision recorded - open question 5 accepted as proposed:
  Artifact 05 will absorb `context` (canon's C, section 11.1) into
  its `request_context` envelope block and grow `target_url` at
  envelope top level. Scheduled as build-order step 6 of the schema
  work, proposed VL-018. Recorded here so the decision is on the
  ledger, not buried in chat history.
- Open questions remaining (recorded in the artifact's "Open
  questions for review" section):
    (1) strictness on unknown keys inside interaction.context;
    (2) versioning of the schema itself;
    (3) where AP/OP get sorted (PEP vs caller);
    (4) target_url manifest-derived allowlist (G4 deferral).
  These are recorded as part of the SINGLE-SOURCE entry; they
  become decided one way or the other before the entry transitions
  to CONFIRMED, OR they are explicitly carried forward into the
  CONFIRMED entry as still-open and tracked in
  docs/restructure/04_current_vs_claimed.md.
- Process finding (canon-vs-code naming tension surfaced rather
  than smoothed): canon section 11.1 names context `C` as one
  component of I; IMPLEMENTATION/pep.py's request model has a flat
  outer `context: Dict[str, Any]` that bags everything together.
  The schema renames the outer field to `interaction`
  (canon-faithful) and reserves `context` for canonical `C` inside
  it. The rename is in the spec; the code change is deferred to
  build-order step 4 (proposed VL-017). Same pattern as VL-012's
  ccs_valid -> manifest_integrity_valid rename: lock the name in
  the spec layer first, ledger the convention, then move code.
  This pattern is now recurring enough that it could be a candidate
  governance rule (GR-2: spec-defines-the-rename; code change is a
  separate commit citing the spec entry). Not proposing GR-2 here;
  flagging that a second instance has emerged.
- Process finding (schema commit landed ahead of this ledger
  entry): SPEC/request_schema.md was committed in d7eddd5 ahead
  of this ledger entry. The intended single-commit shape
  (schema + ledger + STATE.md) was broken by a chat-pasted
  multi-line `git commit -m "..."` block whose embedded newlines
  and quotes collided with shell parsing; the schema commit
  succeeded but the ledger append and STATE.md edits were not
  staged and were not detected before `git push`. This entry and
  the accompanying STATE.md edits are therefore a follow-up
  commit citing d7eddd5, same pattern as VL-012 -> f0df14c
  (which corrected a different self-referencing-hash issue, not
  the same failure mode). The schema file content in d7eddd5
  matches what was reviewed in this session; no rework needed.
- Process finding (pasted-block collision; durable lesson): the
  multi-line `git commit -m "..."` form pasted from chat into
  Git Bash failed silently twice in the same session - the
  second time landing the file commit but losing the ledger and
  STATE.md edits. Failure mode: embedded newlines in a quoted
  string trigger shell continuation; embedded double-quotes
  terminate the string prematurely; either way, `git push`
  runs with whatever arguments fall out the other side and may
  push an incomplete commit. The first occurrence was caught
  before any commit landed (the prior turn's
  `git pushchange; canon/...` scramble); the second was not.
  Durable lesson: open the editor for any multi-paragraph
  commit message (`git commit` with no `-m`); stage files one
  at a time and re-verify `git status` after each `git add`;
  treat `1 file changed` after a multi-file intent as a signal
  to stop, not as a clean commit. Same family as VL-010's
  "trust git diff over diff -u on Windows checkouts" and
  VL-011's "trust what git is about to commit, not what the
  script appeared to do."
- Process finding (ledger paste lost markdown structure): the
  first attempt to append this entry pasted the entire
  scratchpad `session_close_package.md` rather than just the
  VL-014 entry, AND lost the ledger's markdown conventions
  (`###` headers, `-` bullet markers, indented sub-bullets).
  The combination was caught at `git diff` review before
  staging and backed out via
  `git checkout EVIDENCE/verification_ledger.md`. Cause not
  fully diagnosed; likely a paste-buffer interaction between
  the chat source and `vi` on Git Bash. Durable lesson: for
  ledger appends, prepare the entry as a standalone file with
  the exact byte layout intended, then append via
  `cat entry.md >> EVIDENCE/verification_ledger.md` rather
  than pasting into an editor. This entry is the first to use
  that approach; if it lands cleanly, the convention is on
  the record.
- Files added:
    SPEC/request_schema.md (in d7eddd5)
- Files modified in the corrective commit:
    EVIDENCE/verification_ledger.md (this entry)
    STATE.md
- Files unchanged (despite topical relevance):
    CANON/canon.md - locked, untouched.
    MANIFEST/manifest.json - untouched.
    IMPLEMENTATION/pep.py - the rename to `interaction` is
        build-order step 4 (proposed VL-017), not this commit.
    IMPLEMENTATION/evaluator.py - untouched.
    docs/restructure/05_admissibility_envelope_spec.md - the
        feed-back is build-order step 6 (proposed VL-018), not
        this commit.
- Schema commit: d7eddd5 (file landed). Corrective commit (this
  entry + STATE.md): per VL-012's self-referencing-hash
  finding, deliberately not cited here; reachable via `git log`.

### VL-015 - Cross-model verification of VL-014: VL-014 -> DISPUTED; G12 + G13 surfaced
- Date: 2026-05-17
- Event: VL-014 (SPEC/request_schema.md, SINGLE-SOURCE) was
  submitted for independent re-derivation by Grok and OpenAI
  under the procedure established in VL-008. The verification
  request was prepared as a standalone artifact
  (`verification_request_vl014.md`, not yet committed to the
  repo; see process finding below) bundling: (a) the task
  scoping, (b) attached primary sources (CANON/canon.md and
  docs/restructure/05_admissibility_envelope_spec.md), and (c)
  explicit instructions that SPEC/request_schema.md itself was
  NOT to be shown to either verifier (per VL-005's precedent
  that reading the artifact being verified is code review, not
  derivation). Both verifiers returned procedurally-clean
  derivations under VL-008 rules (a), (b), (c). The three
  derivations (Claude's schema, Grok's, OpenAI's) agreed on a
  core field set (AP, OP, expected_manifest_version,
  expected_manifest_sha256) and diverged on three specific
  loci, surfacing two new gaps.
- Status of VL-014: SINGLE-SOURCE -> DISPUTED
- Procedure adherence (VL-008):
    - Grok:
        - Rule (a) scope-bound: response cites only canon.md
          sections; envelope spec explicitly noted as not
          load-bearing for the derivation. Passed.
        - Rule (b) scope-checkable: Scope check section
          present; every field's citation enumerated; envelope
          spec non-use explicitly justified. Passed.
        - Rule (c) prior exposure permitted: Grok has prior
          project exposure (VL-002, VL-005). Permitted under
          rule (c) since (a) and (b) hold.
        - Verdict: response carries verification weight.
    - OpenAI:
        - Rule (a) scope-bound: response cites canon.md
          sections and envelope spec sections; no external
          material. Passed.
        - Rule (b) scope-checkable: Scope check section
          present; comprehensive item-by-item citations to
          canon and envelope spec; closing line affirms
          "No additional concepts or claims were retained that
          could not be cited to the two attached files."
          Passed.
        - Rule (c) prior exposure permitted: OpenAI has prior
          project exposure (VL-008). Permitted under rule (c)
          since (a) and (b) hold.
        - Verdict: response carries verification weight.
        - Note: OpenAI rendered AC^3/T^26 evaluation rules
          using Unicode superset glyph (U+2287) in reasoning
          prose. Canon's ASCII-safe convention (VL-006) uses
          "superset-or-equal." Not a procedure violation
          (verifiers may use mathematical notation in
          reasoning); flagged as observation, not finding.
- Three-way comparison (caller-supplied wire fields only):
    - AP: agreed by all three. Caller-supplied, required.
      Attribution: canon section 11.5 + 11.7. Grok and OpenAI
      both add section 11.1 (the I-tuple basis) as additional
      attribution; non-conflicting refinement.
    - OP: agreed by all three. Caller-supplied, required.
      Attribution: canon section 11.6 + 11.8. Same I-tuple
      refinement from Grok and OpenAI.
    - expected_manifest_version: agreed by all three as
      caller-supplied required. OpenAI explicitly flagged
      attribution as canon section 11.9 + 12.4 PLUS envelope
      spec operationalization (canon requires manifest
      property; envelope spec operationalizes the property
      as a caller-asserted wire field). Claude's schema and
      Grok cited canon clauses without flagging the envelope
      operationalization layer. This is Finding 2 below
      (G13 candidate).
    - expected_manifest_sha256: same as above.
    - context (canon's C): DIVERGED. Claude's schema:
      caller-supplied required. Grok: caller-supplied (named
      as "context elements supporting I"). OpenAI: not
      surfaced as a caller-supplied wire field; cited only in
      the Scope check as part of the I-tuple. Two-of-three
      treat C as caller-supplied; OpenAI's stricter reading
      challenges the schema-and-Grok assertion. This is
      Finding 1 below (G12 candidate, half).
    - t (time): DIVERGED. Claude's schema: not caller-supplied
      (PEP-supplied receipt time). Grok: caller-supplied or
      system-derived (left open). OpenAI: not caller-supplied
      (consistent with Claude). Two-of-three treat t as not
      caller-supplied; Grok is the outlier. This is Finding 1
      below (G12 candidate, other half).
- Finding 1 (G12 candidate): Canon section 11.1 under-specifies
  wire-origins of `I`'s components. Canon defines
  `I = (A, S, C, t)` and the evaluation rules involving AP,
  OP, AR, R. It does not say which of A, S, C, t are
  caller-supplied vs. system-derived. The three derivations
  diverged precisely on the components canon is silent about:
  Claude says "C caller, t PEP"; Grok says "C-bearing caller,
  t caller-or-system"; OpenAI says "neither C nor t is
  canon-derivable as caller-supplied." All three are
  internally consistent and procedurally clean; the
  disagreement is real and traces to canon under-specification,
  not to verifier error. Recommended track: schema makes
  explicit choices with rationale (decisions 1A and 2B in
  VL-016, planned); the under-specification itself is recorded
  as G12 in docs/restructure/04_current_vs_claimed.md, to be
  resolved either by future canon-version event or by a
  permanent "implementation choices over canon
  under-specification" appendix to the schema. Not resolved
  here.
- Finding 2 (G13 candidate): Manifest-pinning field provenance
  is mixed canon + envelope, not pure canon. OpenAI surfaced
  this explicitly: canon section 11.9 requires the manifest to
  be "deterministic, versioned, and integrity-verifiable" but
  does not say the *request* must carry caller-asserted
  version/hash fields. The expected_manifest_version and
  expected_manifest_sha256 fields are operationalizations
  added by the envelope spec (and reinforced by VL-012's
  caller-assertion convention) to realize section 11.9's
  required manifest properties on the wire. The schema's
  citation "canon basis: section 11.9 + section 12.4" is
  *required-property* basis, not *caller-supplied-field*
  derivation. The distinction matters because it documents
  honestly that not every schema field is derived from canon
  alone. Recommended track: schema attribution corrected to
  include "envelope spec operationalization" alongside canon
  clauses (decision 3B in VL-016, planned). Recorded as G13
  in docs/restructure/04_current_vs_claimed.md.
- Finding 3 (process finding, not a gap): The deliberate
  cross-model verification method - packaged request, blind
  verifiers, scope-bound task, scope-checkable response,
  primary-sources-only - worked exactly as VL-008's
  procedure intended. VL-002 confirmed G0 by three
  opportunistic derivations across separate sessions;
  VL-014's verification is the first *deliberate* application
  of the procedure to a specific artifact. The artifact
  `verification_request_vl014.md` is a working template that
  produced procedurally-clean responses from two distinct
  models. Candidate action: commit the template (or a
  generalized form) to `docs/` as a reusable artifact for
  future verifications. Not committed in this entry; planned
  as a separate small commit citing this finding. The
  generalized form would parameterize: the artifact under
  verification, the primary sources, the expected response
  structure (Derivation / Reasoning summary / Scope check),
  and the outcome categorization.
- What the verification DID NOT find:
    - No procedure violations from either verifier (compared
      to OpenAI attempts 1 and 2 in VL-008, which were
      discarded).
    - No errors in the schema's AP/OP/manifest-pinning core.
      All three derivations agreed on these fields and on
      caller-supplied required status.
    - No claim that the schema is wrong overall. The schema
      stays in place; its interpretive choices on C and t
      become explicit rather than silent (planned VL-016).
- Status implications:
    - VL-014: SINGLE-SOURCE -> DISPUTED (interpretive
      divergence on context and t; provenance gap on
      manifest-pinning fields). Not RETRACTED; the schema
      is not wrong, just under-justified at three loci.
    - VL-014 cannot transition to CONFIRMED until the
      interpretive choices are made explicit (G12 resolution
      via VL-016) and the provenance attribution is corrected
      (G13 resolution via VL-016). After VL-016, VL-014's
      status will transition DISPUTED -> CORRECTED, and a
      second verification round on the corrected schema may
      transition CORRECTED -> CONFIRMED if all three
      derivations converge on the (now-explicit) choices.
    - The schema-work build order in SPEC/request_schema.md
      ("Build order (schema-internal)") had VL-015 reserved
      for failing schema-shape tests. That work renumbers to
      VL-017 (after VL-016's schema correction). Tests
      should derive from the corrected schema, not the
      disputed one. STATE.md's "Suggested next move" will
      need updating in VL-016's session-close.
- Three decisions parked for VL-016 (recorded here for
  continuity; not actioned in this entry):
    - Decision 1A: context stays caller-supplied required;
      add explicit rationale citing G12 (canon
      under-specification) and the implementation reasoning
      (context is the canonical carrier of state-transition-
      material per section 12.1).
    - Decision 2B: t stays PEP-supplied; add explicit
      rationale citing G12 and the fail-closed reasoning
      (caller-supplied time enables time-spoofing; PEP
      receipt time is the safer default).
    - Decision 3B: manifest-pinning section grows an
      explicit note that the fields' wire-existence is an
      envelope-spec operationalization realizing section
      11.9's required properties, not direct canon clause
      derivation. Attribution updated accordingly.
- Process finding (verification artifact not committed):
  `verification_request_vl014.md` was prepared in chat and
  used directly without committing to the repository. This
  is consistent with VL-009/VL-010/VL-011 precedent for
  one-shot artifacts that produced their result and were
  not durable. However, unlike the one-shot fixup scripts
  (`fix_manifest_gitignore.sh`, `reorganize_evidence.sh`),
  the verification request is a *methodology* artifact, not
  a fixup. Methodology artifacts arguably warrant durability,
  per Finding 3 above. Candidate action: commit the request
  (or a generalized template) to `docs/` in a separate small
  commit. Recorded here, not actioned.
- Process finding (decision-recording in chat vs. ledger):
  The three decisions (1A, 2B, 3B) were made via single-line
  user response in chat ("1=A, 2=B, 3=B, draft"). They are
  recorded in this entry's "Three decisions parked for
  VL-016" block. They will be applied in VL-016's schema
  edits. The decision-recording chain (chat -> ledger ->
  schema commit) is the same shape as VL-014's "open
  question 5 accepted as proposed" decision; the precedent
  is now twice-established, which warrants a SESSION_PROTOCOL
  note when next that artifact is touched. Not actioned here.
- Files affected:
    - EVIDENCE/verification_ledger.md (this entry)
- Files NOT affected by this entry:
    - SPEC/request_schema.md (correction is VL-016, not this
      entry)
    - STATE.md (updated in VL-016's session-close, since the
      "Suggested next move" and "Known open gaps" lines need
      VL-016-specific changes)
    - CANON/canon.md (locked; G12 may eventually warrant a
      canon-version event but not in this entry)
    - MANIFEST/manifest.json (untouched)
    - IMPLEMENTATION/* (untouched)
    - docs/restructure/04_current_vs_claimed.md (G12 and G13
      additions are part of VL-016's scope, alongside the
      schema correction; recording them in artifact 04
      requires also recording the correction that resolves
      them)
- Per VL-012's self-referencing-hash finding and VL-014's
  reinforcement of the same: this entry deliberately does
  not cite its own commit hash. The commit hash will be
  reachable via `git log`.
