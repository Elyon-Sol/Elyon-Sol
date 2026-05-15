#!/usr/bin/env bash
# append_vl010.sh
# Appends VL-010 to the verification ledger: VL-003 reproducibility restored;
# MANIFEST/manifest.json committed; gitignore overmatch on MANIFEST/ removed.
# Status: CORRECTED. Includes process finding on caller-asserted version
# semantics (sibling of G6).
# Does NOT commit - writes only. Inspect, then commit manually.
# Part of the Elyon-Sol restructure. Committed to scripts/ as method-of-record.

set -euo pipefail
cd "$(dirname "$0")/.."

LEDGER="EVIDENCE/verification_ledger.md"

if [ ! -f "$LEDGER" ]; then
  echo "ABORT: $LEDGER not found."; exit 1
fi

cat >> "$LEDGER" << 'LEDGER_EOF'

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
LEDGER_EOF

echo "APPENDED: VL-010 to $LEDGER"
echo ""
echo "Non-ASCII check (should print nothing of concern):"
LC_ALL=C grep -n '[^[:print:][:space:]]' "$LEDGER" && echo "WARNING: non-ASCII found above" || echo "PASS: ledger still pure ASCII"
echo ""
echo "Next steps (manual):"
echo "  cat $LEDGER          # inspect - confirm VL-010 appended cleanly, VL-001..009 intact"
echo "  git add scripts/append_vl010.sh $LEDGER"
echo "  git status           # confirm only those two files staged"
echo "  git commit -m \"Ledger VL-010: VL-003 reproducibility restored; manifest committed\""
