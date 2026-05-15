#!/usr/bin/env bash
# append_vl009.sh
# Appends VL-009 to the verification ledger: ASCII-safe standard applied
# repo-wide; prior inconsistency in canon_transcription_verification_report.md
# corrected. Status: CORRECTED.
# Does NOT commit - writes only. Inspect, then commit manually.
# Part of the Elyon-Sol restructure. Committed to scripts/ as method-of-record.

set -euo pipefail
cd "$(dirname "$0")/.."

LEDGER="EVIDENCE/verification_ledger.md"

if [ ! -f "$LEDGER" ]; then
  echo "ABORT: $LEDGER not found."; exit 1
fi

cat >> "$LEDGER" << 'LEDGER_EOF'

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
LEDGER_EOF

echo "APPENDED: VL-009 to $LEDGER"
echo ""
echo "Non-ASCII check (should print nothing of concern):"
LC_ALL=C grep -n '[^[:print:][:space:]]' "$LEDGER" && echo "WARNING: non-ASCII found above" || echo "PASS: ledger still pure ASCII"
echo ""
echo "Next steps (manual):"
echo "  cat $LEDGER          # inspect - confirm VL-009 appended cleanly, VL-001..008 intact"
echo "  git add scripts/append_vl009.sh $LEDGER"
echo "  git status           # confirm only those two files staged"
echo "  git commit -m \"Ledger VL-009: ASCII-safe standard applied repo-wide; corrected\""
