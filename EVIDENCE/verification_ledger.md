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

### VL-016 - VL-014 corrections applied; premises cross-model-verified; VL-014 -> CORRECTED
- Date: 2026-05-18
- Event: The three decisions parked in VL-015 (1A, 2B, 3B) were
  applied to `SPEC/request_schema.md` and gaps G12 and G13 were
  recorded in `docs/restructure/04_current_vs_claimed.md`. Prior
  to application, the *premises* beneath those decisions were
  submitted for independent cross-model verification under the
  procedure established in VL-008. The verification request was
  prepared as a standalone artifact
  (`verification_request_vl016_premises.md`, not yet committed
  to the repo; see process finding below) bundling: (a) the
  three premises to classify, (b) attached primary sources
  (CANON/canon.md and
  docs/restructure/05_admissibility_envelope_spec.md), and (c)
  explicit instructions that the corrections themselves and
  `SPEC/request_schema.md` were NOT to be shown to either
  verifier (premise testing is upstream of correction review;
  showing the corrections would let them anchor premise-
  reading). Both Grok and OpenAI returned procedurally-clean
  responses under VL-008 rules (a), (b), (c) with unanimous
  classifications matching the project's expected reading on
  all three premises.
- Status of VL-014: DISPUTED -> CORRECTED
- The three premises and unanimous classifications:
    - Premise 1: Canon section 11.1 defines `I = (A, S, C, t)`
      but does NOT specify whether `C` or `t` are
      caller-supplied on the wire or system-derived.
      Classification: **Under-specified.** Both verifiers cite
      section 11.1's definitional-only treatment of the tuple
      and confirm the silence across sections 11-13 and
      Appendix D.
    - Premise 2: Canon section 11.9 requires the manifest to
      be "deterministic, versioned, and integrity-verifiable"
      as a property of the manifest itself, but does NOT
      require the *request* to carry caller-asserted fields
      naming expected manifest version or expected manifest
      hash. Classification: **Supported.** Both verifiers
      cite section 11.9's property phrasing and confirm no
      canon clause in sections 9, 11, 12, or 13 imposes a
      wire-level requirement.
    - Premise 3: Given premise 1's silence, the interpretive
      choices "C caller-supplied required; t not caller-
      supplied; manifest-pinning fields' wire-existence is
      envelope-spec operationalization realizing section
      11.9's properties" are not contradicted by canon
      (i.e., canon permits these readings).
      Classification: **Supported.** Both verifiers
      enumerate the canon-side silence and cite the envelope
      spec's explicit framing of manifest-pinning fields as
      operationalizations rather than canon-native fields or
      new invariants.
- Procedure adherence (VL-008):
    - Grok:
        - Rule (a) scope-bound: response cites only canon.md
          (sections 11.1, 11.9, 12, 13, Appendix D) and the
          envelope spec (structure, field rationale, canon
          mapping). Passed.
        - Rule (b) scope-checkable: Scope check section
          present; every term and claim enumerated with file
          and section attribution; closing line affirms no
          out-of-scope material used. Passed.
        - Rule (c) prior exposure permitted: Grok has prior
          project exposure (VL-002, VL-005, VL-015).
          Permitted under rule (c) since (a) and (b) hold.
        - Verdict: response carries verification weight.
    - OpenAI:
        - Rule (a) scope-bound: response cites canon.md
          (sections 9, 11.1, 11.9, 13) and the envelope spec
          (introduction, mapping section, envelope structure
          section, relationship-to-canon section). Passed.
        - Rule (b) scope-checkable: Scope check section
          present; item-by-item citations; closing line
          affirms "No concepts or claims used in the
          derivation were sourced outside the attached
          files." Passed.
        - Rule (c) prior exposure permitted: OpenAI has prior
          project exposure (VL-008, VL-015). Permitted under
          rule (c) since (a) and (b) hold.
        - Verdict: response carries verification weight.
- Finding (strengthened framing carried forward from OpenAI's
  premise 1 reasoning): Canon's silence on `C`/`t` wire-origin
  is *meaningfully* under-specified, not merely silent.
  OpenAI's response observed that canon section 11.9 (and
  section 9) explicitly specifies derivation behavior when it
  intends to ("derived exclusively from M") for AR(I) and R(I),
  whereas no comparable wire-origin or derivation rule exists
  for `C` or `t`. The argument-from-contrast strengthens G12
  from "canon is silent" to "canon's silence is significant
  against a backdrop of demonstrated capacity to specify."
  This framing is incorporated into G12's entry in artifact 04
  and into the rationale text applied to the schema.
- Corrections applied to `SPEC/request_schema.md`:
    - Decision 1A: the `interaction.context` field section was
      augmented with a "RATIONALE AND CANON UNDER-SPECIFICATION
      (G12)" paragraph appended after the existing NAMING NOTE.
      The new paragraph names section 11.1's under-specification
      explicitly, cites section 12.1's "interaction context" as
      one of four drivers of state transition (the
      implementation reasoning for keeping `C` caller-supplied),
      and records the three-way divergence from VL-015. The
      schema's outcome (`C` caller-supplied required) is
      unchanged; the interpretive choice is now explicit.
    - Decision 2B: a new section "Canon mapping - section 11.1
      `t` (time) -> not in request" was added parallel to the
      existing "Canon mapping - section 12 -> not in request"
      section. The new section names section 11.1's
      under-specification, makes the schema's choice (`t` NOT
      caller-supplied; PEP records receipt timestamp) explicit,
      and cites section 9 (reproducibility) and section 12.4
      (invalid transitions) for the fail-closed reasoning. The
      existing canon mapping table row for `t` was updated to
      refer to this new section rather than repeating the
      rationale inline. The schema's outcome (`t` not on the
      wire) is unchanged.
    - Decision 3B: the "Canon mapping - section 11.9 ->
      manifest-pinning fields" section table was updated so
      that the attribution column for `expected_manifest_version`
      and `expected_manifest_sha256` reads "section 11.9
      (required manifest properties) + section 12.4 (invalid
      manifest transition) + envelope spec operationalization
      (Deliverable 05)" rather than the prior pure-canon
      citation. The prose under the table was expanded with a
      "PROVENANCE NOTE (G13)" paragraph making the layered
      provenance explicit: canon section 11.9 requires
      manifest properties; the decision to surface those
      properties as caller-asserted wire fields is the
      envelope-spec operationalization. The schema's behavior
      (caller-asserted required; gate refuses on mismatch per
      VL-012 convention) is unchanged.
- Gaps recorded in `docs/restructure/04_current_vs_claimed.md`:
    - G12 (canon under-specifies wire-origins of `I`'s
      components): added with status **PARTIALLY ADDRESSED**.
      The schema's interpretive choices on `C` and `t` are
      now explicit (closing the implementation-layer half of
      the gap); the canon under-specification itself remains
      open (canon-layer resolution would require a
      canon-version event under GR-1; not part of this work).
      Entry incorporates OpenAI's argument-from-contrast
      framing.
    - G13 (manifest-pinning field provenance is mixed canon +
      envelope, not pure canon): added with status
      **PARTIALLY ADDRESSED**. The schema's attribution now
      makes the layered provenance explicit (closing the
      attribution-layer half of the gap); the canon-layer
      question of whether section 11.9 should be amended to
      explicitly authorize wire-level operationalization
      remains open.
- Combined-entry rationale: the premise verification and the
  corrections it justifies are recorded in this single entry
  rather than split across two entries. Rationale: (1) the
  corrections rest entirely on the premises whose verification
  this entry records; splitting them would create two entries
  citing each other in a tight loop; (2) the chat-paste split-
  commit failure shape recorded in VL-014's process finding is
  worth avoiding repetition of; (3) the "simplify" guidance in
  the session handoff preferred a combined entry. The
  premise-verification half could have been a standalone
  entry; the choice to combine is recorded here for
  precedent-setting.
- VL-014 transitions to CORRECTED in this entry. CORRECTED is
  distinct from CONFIRMED: it means the disputed loci have
  been addressed by explicit-choice corrections, not that the
  corrected schema has itself been independently re-derived.
  A second verification round on the corrected schema could
  transition CORRECTED -> CONFIRMED if all three derivations
  converge on the (now-explicit) choices; that work is not
  part of this entry and is not currently scheduled.
- Build-order impact: the schema-work build order in
  `SPEC/request_schema.md` ("Build order (schema-internal)")
  reserved VL-015 for failing schema-shape tests; VL-015 was
  consumed by the verification round. That work renumbers
  again with this entry consuming VL-016: failing schema-shape
  tests are now proposed VL-017, the request validator
  proposed VL-018, the PEP wiring proposed VL-019, and the
  artifact 05 freshness pass proposed VL-020. STATE.md's
  "Suggested next move" is updated accordingly.
