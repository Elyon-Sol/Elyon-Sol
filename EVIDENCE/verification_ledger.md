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
- Changes (commit 45bd181):
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
- Commit: 45bd181.
