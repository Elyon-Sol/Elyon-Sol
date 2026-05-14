#!/usr/bin/env bash
# lock_canon.sh
# Locks canon v0.9.8.4: verifies canon.md is pure ASCII, confirms both canon
# files exist, generates CANON/canon.lock, and appends VL-006 and VL-007 to
# the verification ledger.
# Does NOT commit - writes files only. Inspect, then commit manually.
# Preconditions: F4/F5/F6 verification of canon.md against the PDF is COMPLETE.
# Part of the Elyon-Sol restructure. Committed to scripts/ as method-of-record.

set -euo pipefail
cd "$(dirname "$0")/.."   # run from repo root regardless of where invoked

CANON_MD="CANON/canon.md"
CANON_PDF="CANON/canon_v0.9.8.4.pdf"
CANON_LOCK="CANON/canon.lock"
LEDGER="EVIDENCE/verification_ledger.md"

echo "=== Precondition checks ==="

# 1. Both canon files must exist.
if [ ! -f "$CANON_MD" ]; then echo "ABORT: $CANON_MD not found."; exit 1; fi
if [ ! -f "$CANON_PDF" ]; then echo "ABORT: $CANON_PDF not found."; exit 1; fi
if [ ! -f "$LEDGER" ]; then echo "ABORT: $LEDGER not found - run establish_ledger.sh first."; exit 1; fi
echo "PASS: canon.md, canon PDF, and ledger all present."

# 2. canon.md must be pure ASCII (POSIX-class check - locale-independent).
if LC_ALL=C grep -n '[^[:print:][:space:]]' "$CANON_MD" > /dev/null; then
  echo "ABORT: $CANON_MD contains non-ASCII or control characters:"
  LC_ALL=C grep -n '[^[:print:][:space:]]' "$CANON_MD"
  exit 1
fi
echo "PASS: canon.md is pure ASCII."

echo ""
echo "=== Generating lock ==="
sha256sum "$CANON_MD" | awk '{print $1}' > "$CANON_LOCK"
LOCK_HASH=$(cat "$CANON_LOCK")
echo "WROTE: $CANON_LOCK"
echo "  canon.md sha256 = $LOCK_HASH"

echo ""
echo "=== Appending VL-006 and VL-007 to ledger ==="
cat >> "$LEDGER" << 'LEDGER_EOF'

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
LEDGER_EOF

echo "APPENDED: VL-006 and VL-007 to $LEDGER"

echo ""
echo "Non-ASCII check on updated ledger (should print nothing of concern):"
LC_ALL=C grep -n '[^[:print:][:space:]]' "$LEDGER" && echo "WARNING: non-ASCII found above" || echo "PASS: ledger still pure ASCII"

echo ""
echo "=== Next steps (manual) ==="
echo "  cat $LEDGER          # inspect - confirm VL-006 and VL-007 appended cleanly"
echo "  cat $CANON_LOCK      # inspect - confirm it holds one sha256 line"
echo "  git add .gitattributes scripts/lock_canon.sh \\"
echo "          $CANON_PDF $CANON_MD $CANON_LOCK $LEDGER"
echo "  git status           # confirm staged set is exactly those six files"
echo "  git commit -m \"Lock canon v0.9.8.4; add .gitattributes; ledger VL-006, VL-007\""