- Deferred edit (schema build-order numbering text): the
  "Build order (schema-internal)" section of
  `SPEC/request_schema.md` (around lines 423-427 at HEAD) still
  names the pre-VL-015 numbering ("VL-014 (this artifact),
  VL-015 (failing tests), VL-016 (validator), VL-017 (PEP
  wiring + G2 close), VL-018 (artifact 05 freshness pass)").
  This text is stale post-VL-016 but is NOT updated in this
  entry. Rationale: same shape as VL-013's freshness pass
  (update numbering claims when the change that necessitates
  the update lands, not in advance); VL-017's session-close
  will naturally update the schema to read "VL-017 (this
  entry's failing tests), VL-018 (validator), VL-019 (PEP
  wiring), VL-020 (artifact 05 freshness pass)" since that
  commit IS the renumbered VL-017. STATE.md and this ledger
  entry are the authoritative numbering source in the interim.
  Window of staleness: this commit to VL-017's commit.
- Process finding (verification artifact not committed):
  `verification_request_vl016_premises.md` was prepared in
  chat and used directly without committing to the repository,
  same shape as VL-015's process finding on
  `verification_request_vl014.md`. The candidate action from
  VL-015 (commit the verification request or a generalized
  template to `docs/`) is now reinforced by the second
  instance. The methodology has now been deliberately applied
  in back-to-back rounds on related questions (schema
  derivation in VL-015; premise classification in this entry);
  four verifier-runs total (Grok x2, OpenAI x2); all
  procedurally clean. The case for durability of the
  methodology artifact is stronger than after VL-015 alone.
  Recorded here, not actioned.
- Process finding (premise-testing as a distinct verification
  shape): VL-015 verified an artifact (the schema). This
  entry verifies the *premises* beneath corrections to that
  artifact, without showing the corrections. This is a
  distinct verification shape from VL-015's: it tests the
  reasoning upstream of corrections rather than the
  corrections themselves. Both shapes are useful and both
  fit under VL-008's procedure. The distinction is worth
  naming because it expands the methodology's surface from
  "verify an artifact" to "verify the reasoning beneath an
  artifact." Candidate methodology-artifact addition; not
  actioned.
- Files affected:
    - EVIDENCE/verification_ledger.md (this entry)
    - SPEC/request_schema.md (decisions 1A, 2B, 3B applied)
    - docs/restructure/04_current_vs_claimed.md (G12 and G13
      rows added)
    - STATE.md (reconciled to post-VL-016 reality)
