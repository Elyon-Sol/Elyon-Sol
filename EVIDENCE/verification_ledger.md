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
