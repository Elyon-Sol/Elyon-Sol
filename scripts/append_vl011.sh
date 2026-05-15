#!/usr/bin/env bash
# append_vl011.sh
# Appends VL-011 to the verification ledger: EVIDENCE/ reorganized into
# proofs/ and archive/; honest-base track complete.
# Status: CORRECTED. Includes process findings on staging-vs-write,
# pre-existing ASCII violations in archived files, and an untracked
# working-tree file caught at preflight.
# Does NOT commit - writes only. Inspect, then commit manually.
# Part of the Elyon-Sol restructure. Committed to scripts/ as method-of-record.

set -euo pipefail
cd "$(dirname "$0")/.."

LEDGER="EVIDENCE/verification_ledger.md"

if [ ! -f "$LEDGER" ]; then
  echo "ABORT: $LEDGER not found."; exit 1
fi

cat >> "$LEDGER" << 'LEDGER_EOF'

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
LEDGER_EOF

echo "APPENDED: VL-011 to $LEDGER"
echo ""
echo "Non-ASCII check (should print nothing of concern):"
LC_ALL=C grep -n '[^[:print:][:space:]]' "$LEDGER" && echo "WARNING: non-ASCII found above" || echo "PASS: ledger still pure ASCII"
echo ""
echo "Next steps (manual):"
echo "  cat $LEDGER          # inspect - confirm VL-011 appended cleanly, VL-001..010 intact"
echo "  git add scripts/append_vl011.sh $LEDGER"
echo "  git status           # confirm only those two files staged"
echo "  git commit -m \"Ledger VL-011: EVIDENCE/ reorganized; honest-base track complete\""