- Files NOT affected by this entry:
    - CANON/canon.md (locked; G12 and G13 may eventually
      warrant a canon-version event but not in this entry)
    - MANIFEST/manifest.json (untouched)
    - IMPLEMENTATION/* (untouched; G2 code-close is proposed
      VL-018/VL-019)
    - TESTS/* (untouched; failing schema-shape tests are
      proposed VL-017)
    - docs/restructure/05_admissibility_envelope_spec.md
      (untouched; the envelope spec's operationalization role
      is now cited from the schema, but the spec itself does
      not need editing for this entry; freshness pass is
      proposed VL-020)
    - docs/MAINTENANCE_PROTOCOL.md (untouched; candidate
      GR-2 from VL-014 remains deferred)
- Per VL-012's self-referencing-hash finding and VL-014's
  reinforcement of the same: this entry deliberately does
  not cite its own commit hash. The commit hash will be
  reachable via `git log`.

### VL-016 follow-up - schema and artifact 04 edits applied; split commit repaired
- Date: 2026-05-18
- Event: VL-016 commit `20cd1a1` was incomplete. The ledger
  entry and STATE.md edits landed; the schema edits (decisions
  1A, 2B, 3B applied to `SPEC/request_schema.md`) and the
  artifact 04 edits (G12 and G13 rows + Priority order update
  in `docs/restructure/04_current_vs_claimed.md`) did not.
  This commit lands the missing edits. The split-commit
  failure mode is recorded as a process finding below.
- Status: VL-016 entry's "Files affected" claim in `20cd1a1`
  is now accurate as of this commit. VL-014 status (CORRECTED,
  as recorded in the VL-016 entry) is now actually
  substantiated by the schema's content.
- Failure shape: the chat-pasted execution block contained
  comment-only lines for the multi-step edits:
  ```
  # apply the 8 str_replace operations from schema_insertions.md
  # apply the 2 str_replace operations from artifact_04_rows.md
  ```
  These were instructions to perform actions, not the actions
  themselves. The shell treated them as comments and executed
  nothing. The only operations that ran were the `cp` (STATE.md)
  and `cat` (ledger append). The `git status` between
  operations correctly reported only two modified files; the
  handoff's lesson 5 ("verify the file list matches intent
  before staging") flagged this exact signal, but the commit
  proceeded.
- Files affected by this corrective commit:
    - SPEC/request_schema.md (decisions 1A, 2B, 3B applied:
      eight `str_replace` operations per
      `schema_insertions.md`, covering the `interaction.context`
      RATIONALE paragraph, the new "Canon mapping - section 11.1
      `t` (time)" section, the canon mapping table row update
      for `t`, the two manifest-pinning table row attribution
      updates, the PROVENANCE NOTE paragraph, and the two
      field-by-field attribution updates for
      `expected_manifest_version` and `expected_manifest_sha256`)
    - docs/restructure/04_current_vs_claimed.md (G12 and G13
      entries added in long structured form matching G11's
      style; Priority order updated to move G2 out of the
      bookkeeping batch into its own active track at item 4,
      paired with G12 and G13)
    - EVIDENCE/verification_ledger.md (this corrective entry)
    - STATE.md (small edit: Last-updated line updated; new
      process-finding bullet under "Known items open but not
      scheduled")
- What this entry does NOT change:
    - The substance of VL-016 (the corrections, the gap
      classifications, the premise verification record) is
      unchanged. `20cd1a1`'s VL-016 entry stands as written;
      this is execution-layer corrective work, not a revision
      of the decisions or the verification.
    - VL-014's status (CORRECTED) is unchanged.
    - The proposed renumbering of subsequent ledger entries
      (VL-017 failing tests, VL-018 validator, VL-019 PEP
      wiring, VL-020 artifact 05 freshness pass) is
      unchanged. This corrective entry does NOT consume a new
      ledger number; it is the third "follow-up" commit in
      the project's history (after VL-012's hash-correction
      `f0df14c` and VL-014's ledger-recovery `bc83346`).
- Process finding (third instance of chat-paste-eats-content):
  This is the third occurrence in the project's history of a
  chat-pasted execution block failing to do what its narrative
  said it would:
    - VL-012: `git commit -m` with embedded newlines lost
      paragraph breaks in the commit body. Lesson recorded;
      `f0df14c` corrected the hash citation.
    - VL-014: `git commit -m` failed twice in the same
      session, the second failure landing only the schema
      commit and losing the ledger + STATE.md edits;
      `bc83346` repaired the split.
    - VL-016 (this): comment-only lines in a pasted block
      silently skipped the schema and artifact 04 edits;
      this commit repairs the split.
  The first two cases were `git commit -m` mechanics. This
  third case is a different mechanism (comment lines treated
  as no-ops) but the same family of failure: the chat-paste
  surface produces a script that *reads* correct but *executes*
  incomplete. The lesson generalizes: **never paste a multi-
  step block that includes comment-form action items**; either
  paste the actual commands (no `# apply ...` placeholders) or
  break the work into one tool call per step. The handoff's
  lessons 1 and 5 cover commit-message mechanics and
  file-count verification respectively, but did not cover the
  "comment lines silently skip" case. Candidate addition to
  the project's session-mechanics lessons file (currently
  living in the next-session handoff, not yet promoted to
  `docs/`).
- Process finding (combined-entry rationale was orthogonal to
  the failure): the VL-016 entry argued that combining
  premise verification and corrections in one ledger entry
  was preferable to splitting because splitting would "repeat
  the chat-paste split-commit failure shape." That argument
  was correct about the *entry-structure* layer but did not
  prevent failure at the *execution* layer. The two layers
  are independent: an entry can be well-structured and still
  fail to be enacted by the commit that carries it. The
  combined-entry decision is not retracted; the failure mode
  was not what that decision was guarding against. Worth
  recording that ledger-entry structure and commit execution
  are separate concerns, both of which can fail independently.
- Process finding (handoff lesson 5 worked but was
  overridden): the `git status` between operations correctly
  showed "2 files changed" when intent was 4. Per lesson 5
  ("the '1 file changed' diff stat after multi-file intent
  is a signal to stop, not to commit"), this was the
  designed-in stop signal. The signal fired; the commit
  proceeded anyway. Lesson 5 is sound; the protocol gap is
  one level higher: there is no mechanism for the stop signal
  to be acted on in the chat-paste workflow, since the same
  block that produces the bad state also commits it. The
  lesson generalizes: **stop signals require an interactive
  pause, not just a printed warning.** Break the work into
  separate paste-points at every `git status` so the human-
  in-the-loop can act on what they see.
- Recovery path chosen: Option 3 of three options offered
  (revert, reset+force-push, follow-up commit). Option 3 was
  chosen for the methodology-lesson value of preserving the
  failure-mode evidence in the public commit log. Option 2
  (reset + force-push) would have produced a cleaner public
  history but erased the evidence of the failure mode; Option
  1 (revert) would have added more ceremony than help for a
  single-author repository. Option 3 matches the precedent
  set by `bc83346` (VL-014 follow-up) for exactly this shape
  of failure.
- Per VL-012's self-referencing-hash finding and VL-014's
  reinforcement of the same: this entry deliberately does
  not cite its own commit hash. The commit hash will be
  reachable via `git log`.

### VL-017a - Methodology artifacts promoted: verification-request template + apply-script template
- Date: 2026-05-18
- Event: Two methodology artifacts that were "candidate
  actions, not actioned" since VL-015 are now committed to
  `docs/methodology/` and reusable for future sessions:
    - `docs/methodology/verification_request_template.md`:
      parameterized template extracted from
      `verification_request_vl014.md` and
      `verification_request_vl016_premises.md`. Both source
      artifacts produced procedurally-clean cross-model
      responses under VL-008; the genuine common structure
      across them is what this template captures.
    - `docs/methodology/apply_script_template.py`:
      parameterized template extracted from
      `apply_vl016_followup.py` (the script that recovered the
      VL-016 split commit; commit `ebcbc89`). Captures the
      uniqueness-check + atomic-write + per-edit-delta
      pattern. Includes the `newline="\n"` fix learned from
      the VL-016 follow-up CRLF warnings.
- Numbering: this entry is VL-017a, not VL-017. VL-017 remains
  reserved for the failing schema-shape tests work named in
  the schema's "Build order (schema-internal)". Methodology
  promotion is efficiency work; it does not consume a
  build-order ledger number. The `a` suffix follows the
  established pattern (precedent: none in the ledger yet, but
  consistent with how `f0df14c` and `bc83346` are recorded as
  follow-up commits rather than as new VL-NNN entries).
- Classification: this is an **efficiency move**, not a
  **trajectory move**. The distinction is explicit in this
  entry because it informs how future sessions should weigh
  similar promotions:
    - Efficiency moves lower the friction cost of future work
      without changing the project's actual capability. They
      are unbounded in supply (there is always more
      methodology debt to close).
    - Trajectory moves change what the project can do (closed
      gaps, implemented invariants, executable evidence).
      They are bounded by the actual open work in artifact 04.
  This promotion is the efficiency analog of bringing
  artifacts 05/06 current in VL-013: maintenance that
  preserves rigor without advancing capability. The
  trajectory work (VL-017 failing tests, VL-018 validator,
  VL-019 PEP wiring, G0 build proper) is downstream.
- Why this promotion is appropriate now:
    - Both source artifacts have been used twice each (the
      verification-request shape across VL-014 and VL-016
      premises; the apply-script shape would have been used
      in VL-016's original commit if it had existed). The
      shape is proven, not speculative.
    - Both have process-finding ledger entries (VL-015's
      methodology-artifact-not-committed; VL-016's
      verification-request-not-committed and the follow-up's
      apply-script process finding) calling for promotion.
      Two ledger entries calling for an action that hasn't
      been taken is methodology debt.
    - The promotion is small and low-risk: pure additions to
      `docs/`, no canon change, no code change, no test
      change, no implementation surface affected.
- What the templates capture (and what they intentionally do
  not):
    - **Verification-request template:** the seven common
      sections across VL-014 and VL-016 premises requests
      (What you are being asked to do; Procedure; What VERB
      means/does not mean; What outcome means what;
      Submission format; Attached files; Ledger context).
      Plus optional sections (out-of-scope boundaries,
      clarifications) for when the verification question is
      narrower than the artifact under verification. The
      template does NOT prescribe the task verb, the outcome
      categories, or the submission structure - those are
      task-specific parameters. The procedure block (VL-008
      rules a/b/c) is the only fixed content; everything
      else is parameterized.
    - **Apply-script template:** the per-edit uniqueness
      check, the atomic write, the per-edit byte-delta
      reporting, the CRLF-on-read normalization, and the
      always-write-LF convention. CRLF normalization on read
      lets old_str literals always use LF regardless of the
      on-disk convention; always-writing-LF aligns with the
      repo's VL-009 standard and surfaces line-ending
      normalization in git diff where it's trackable. The
      template does NOT prescribe which files to edit or
      what edits to apply - those are filled in by the
      caller. The example edit-list structure is included
      as commented-out placeholder.
- What this entry does NOT do:
    - Add any implementation code.
    - Close any open gap (G0/G2/G4/G5/G7/G8/G9/G11/G12/G13
      all remain open at the same status as before).
    - Change the substantive G0 build track.
    - Reduce open-questions count in any artifact.
    - Re-verify any previously-verified artifact.
  This entry's contribution is purely on the efficiency
  axis. It does not move the trajectory axis.
- Process finding (the efficiency/trajectory distinction is
  worth surfacing as part of the project's ongoing
  self-assessment): a rigor-heavy project has a comfortable
  failure mode where each session produces methodology
  improvements without producing capability improvements. The
  ratio of efficiency work to trajectory work, sustained over
  multiple sessions, is a signal worth tracking. The VL-013
  through VL-017a sessions have produced significant
  methodology work and one substantive artifact (the schema);
  the next 3-5 sessions should be predominantly trajectory
  work (G2 code-close via VL-017/018/019; G0 build proper) to
  maintain a healthy ratio. Not actioned as a rule or
  governance change; recorded as project-level self-awareness.
- Process finding (template-evolution during first use): the
  apply-script template's first use in VL-017a aborted on
  edit 2 because STATE.md on disk had CRLF line endings
  (autocrlf artifact from the VL-016 follow-up checkout) and
  the script's old_str literals used LF. The script's
  atomic-write design correctly prevented partial application;
  the abort was clean. The fix - normalize CRLF to LF on read
  before matching, always write LF - was incorporated into the
  template BEFORE committing it. This is the right shape for
  template promotion: the first attempted use surfaces real
  failure modes; those failures get folded into the template;
  the template that lands has been hardened against at least
  one cycle of real-world hostility. A template promoted
  without first-use exercise would have shipped with the bug
  baked in. Lesson: methodology promotions benefit from
  going through one real application before being committed
  to docs/, even when the underlying source artifact appears
  proven. The source artifact (apply_vl016_followup.py) worked
  in its specific run; the generalization to a template
  surfaces edge cases the specific run didn't hit.
- Files affected:
    - docs/methodology/verification_request_template.md (new)
    - docs/methodology/apply_script_template.py (new)
    - EVIDENCE/verification_ledger.md (this entry)
    - STATE.md (small reconciliation update)
- Files NOT affected:
    - CANON/canon.md (locked)
    - MANIFEST/manifest.json (untouched)
    - SPEC/* (untouched)
    - IMPLEMENTATION/* (untouched)
    - TESTS/* (untouched)
    - docs/restructure/* (untouched; the methodology
      directory is parallel to restructure, not a revision
      of it)
- Per VL-012's self-referencing-hash finding and subsequent
  reinforcement: this entry deliberately does not cite its
  own commit hash. The commit hash will be reachable via
  `git log`.
### VL-017 - Failing schema-shape tests at PEP boundary (G2 build track, build-order step 2)
- Date: 2026-05-18
- Event: `TESTS/adversarial/test_request_schema.py` added, derived from `SPEC/request_schema.md` (post-VL-016, CORRECTED). 27 tests, one per refusal class named in the schema's "Rejected shapes" and "PEP boundary behavior" sections, plus a positive accepting-shape case. Against `IMPLEMENTATION/pep.py` at HEAD (commit `572828e`), all 27 fail. This is the honest G2 signal that the schema's build-order step 2 specifies: schema-derived tests precede the validator (proposed VL-018) and PEP wiring (proposed VL-019). Evidence committed as `EVIDENCE/proofs/g2_schema_failing_tests_001.log` (raw pytest output) and `EVIDENCE/proofs/g2_schema_failing_tests_001.md` (prose proof).
- Classification: **trajectory move** (per VL-017a's distinction). The test file is new capability surface that codifies what the validator must achieve. Contrast with VL-017a's pure-efficiency methodology promotion.

#### The uniform-422 finding (honest framing)
All 27 tests fail at the same wire-shape gate with HTTP 422 from Pydantic, `loc=["body","context"]`, message `Field required`. None reaches `evaluate()`. None reaches `requests.post()` (upstream_guard records zero calls across 27 cases). The failure is at the FastAPI/Pydantic boundary because `GovernedCallRequest` declares `context: Dict[str, Any]` at the top level, but every test request uses the new schema's `interaction` envelope.

What this means honestly: the tests do not, at HEAD, discriminate between the seven refusal classes. They collectively prove that the current `pep.py` wire shape is incompatible with the corrected schema's wire shape. They will become genuinely discriminating between refusal classes only once VL-019 lands the new wire shape; before VL-019 they are effectively one test with 27 names.

This is a property of the current code, not a defect in the tests. There is no way to write a test exercising the new wire shape against the current code without that test failing at the Pydantic gate. The tests' diagnostic value is post-VL-019; their G2-signal value is now.

The pre-test prediction in this session was that failures would fall in three families (Pydantic-422, silent-accept-then-403, silent-accept-then-upstream). The actual result was 100% Family 1. Recording this prediction-vs-result delta because it's the cleanest possible characterization of how incompatible the wire shapes are: there is no overlap between the new schema's accepting shape and the old PEP's accepting shape, so no test of the new shape ever reaches the old handler logic.

#### Decisions made during the session (recorded for repeatability)
- **Test file location.** `TESTS/adversarial/test_request_schema.py` (subdirectory) rather than flat `TESTS/test_request_schema.py`. The schema's build-order step 2 names the subdirectory path explicitly; the existing flat-`TESTS/` convention is implicit. When implicit convention and explicit spec diverge, the spec wins. Subdirectory created in this commit. Future test files following the schema's prescriptions go to `TESTS/adversarial/`; older flat-layout test files are not migrated.
- **Live manifest values reused.** `LIVE_MANIFEST_VERSION = "1.0"` and `LIVE_MANIFEST_SHA256 = "a21dea8b..."` taken from `TESTS/test_adversarial_evaluator.py`'s existing `SHA` constant. Rationale: the positive case must use values that *would* validate against the live manifest post-VL-019; copying from an existing passing test guarantees those values are current.
- **`upstream_guard` fixture pattern.** Monkeypatches `IMPLEMENTATION.pep.requests.post` and records calls. Negative cases assert the list is empty (schema-layer refusal must not forward); positive case asserts exactly one call (validator allows ELIGIBLE through). The fixture is per-test (function scope), so each test gets a fresh empty list.
- **Evidence convention: `.log` raw plus `.md` prose.** Matches the pattern of existing `EVIDENCE/proofs/` files. The `.log` is regenerable by re-running pytest; the `.md` is prose interpretation of what the log demonstrates. Splitting them keeps the raw evidence machine-comparable and the prose human-readable.

#### What this entry does NOT close
- G2 remains open. The validator (VL-018) and PEP wiring (VL-019) are the closure events; this entry is the failing-tests precursor.
- G7 (canon-derived tests) is unaffected; schema-shape tests are at a different layer than canon-invariant tests.
- G0 build track is unaffected; the schema is for the PEP boundary, not the canonical CCS implementation.
- No canon change. No manifest change. No implementation change. No change to existing tests.

#### Process findings

**Friction-point density in this session.** Seven file-transfer or environment-mechanics failures occurred during a session that produced ~390 lines of substantive test code:
1. Schema upload arrived with empty content (first attempt).
2. Schema upload arrived with empty content (second attempt; succeeded only via inline `cat` paste).
3. `present_files` tool call reported success but the file was not delivered to the user.
4. Multi-line chat-paste produced garbled output during heredoc input.
5. Initial `pytest` invocation failed: not on PATH; needed `python -m pytest` prefix.
6. STATE.md's suggested next-move path (`TESTS/adversarial/`) didn't match repo convention (flat `TESTS/`); decision required.
7. Typo `test_request_shema.py` created and renamed; brief confusion about whether content was preserved.

Five distinct mechanisms, same family as VL-012/VL-014/VL-016-follow-up's `chat-paste-eats-content` findings: the file-transfer surface produces outputs that *appear* successful but are silently incomplete or wrong-shape. Two are uploads-without-payload; one is a tool reporting success without delivery; one is a paste-time character mangling; one is a PATH-discovery issue; one is a layout-assumption mismatch; one is a filename typo.

The candidate action from VL-015 (commit a generalized verification-request template to `docs/methodology/`) was honored in VL-017a. The candidate action from VL-016-follow-up (promote session-mechanics-lessons file to `docs/`) is now reinforced by these seven instances and is the strongest unactioned candidate in the backlog.

**Threshold-bearing process finding (new).** Process findings without explicit thresholds accumulate as "candidate actions, not actioned" indefinitely (precedent: the verification-request template took two ledger entries calling for it before VL-017a actioned it). For this session, recording an explicit threshold for the session-mechanics-lessons promotion:

> If the next G2 build-track session (proposed VL-018) opens with **three or more** friction points in the first hour before substantive work begins, pause that session's trajectory work and promote the session-mechanics-lessons file to `docs/` as the session's deliverable. Otherwise, continue with trajectory work and the promotion remains a candidate.

The threshold is explicit, falsifiable, and self-actuating. Whether it triggers is itself a measurement worth recording in VL-018's entry.

**False stop signal on line count.** During the verification of `TESTS/adversarial/test_request_schema.py` content integrity (the `wc -l` showed 536 lines vs. my estimated ~390), I called a stop signal that turned out to be spurious; the file was structurally sound. My estimate had been computed without actually counting, treated as a hard bound, and used to gate progress. This is the exact failure mode stop signals are supposed to *prevent*, not produce.

Generalized lesson: stop signals depend on the calibration of the expected-value reference. An uncalibrated estimate used as a hard bound erodes the protocol's signal-to-noise. When my predicted value is an estimate rather than a derivation, the appropriate response to a discrepancy is *diagnostic curiosity* (run grep/file/head to characterize the actual content), not *stop* (halt all forward motion). The diagnostic curiosity ultimately succeeded, but the initial framing as a stop signal cost a turn of unnecessary alarm.

Worth promoting to the session-mechanics-lessons file (whenever that promotion happens): **calibrate the reference value before declaring a discrepancy a stop signal. An uncalibrated reference produces false stops.**

**Inherited-`.gitignore` pattern (second instance).** The pytest evidence log `EVIDENCE/proofs/g2_schema_failing_tests_001.log` was initially hidden by a `.gitignore` rule `*.log` at line 61, inherited from the Python project template. This is structurally identical to VL-010, where `MANIFEST/manifest.json` was hidden by an inherited `MANIFEST` rule. Resolution paralleled VL-010's: explicit un-ignore line `!EVIDENCE/proofs/*.log` added to `.gitignore` with a comment citing this entry, landing in the same commit as the file it had been hiding.

Two instances is a pattern. The inherited Python-template `.gitignore` makes assumptions about which file names are build/cache artifacts (`*.log`, `MANIFEST`, possibly others) that conflict with this repository's domain naming. The cost is corrective edits scattered across ledger entries.

Candidate action (not actioned in VL-017): a focused commit auditing `.gitignore` against the repo's actual domain directories (`CANON/`, `MANIFEST/`, `EVIDENCE/`, `SPEC/`, `IMPLEMENTATION/`, `TESTS/`, `docs/`) and adding explicit un-ignore rules or comments for every name that could collide with a template assumption. This is methodology debt; per VL-017a's classification, an efficiency move. Promoted to "Known items open but not scheduled" in STATE.md alongside this finding.

#### Files affected
- `TESTS/adversarial/test_request_schema.py` (new; ~390 lines)
- `EVIDENCE/proofs/g2_schema_failing_tests_001.log` (new; raw pytest output, ~58 KB)
- `EVIDENCE/proofs/g2_schema_failing_tests_001.md` (new; prose proof, 78 lines)
- `EVIDENCE/verification_ledger.md` (this entry)
- `STATE.md` (reconciliation: VL-017 lands, next action becomes VL-018 validator)
- `.gitignore` (corrective un-ignore for `EVIDENCE/proofs/*.log`; structurally parallel to VL-010; rationale in the Inherited-`.gitignore` pattern process finding above)

#### Files NOT affected
- `CANON/canon.md` (locked).
- `MANIFEST/manifest.json` (untouched).
- `SPEC/request_schema.md` (untouched in this commit; one stale forward-reference noted in the schema's "Build order" section listing `VL-014..VL-018` rather than the actual `VL-014, VL-015, VL-016, VL-017, VL-018, VL-019, VL-020` is a follow-up bookkeeping item, not actioned here).
- `IMPLEMENTATION/*` (untouched; the wire-shape change is VL-019 work).
- Existing `TESTS/test_*.py` files (untouched; regression confirmed: `TESTS/test_adversarial_evaluator.py` still 23/23 passing).
- `docs/restructure/*` (untouched; artifact 04's G2 status update is part of the closure entry, not this precursor).

Per VL-012's self-referencing-hash finding and subsequent reinforcement: this entry deliberately does not cite its own commit hash. The commit hash will be reachable via `git log`.
### VL-017b - Build-resumption invocation tested against two models; methodology template promoted

- Date: 2026-05-18
- Event: A build-resumption invocation artifact (prompt block + six-file
  primary-source bundle, targeting `IMPLEMENTATION/request_validator.py`
  per `SPEC/request_schema.md` build-order step 3) was tested against two
  fresh model sessions (Grok and OpenAI) under dry-run framing. Both
  sessions produced procedurally-clean output per the VL-008 procedure
  adapted for build (scope confirmation present, primary-source-derived
  citations present, out-of-scope items not produced). The test
  incidentally surfaced three findings about `SPEC/request_schema.md` in
  its post-VL-016 CORRECTED state. The build-resumption-request template
  extracted from the test artifact is promoted to
  `docs/methodology/build_resumption_request_template.md`, paralleling
  VL-017a's promotion of the verification-request template.
- Classification: **test result with incidental trajectory findings**.
  This is a new classification, distinct from VL-017a's pure-efficiency
  promotion and VL-017's pure-trajectory test commit. The methodology
  promotion portion is efficiency work; the three incidental spec
  findings are trajectory-shaped (they belong with G12/G13's family as
  spec-gap candidates) but were not produced under live-build conditions.
  The classification is load-bearing: downstream citation of the three
  findings must treat them as **candidates for live-build confirmation
  or supersession**, not as established findings. See the "Citation
  discipline" subsection below.

#### What the test was

A dry-run exercise to prove that the cross-model verification pattern
established for spec artifacts (VL-015, VL-016) generalizes to build
artifacts. The invocation handed each model the same six primary-source
attachments (`SPEC/request_schema.md`, `TESTS/adversarial/test_request_schema.py`,
`CANON/canon.md`, `CANON/canon.lock`, `MANIFEST/manifest.json`,
`IMPLEMENTATION/pep.py`) and the same prompt block, with explicit
dry-run framing at the top of the prompt: output would not be committed,
purpose was to prove the invocation mechanism. Both models were asked
to produce `IMPLEMENTATION/request_validator.py` per the spec's
build-order step 3, with submission format requiring procedure
confirmation, the validator file, a spec-citation map, a test-mapping
table, and gap candidates (if any).

The test was *not* a verification of either model's code output for
correctness against the 27 tests in `TESTS/adversarial/test_request_schema.py`.
That verification will happen in the live VL-018 build session when
the validator's code is committed and the test suite is run against
it. The test *was* a verification of (a) the invocation artifact's
procedural binding across models, (b) the spec's build-readiness as
observed through two independent derivations.

#### Procedural results (both models procedurally clean)

Both Grok and OpenAI produced responses meeting the four procedural
criteria specified in the test setup:

1. **Procedure confirmation present.** Both opened with explicit
   confirmation of scope adherence, naming the six attached primary
   sources.
2. **Spec-citation map present.** Both mapped each refusal code their
   validator emitted to a section of `SPEC/request_schema.md`. OpenAI's
   citations included quoted spec text; Grok's cited section names
   without quoted text. Both forms are within procedural bounds; the
   quoted-text form is more falsifiable and is reflected in the
   template's submission-format specification.
3. **Out-of-scope items not produced.** Neither model produced edits
   to `pep.py`, new tests, evidence files, or ledger entries.
4. **Two-model convergence/divergence observable.** Both models
   converged on six common refusal codes with the same trigger
   semantics; both produced spec-citation maps and test-mapping tables
   evaluable against each other.

Procedural classification per VL-008 adapted for build: both sessions
procedurally clean.

#### Convergence (the spec's stable core)

Six refusal codes were emitted by both validators with identical names
and identical trigger conditions:

- `REF_SCHEMA_TOP_LEVEL`
- `REF_SCHEMA_BAD_URL`
- `REF_SCHEMA_FLAT_KEYS`
- `REF_SCHEMA_MANIFEST_PINNING_MISSING`
- `REF_SCHEMA_TYPE_MISMATCH`
- `REF_SCHEMA_RESERVED_CCS`

Two independent derivations from the post-VL-016 CORRECTED spec, under
procedurally-clean conditions, agreed on these codes. This is the
strongest form of cross-model corroboration achieved on a build-track
artifact to date. The spec's core refusal-code definitions are
build-ready in the sense that two models extract the same set without
disagreement. Classification: candidate confirmation; subject to
live-build supersession only if the actual VL-018 validator commit
surfaces a different result against the test suite.

#### Divergence (three incidental trajectory findings, candidates)

**Finding 1 - The seventh refusal code's status is under-specified.**

`SPEC/request_schema.md` (per STATE.md's description, "implements the
seven schema-named refusal codes") presumably names seven codes. Both
models agreed on six. They diverged on the seventh:

- Grok emitted six codes; routed `test_schema_rejects_parse_error` to
  "(handled outside validator)" with the rationale that the spec's
  build-order step 1 ("parse handled by caller") puts parse-error
  outside the validator's responsibility.
- OpenAI emitted seven codes, defining `REF_SCHEMA_PARSE_ERROR` as a
  named constant but documenting in the validator's docstring that
  raw JSON parsing responsibility lives in future `pep.py` integration.
  Routed `test_schema_rejects_parse_error` to `REF_SCHEMA_PARSE_ERROR`.

Both interpretations are defensible from the spec. The under-specified
locus: should the validator name a refusal code it does not emit,
because the spec lists it among the seven? This is structurally
analogous to G12/G13 from VL-015. Recorded here as a candidate for
artifact 04 entry, *pending live-build confirmation in VL-018*. If
VL-018's validator resolves this question (by emitting six or seven
codes and citing rationale), the finding either upgrades to a real
spec gap or is superseded by VL-018's resolution.

**Finding 2 - Generic unknown keys inside `interaction` are
under-specified.**

OpenAI surfaced this explicitly as a gap candidate: the spec rejects
CCS-shaped fields with `REF_SCHEMA_RESERVED_CCS` and presumably
rejects unknown keys generally, but does not define a distinct
refusal code for non-CCS-shaped unknown keys. OpenAI's validator
falls back to existing codes; the spec does not specify whether this
is correct behavior or whether a separate code should exist.

Grok did not surface this gap (Grok's gap-candidates section reported
none). The asymmetry is itself a procedural observation: Grok may have
silently resolved this in code rather than surface it. A future
build-resumption-request template revision (proposed) should require
gap candidates to be enumerated even when zero, forcing the model to
assert absence rather than skip the section.

Classification: candidate spec gap, pending live-build confirmation.

**Finding 3 - Parse-order behavior is procedurally rather than
structurally specified.**

OpenAI's second gap candidate: the spec describes parse-order behavior
procedurally at the PEP boundary rather than structurally in the
validator's API. The validator therefore assumes already-parsed Python
objects; the contract between caller (the future `pep.py` revision)
and validator on parse-error handling is implicit rather than
specified. This is closely related to Finding 1 but addresses the
API-shape question rather than the refusal-code-existence question.

Classification: candidate spec gap, pending live-build confirmation.

#### Citation discipline (load-bearing classification)

The three findings above are classified as **candidates from a
dry-run test**, not as established findings. Downstream citation
must honor this classification. Specifically:

- The VL-018 entry (live build) may cite these findings as candidates
  it confirms, supersedes, or revises with its own resolution.
- The VL-018 entry MUST NOT cite these findings as established spec
  gaps without first running the live-build validator commit and
  observing the actual behavior. The dry-run test did not commit
  code, run tests, or expose either validator to test-suite pressure.
- Artifact 04 (`docs/restructure/04_current_vs_claimed.md`) does NOT
  receive new G-numbered entries from this test. If VL-018 confirms
  Finding 1 as a real spec gap, *that* entry creates the artifact-04
  row, with citation pointing back to both VL-017b (candidate
  surface) and VL-018 (live-build confirmation).

This citation discipline is the cost of recording test results in
the same ledger as live-build findings. The classification is
load-bearing in exactly the way VL-017a's efficiency/trajectory
distinction is load-bearing: removing the classification or treating
it as decorative degrades the ledger's evidentiary value.

#### Cross-model internal-consistency observations

Beyond the procedural-cleanliness and convergence findings, two
observations about how each model's response held together:

**Grok's test-mapping table claims routes its code would not take.**

- Grok's CCS-reserved detection uses substring match on `"ccs"` only.
  Grok's test-mapping table routes `reserved_ccs_continuity_token`
  and `reserved_ccs_prior_state_hash` to `REF_SCHEMA_RESERVED_CCS`,
  but Grok's code would not match these (no `"ccs"` substring in
  `"continuity_token"` or `"prior_state_hash"`).
- Grok's flat-key check is positionally ordered such that
  `flat_keys_archived_proof_001_shape` would hit `REF_SCHEMA_TOP_LEVEL`
  before reaching the flat-keys check, but Grok's mapping table routes
  it to `REF_SCHEMA_FLAT_KEYS`.

**OpenAI's code matches OpenAI's table.** OpenAI explicitly handles
the flat-keys-without-interaction case before raising top-level; uses
a broader substring set (`"ccs"`, `"continuity"`, `"prior_state_hash"`)
for CCS-reserved detection consistent with the test names.

This is a calibration finding about the two models on this task on
this day: OpenAI's response was more internally consistent than
Grok's. Not a generalization, not a verdict on either model. Recorded
because it would inform a future decision about which model to use
for which build-track step under what verification regime. The
specific lesson: when running two-model corroboration on a build
artifact, table-versus-code consistency is itself a procedural check,
not just an output property. Worth adding to the template's
submission-format section.

#### Build-resumption template promoted

The template extracted from this test's prompt artifact is committed
to `docs/methodology/build_resumption_request_template.md`. Structure
follows the seven-section shape of
`docs/methodology/verification_request_template.md` (VL-017a),
adapted from verification to build:

- What you are being asked to do (specifies the build artifact and
  the spec section that names it as a build-order step)
- Procedure (VL-008-bound, with the build adaptation explicit)
- What BUILD means / does not mean
- Bounded deliverable
- What outcome means what (procedurally clean complete, procedurally
  clean gap-finding, procedurally unclean)
- Submission format (procedure confirmation, the artifact, spec-citation
  map, test-mapping table or equivalent, gap candidates)
- Attached files (primary sources)
- Hard constraints (reiterating the most common procedural failures)

The template does NOT prescribe the build artifact, the spec section,
or the file list - those are task-specific parameters. The procedure
block and the submission-format requirements are the fixed content.

Two-instance promotion bar per VL-017a's pattern: this test exercises
the template against two models in one task, which is the
build-resumption analog of VL-016's premise-verification-with-two-models
shape. Whether this counts as "two instances" or "one instance with
two-model corroboration" is a methodology call; recorded here as
two-instance equivalent under the principle that the procedural
binding was demonstrated against two independent model surfaces. If
a future build-resumption session against a single model with the
template surfaces issues this two-model test did not, that's a real
finding and revises the promotion's basis; the template stays
committed in the interim.

#### What this entry does NOT do

- Commit any code to `IMPLEMENTATION/`. The validator file remains
  unauthored at HEAD; VL-018 is the live-build commit for that file.
- Close G2 or any other open gap. The candidates surfaced here are
  pending live-build confirmation per the citation discipline above.
- Run the 27 tests in `TESTS/adversarial/test_request_schema.py`. The
  uniform-422 finding from VL-017 stands at HEAD; tests become
  discriminating only after VL-018 (validator) and VL-019 (PEP wiring).
- Change the build-order trajectory. Next action remains VL-018:
  build the validator, run the tests, confirm or supersede the
  candidates from this entry.

#### Process findings

**The "dry-run vs ledger" framing question.** This session opened with
an explicit decision not to record the test, on the grounds that
context loss at session close made findings ephemeral. The decision
was revised mid-session on the argument that a test is a test, the
findings are real, and ledger completeness through classification is
preferable to ledger purity through admission gating. Recording the
revision here because the decision-shape will recur: any session
producing real findings under non-standard framing faces this question.
The answer this entry establishes: real findings enter the ledger with
honest classification of their provenance and citation discipline
constraining downstream use. Admission gating on framing grounds is
not the discipline; classification rigor is.

**Verbosity-as-deflection in methodology questions.** During the
session, the methodology argument for recording the test ran longer
than the test itself produced findings. Two turns of methodology
argument could have been one turn of "yes, record it" and one turn of
"here's the draft." Generalized lesson worth carrying into future
sessions: when the user asks a methodology question, the pull toward
arguing the methodology is itself a failure mode. The methodology
exists to enable work, not to justify discussions about work. If the
user has stated a position and asked for objective check, the check
is bounded; running the check past the bound is filler. Recorded
because this is a session-mechanics-lessons candidate of a different
shape than VL-017's friction-point findings - it is a Claude-side
behavior pattern, not an environment-side one.

**First-hour friction count per VL-017's threshold.** VL-017 set the
threshold at three friction points in the first hour for triggering
session-mechanics-lessons promotion. This session opened with one
friction point (paste corruption in the resume-protocol intent block:
the phrase "over the template instrumentation.y promotion takes
precedencent" was a mid-word fragment of the intended methodology
instruction). One point, threshold not triggered. The session
proceeded with trajectory-adjacent work (the dry-run test) rather
than session-mechanics promotion. Recording the count satisfies
VL-017's "whether it triggers is itself a measurement worth
recording" provision.

#### Files affected

- `EVIDENCE/verification_ledger.md` (this entry)
- `docs/methodology/build_resumption_request_template.md` (new)
- `STATE.md` (small reconciliation update: VL-017b lands; next action
  remains VL-018; the three candidate findings are noted in "Known
  items open but not scheduled" with explicit citation discipline)

#### Files NOT affected

- `CANON/canon.md` (locked)
- `MANIFEST/manifest.json` (untouched)
- `SPEC/*` (untouched; the three candidate findings about the spec
  do not produce edits to the spec - they produce candidate
  artifact-04 entries pending live-build confirmation)
- `IMPLEMENTATION/*` (untouched; no validator code in this entry)
- `TESTS/*` (untouched; no test changes)
- `docs/restructure/*` (untouched; artifact 04 receives no entries
  from this test per the citation discipline)
- The verification-request template at
  `docs/methodology/verification_request_template.md` (unchanged;
  the build-resumption template is a parallel artifact, not a
  revision of it)

Per VL-012's self-referencing-hash finding and subsequent reinforcement:
this entry deliberately does not cite its own commit hash. The commit
hash will be reachable via `git log`.
## VL-018 - 2026-05-18 - G2 build track: schema validator live build; three VL-017b candidates resolved with rationale; G14 surfaced

**Status:** COMMITTED
**Author:** Claude (working session with the project author)
**Verifies:** Build-order step 3 of `SPEC/request_schema.md`
(post-VL-016 CORRECTED). The schema's named validator artifact
exists in `IMPLEMENTATION/` and emits the schema-named refusal
codes per the spec's "PEP boundary behavior" section, adapted for
the validator's parsed-dict input contract.

---

### What was built

`IMPLEMENTATION/request_validator.py`, the first artifact of the
G2 build track's code half. The validator accepts an already-
parsed Python dict and returns either a normalized interaction
dict (on acceptance) or a refusal code (on rejection). It does
NOT touch `IMPLEMENTATION/pep.py`; wiring is build-order step 4
(proposed VL-019). It does NOT call `evaluate()` and does NOT
forward to any upstream; both prohibitions are structural
(the validator is a pure function over its input dict) rather
than enforced by check.

The validator exports seven module-level refusal-code constants
matching the spec's "PEP boundary behavior":

- Six emitted by `validate_request()`:
  `REF_SCHEMA_TOP_LEVEL`, `REF_SCHEMA_BAD_URL`,
  `REF_SCHEMA_FLAT_KEYS`, `REF_SCHEMA_MANIFEST_PINNING_MISSING`,
  `REF_SCHEMA_RESERVED_CCS`, `REF_SCHEMA_TYPE_MISMATCH`.
- One named but NOT emitted by `validate_request()`:
  `REF_SCHEMA_PARSE_ERROR`. See "Candidate 1 resolution" below.

In a verification run inside the working container, all 26
parametrized NEGATIVE_CASES from
`TESTS/adversarial/test_request_schema.py` plus the positive
case were exercised against `validate_request()` directly
(not through the FastAPI TestClient, which requires the PEP
wiring that VL-019 delivers); all 26 returned the expected
refusal code; the positive case returned a normalized
interaction with AP and OP sorted and deduplicated. The 27th
discriminating test (`test_schema_rejects_parse_error`) was
not exercised against the validator because parse-error is
structurally outside the validator's contract per Candidate 3
resolution below; it becomes discriminating after VL-019.

---

### Citation-discipline observance: three VL-017b candidates
### resolved

VL-017b recorded three candidate spec-gap findings from a
two-model dry-run test, each with explicit citation discipline
requiring VL-018's live build to confirm, supersede, or revise
them. Each candidate's resolution is recorded below with
rationale.

#### Candidate 3 (parse-order API-vs-procedure separation) - RESOLVED

VL-017b's Candidate 3 noted that the spec describes parse-order
behavior procedurally at the PEP boundary rather than
structurally in the validator's API, leaving implicit whether
the validator should accept raw bytes (and own parse-error
emission) or accept an already-parsed dict (and defer
parse-error to the caller).

**Resolution: validator accepts already-parsed dict.**

**Rationale:** Two direct readings of primary sources force the
choice:

1. `SPEC/request_schema.md` lines 318-333 number the PEP boundary
   behavior in six steps. Step 1 ("Parse JSON. Failure -> REFUSE
   with `REF_SCHEMA_PARSE_ERROR`") and step 6 ("Only after all of
   the above: `evaluate(interaction, manifest)` is called") are
   both explicitly *boundary* concerns, listed alongside the
   validator's steps but not internal to it. Step 6 calls
   `evaluate()` from outside the validator; step 1's parse is
   the symmetric counterpart upstream of the validator.

2. `TESTS/adversarial/test_request_schema.py` lines 467-495
   exercise parse-error by sending raw non-JSON bytes to the
   FastAPI TestClient. The test exercises the *endpoint*, not
   the validator's API directly. The test author's framing
   makes the locus explicit: parse-error is a PEP-wiring
   concern that VL-019 closes; the validator's contract is
   over parsed input.

This coupling (Candidate 3 decides Candidate 1's structural
question) was flagged in the VL-018 session opener and held
through to the live build.

**Citation:** This candidate is **superseded by VL-018**. The
question is no longer open at the spec layer; the spec's
existing text plus the test author's design choice already
implicit the answer. No spec edit needed. The validator's
docstring records the API decision and references the spec
sentences that force it.

#### Candidate 1 (seventh refusal code's status) - RESOLVED via Candidate-3 coupling

VL-017b's Candidate 1 recorded that Grok and OpenAI diverged on
whether `REF_SCHEMA_PARSE_ERROR` should be named-but-not-triggered
in the validator (OpenAI) or omitted entirely (Grok). The dry-run
test left this open pending VL-018's live build.

**Resolution: seven codes named at module level; six emitted by
the validator; the seventh (`REF_SCHEMA_PARSE_ERROR`) is named
here and emitted by `pep.py` at VL-019.**

**Rationale:** Given Candidate 3's resolution (parsed-dict
contract), `REF_SCHEMA_PARSE_ERROR` is structurally unreachable
from inside `validate_request()`. The choice then reduces to:
(a) name the constant in this module and document non-emission
[OpenAI's approach], or (b) omit it from this module and let
VL-019 define it elsewhere [Grok's approach]. The decision is
for (a) on the grounds that the spec's "PEP boundary behavior"
numbers all seven steps as a single set with a single named
vocabulary; centralizing the constants in the validator module
keeps that vocabulary discoverable from one import in VL-019,
which is preferable to scattering the schema-layer vocabulary
across two modules.

The OpenAI dry-run output that informed this decision was not
treated as authoritative (no dry-run output is authoritative
per VL-017b's citation discipline); it was treated as one of
two defensible options, and the live-build commit chose between
them with stated rationale. This is the discipline working as
intended.

**Citation:** This candidate is **superseded by VL-018** in the
sense that the implementation makes the decision; the
underlying question (which approach is right) is no longer
open. No spec edit needed; the spec's existing seven-code
enumeration is consistent with both the validator's six-code
emission and `pep.py`'s downstream emission of the seventh.

#### Candidate 2 (generic unknown keys inside `interaction`) - UPGRADED to real spec gap

VL-017b's Candidate 2 recorded OpenAI's gap-candidate flag that
the spec rejects CCS-shaped fields with `REF_SCHEMA_RESERVED_CCS`
but does not define a refusal code for non-CCS-shaped unknown
keys inside `interaction`. The dry-run test left this pending
live-build confirmation.

**Resolution: this candidate is confirmed as a real spec gap
(G14) and addressed provisionally in the validator pending the
spec edit.**

**Rationale:** Two independent surface events corroborate the
gap:

1. `TESTS/adversarial/test_request_schema.py` module docstring
   lines 31-37 explicitly flagged the gap in the VL-017 commit:
   *"The schema names a step-4 'no unknown top-level keys
   inside interaction' rule but does not enumerate a distinct
   refusal code for that case (REF_SCHEMA_RESERVED_CCS is
   narrower: keys containing 'ccs'). That case is intentionally
   NOT tested here; inventing a code would be tests driving the
   schema rather than deriving from it. Flagged in the VL-017
   ledger entry as a schema-side follow-up."*

2. VL-017b's OpenAI derivation surfaced the same gap
   independently as Candidate 2.

Two surfaces by two different paths (the test author's
spec-derived test design; an external model's spec-derived code
draft) constitute the cross-model corroboration that VL-008
defines. The gap is upgraded from VL-017b candidate status to a
real artifact-04 row in this commit: **G14 - unknown-key
refusal code under-determination inside `interaction`**, status
PARTIALLY ADDRESSED.

**Provisional validator handling:** unknown non-CCS-shaped keys
inside `interaction` are refused with `REF_SCHEMA_TYPE_MISMATCH`.
The mapping is *provisional* because TYPE_MISMATCH's natural
reading is "field type is wrong," not "field is unexpected." The
spec edit (post-VL-018, separate commit per candidate GR-2's
spec-defines-the-rename pattern) should either:

(a) define a new `REF_SCHEMA_UNKNOWN_KEY` code, or
(b) explicitly designate `REF_SCHEMA_TYPE_MISMATCH` as covering
    unknown-key cases (formalizing this provisional choice).

The provisional handling preserves fail-closed semantics; the
alternative (silent acceptance of unknown keys) would violate
the spec's step-4 prohibition. The provisional cost is a
slightly misleading refusal code on unknown-key cases; the
spec edit retires that cost.

**Citation:** Candidate 2 **confirms** as G14, with VL-017
(first surface), VL-017b (second-model corroboration), and
VL-018 (live-build confirmation + provisional code choice) all
cited in G14's artifact-04 entry.

---

### Validation order (load-bearing interpretive choice)

The validator implements one specific deterministic ordering of
the spec's step-4 sub-checks. The spec at lines 326-329 names
step-4 as a single check ("`interaction` contains exactly the
required fields named above; no unknown top-level keys inside
`interaction`; no flat-key collisions (G2). Failure -> REFUSE
with appropriate code from 'Rejected shapes.'") but does not
order the sub-checks among themselves.

The validator's chosen order:

- 4a. Flat-key check (AP/OP at top level)
- 4b. CCS-shaped keys (top-level then inside `interaction`)
- 4c. Manifest pinning presence
- 4d. Unknown-key check inside `interaction` (provisional per G14)
- 5.  Type/format checks

Rationale documented in the validator's docstring: flat-key
before CCS because a request with both is more diagnostically
clear as flat-key; CCS before pinning-missing because CCS is a
specific G0-track violation that warrants explicit naming over
a generic "field absent" message; pinning before unknown-key
because pinning is required and named while unknown-key is the
provisional catch-all.

This is one defensible ordering; alternatives exist. The order
is interpretive but consistent and reproducible. Recording it
here so that a future cross-model verification of the validator
can surface disagreement on ordering specifically rather than
disagreement masquerading as a different finding. Worth a
candidate verification round at some later point under VL-008
procedure.

---

### What this entry does NOT do

- Wire the validator into `IMPLEMENTATION/pep.py`. That is
  build-order step 4 (proposed VL-019). `pep.py` is unchanged.
  The current `GovernedCallRequest` Pydantic model still has
  `target_url` and `context` (flat) at HEAD; the wire-shape
  change to `interaction` envelope is VL-019's domain.
- Run the 27 discriminating tests in
  `TESTS/adversarial/test_request_schema.py` against the
  endpoint. The tests still fail uniformly at the Pydantic
  wire-shape gate against HEAD `pep.py`, as VL-017 recorded.
  They become discriminating only after VL-019.
- Edit `SPEC/request_schema.md`. The spec stays at the post-
  VL-016 CORRECTED state. The G14 spec edit is a separate
  forthcoming commit, matching the spec-defines-the-rename
  pattern (candidate GR-2) flagged in VL-014's process finding.
- Close G2. G2's code half is two commits: validator (this
  entry) plus PEP wiring (VL-019). G2 closes on VL-019, not
  here.
- Cross-model-verify the validator. The validator is committed
  on the strength of (a) direct derivation from spec primary
  sources, (b) 26/27 discriminating-test pass in container,
  (c) explicit rationale for all three VL-017b candidate
  resolutions. A separate cross-model verification round is
  available under VL-008 procedure if the build-resumption
  template (`docs/methodology/build_resumption_request_template.md`,
  VL-017b) is invoked against this validator; not done in this
  commit, available for any future session that wants the
  additional corroboration.

---

### Files affected

- `IMPLEMENTATION/request_validator.py` (new file)
- `EVIDENCE/verification_ledger.md` (this entry)
- `docs/restructure/04_current_vs_claimed.md` (new G14 row,
  status PARTIALLY ADDRESSED)
- `STATE.md` (reconciliation: VL-018 lands; next action becomes
  VL-019 PEP wiring; G14 added to "Known open gaps" summary;
  test-count drift acknowledged - the test file contains 28
  tests total: 26 NEGATIVE_CASES + 1 parse-error + 1 positive,
  of which 27 are discriminating; the prior "27 tests" framing
  carried VL-017's discriminating count, not the total)

### Files NOT affected

- `CANON/canon.md` (locked)
- `MANIFEST/manifest.json` (untouched)
- `SPEC/request_schema.md` (untouched; G14 spec edit is a
  separate forthcoming commit)
- `IMPLEMENTATION/pep.py` (untouched; VL-019's domain)
- `IMPLEMENTATION/evaluator.py` (untouched; evaluator's
  `manifest_integrity_valid()` is downstream of the validator
  per the spec's "PEP boundary behavior" step 6)
- `TESTS/adversarial/test_request_schema.py` (untouched; no
  test changes in this commit)
- `docs/methodology/verification_request_template.md`,
  `docs/methodology/build_resumption_request_template.md`,
  `docs/methodology/apply_script_template.py` (untouched; no
  methodology changes from this build)
- `EVIDENCE/proofs/g2_schema_failing_tests_001.log` and
  `.md` (VL-017's proof artifacts; unchanged. These remain
  honest evidence of the wire-shape incompatibility at HEAD.
  After VL-019, a new proof artifact will record the
  tests-passing-against-wired-PEP state; that artifact
  belongs to VL-019, not here)

---

### Process findings

**Source-first instruction held, with one retraction.** The
VL-018 session opener (the project author's two-message intent
block) named the source-first instruction explicitly with
VL-017b's apply-script process finding as its provenance. The
instruction held for the validator draft: all five primary
sources (`SPEC/request_schema.md`,
`TESTS/adversarial/test_request_schema.py`, `CANON/canon.md`,
`MANIFEST/manifest.json`, `IMPLEMENTATION/pep.py`) were viewed
in full before any drafting. For the apply-script draft, Claude
initially argued the script was "bounded enough" to skip
reading `docs/methodology/apply_script_template.py`; this was
a source-first violation in form (an argument against the rule
rather than an application of it) that Claude retracted in the
same turn before drafting. The template was then read in full
before the apply-script was drafted. One uploaded-file recovery
event also occurred (document text not appearing in message
body despite filename being listed; resolved by direct read
from the upload mount in one tool call); classified as a
recovery, not a friction point, because no rework resulted.
Friction-point count from environment-side sources in the first
hour: zero. Friction-point count from Claude-side sources: see
verbosity-as-deflection finding below.

**Candidate-coupling framing reduced rework.** The session
opener acknowledged Claude's framing that Candidates 1 and 3
were coupled (the API-shape decision for parsed-vs-raw input
determines whether the seventh code is structurally
reachable). This was confirmed during source reading - the
spec's step-1-and-step-6 pairing as boundary concerns made the
coupling explicit in the primary source - and held through to
the ledger entry's resolution rationale. Recording it here as
a session-mechanics observation: when a candidate set has
internal logical structure, naming the structure before source
reading (rather than discovering it during) saves an iteration.
Counterpart finding for future sessions handling multi-
candidate citation discipline.

**Verbosity-as-deflection: three instances this session.** VL-017b
recorded one instance of this pattern. This session produced three
more: (a) a methodology-clarification ask_user_input_v0 call before
the ledger draft, retracted in the next message; (b) a source-
clarification ask_user_input_v0 call before drafting the ledger
entry's prose, retracted in the next message; (c) a script-scope
ask_user_input_v0 call before drafting the apply-script that
argued the bounded-enough framing against the source-first rule,
retracted in the next message. In each case the retraction was
immediate (within one turn) and the substantive work proceeded
correctly. But three instances in one session crosses VL-017's
friction-point threshold from the Claude-side rather than the
environment-side. The threshold was originally calibrated for
environment-side friction; the Claude-side analog is now in
evidence. Generalized lesson: ask_user_input_v0 calls about
"should I read source first" or "should I treat the rule as
bounded" are themselves the rule violation - the answer is
always source-first - and the call is the friction. The check
to internalize: if the question Claude is about to ask has a
known-correct answer derivable from the session's stated rules,
the question is filler; act on the rule instead. Worth promoting
to a session-mechanics-lessons artifact under VL-017's
self-actuating-threshold provision; not actioned in VL-018
(promoting mid-session would mean abandoning trajectory work, and
the threshold was about whether to abandon, not what to do once
the work is done).

**G-numbering chosen on first-available basis.** G14 is the
first available number after G13. G6 and G10 remain numbered-
but-resolved (not reused) per the convention that gap numbers
are durable identifiers, not slot reuses. Recording this so
that future entries can cite the convention rather than re-
derive it from prior practice.

**Test-count drift acknowledged.** VL-017's "27 tests" and
STATE.md's inherited "27" count the discriminating set (26
parametrized negatives + 1 parse-error test), excluding the
positive `test_schema_accepts_valid_request`. The test file
contains 28 tests total. The drift is honest accounting
(VL-017 was counting the failing-set; this entry records the
total-vs-discriminating distinction). Not a correction of
prior entries; a clarification of what "27" means going
forward.

**Apply-script template used; build-resumption template not used.**
`docs/methodology/apply_script_template.py` (VL-017a) was used in
this session to produce `apply_vl018.py` for the STATE.md edits.
This is the second instance of apply-script-template use after
VL-017b's use of the same template (which itself was the first
instance after the template's promotion in VL-017a). The pattern
is now stable across two sessions and three distinct edit sets
(VL-017b's STATE.md reconciliation, VL-018's STATE.md edits).
`build_resumption_request_template.md` (VL-017b) was NOT used in
this session: Claude drafted the validator directly rather than
delegating to another model. Available for any future session
that wants the additional corroboration; absence of use here is
not a finding about its utility.

**Verification-ledger-range drift corrected by VL-018's apply
script.** The STATE.md line "entries VL-001 through VL-016" was
stale - VL-017, VL-017a, and VL-017b had all landed without
updating it. The VL-018 apply script's edit 2 corrects this to
"entries VL-001 through VL-018." This is a process finding about
STATE.md hygiene: the verification-ledger-range line is a
canonical-fact statement that should update with every VL-Nxx
entry, but does not have a self-actuating mechanism. Candidate
action: a STATE.md hygiene check that includes verification of
this line against the actual last-ledger-entry, runnable as part
of the session-close protocol. Not actioned in VL-018; flagged
for the session-mechanics-lessons artifact when promoted.

**False-positive blank-line-stripping diagnosis.** After the
ledger entry's first append to `verification_ledger.md`, Claude
read `tail -50` output and diagnosed blank-line stripping
between Process findings paragraphs, citing it as a recurrence
of VL-017a's process finding. Recovery plan included `git
restore` and a Python-based re-append to preserve blank lines.
At the project author's request to verify the diagnosis first,
a `diff <(tail -50 file) <(tail -50 source)` showed zero
differences: the source artifact and the appended-to file were
byte-identical at the tail. The "run-on paragraphs" Claude saw
in the terminal were a `tail -50` framing artifact - the 50-line
window started mid-paragraph and excluded the leading blank
lines that did exist. The append was clean; the diagnosis was
wrong. Generalized lesson: when investigating whether terminal
output indicates a file-content problem, distinguish "output
format issue" from "file content issue" before drawing the
conclusion. The diff primitive is the right check; `tail` alone
is not. Claude almost recorded a false process finding about
cat-append behavior; the project author's request for the diff
caught the misdiagnosis before that finding landed. Recording
this here as the actual finding to displace the false one.

Per VL-012's self-referencing-hash finding and subsequent
reinforcement: this entry deliberately does not cite its own
commit hash. The commit hash will be reachable via `git log`.
