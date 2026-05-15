#!/usr/bin/env bash
# update_state_vl011.sh
# Updates STATE.md to reflect VL-011 (EVIDENCE/ reorganized) and the
# completion of the honest-base track. Switches "Next open action" to
# the G0 build track. Records the pre-existing ASCII-violation finding
# from VL-011 as a known-open item in "What is locked vs. open."
# Does NOT commit - writes only. Inspect, then commit manually.
# Part of the Elyon-Sol restructure. Committed to scripts/ as method-of-record.
#
# Replacement strategy: section-anchored awk. Each affected section is
# replaced as a contiguous range. Anchors are full-line equality matches
# against the current text at HEAD = e3b2ee9 (verified before authoring).
# If any anchor fails to match, awk emits the file unchanged and the
# postcheck diff shows zero changes - the script refuses to half-apply.

set -euo pipefail
cd "$(dirname "$0")/.."

STATE="STATE.md"

if [ ! -f "$STATE" ]; then
  echo "ABORT: $STATE not found."; exit 1
fi

# Snapshot for diff comparison.
cp "$STATE" "${STATE}.preedit"

# --- Edit 1: Last-updated line ---
# Single-line replacement, anchored on exact current text.

OLD_UPDATED="Last updated: 2026-05-15 (commit: see \`git log\` for STATE.md; honest-base step 1 done; last ledger entry VL-010)"
NEW_UPDATED="Last updated: 2026-05-15 (commit: see \`git log\` for STATE.md; honest-base track complete; last ledger entry VL-011)"

if ! grep -qxF -- "$OLD_UPDATED" "$STATE"; then
  echo "ABORT: 'Last updated' anchor not found verbatim. STATE.md may have drifted."
  rm -f "${STATE}.preedit"
  exit 1
fi

# Use awk for the substitution (line-equality match, no regex pitfalls).
awk -v old="$OLD_UPDATED" -v new="$NEW_UPDATED" '
  $0 == old { print new; next }
  { print }
' "$STATE" > "${STATE}.tmp" && mv "${STATE}.tmp" "$STATE"

# --- Edit 2: Append VL-011 bullet to "Current verified state" ---
# Add a new bullet immediately after the existing VL-010 manifest bullet.
# The VL-010 bullet ends with "from a fresh clone." - we anchor on that
# closing sentence.

VL010_TAIL="  corrective ledger entry VL-010. VL-003's derivation is now reproducible"
VL010_LAST="  from a fresh clone."

if ! grep -qxF -- "$VL010_LAST" "$STATE"; then
  echo "ABORT: VL-010 bullet tail not found verbatim. STATE.md may have drifted."
  mv "${STATE}.preedit" "$STATE"
  exit 1
fi

# Insert the VL-011 bullet after the line matching VL010_LAST.
awk -v anchor="$VL010_LAST" '
  { print }
  $0 == anchor {
    print "- **EVIDENCE/ reorganized (VL-011).** Six proof-style files split into"
    print "  `EVIDENCE/proofs/` (three current proofs plus the raw pytest log"
    print "  backing the AC^3 mutation experiment) and `EVIDENCE/archive/` (two"
    print "  interception proofs of the dead flat-key API, plus the truncated"
    print "  stability proof). Each archived file carries a prepended NON-CURRENT"
    print "  header citing the gaps that retired it (G2/G5/G9). `EVIDENCE/tmp/`"
    print "  removed. `EVIDENCE/verification_ledger.md` is unchanged at"
    print "  `EVIDENCE/` root. The honest-base track is now complete."
  }
' "$STATE" > "${STATE}.tmp" && mv "${STATE}.tmp" "$STATE"

# --- Edit 3: Replace the "Open" bullet under "What is locked vs. open" ---
# The current "Open:" bullet spans from "- **Open:**" to a blank line before
# the next section. We replace the entire bullet body in one awk pass.

OPEN_START='- **Open:** the honest-base track is in progress. Steps 1-2 are done'

if ! grep -qxF -- "$OPEN_START" "$STATE"; then
  echo "ABORT: 'Open:' bullet start not found verbatim. STATE.md may have drifted."
  mv "${STATE}.preedit" "$STATE"
  exit 1
fi

awk -v start="$OPEN_START" '
  $0 == start {
    print "- **Open:** the honest-base track is complete. The G0 build track has"
    print "  not started. One known item is recorded but not yet scheduled: the"
    print "  VL-009 ASCII-safe standard is violated by pre-existing content in"
    print "  the three `EVIDENCE/archive/` files (VL-011 process finding);"
    print "  resolution deferred to a follow-up decision (normalize / preserve"
    print "  verbatim / repo-wide pass)."
    # Consume the original Open bullet until we hit a line that does not
    # start with whitespace+text (i.e. the bullet body ends).
    in_open = 1
    next
  }
  in_open && /^[[:space:]]/ { next }   # still inside the original bullet body
  in_open && /^$/ { in_open = 0; print; next }  # blank line ends it
  in_open && /^-/ { in_open = 0; print; next }  # next bullet ends it
  in_open && /^#/ { in_open = 0; print; next }  # next heading ends it
  { print }
' "$STATE" > "${STATE}.tmp" && mv "${STATE}.tmp" "$STATE"

# --- Edit 4: Replace "Next open action" section body ---
# From the "## Next open action" heading to (but not including) the next
# top-level "## " heading.

NEXT_HEADING='## Next open action'

if ! grep -qxF -- "$NEXT_HEADING" "$STATE"; then
  echo "ABORT: 'Next open action' heading not found verbatim. STATE.md may have drifted."
  mv "${STATE}.preedit" "$STATE"
  exit 1
fi

awk -v heading="$NEXT_HEADING" '
  $0 == heading {
    print heading
    print ""
    print "Begin the **G0 build track**: implement canonical CCS via the admissibility"
    print "envelope (`docs/restructure/05_admissibility_envelope_spec.md`), with"
    print "canon-derived tests (G7)."
    print ""
    print "The honest-base track is complete:"
    print ""
    print "1. **Artifact 01 reconciled against HEAD.** Done (commit 148e725)."
    print "2. **Maintenance protocol artifact added with GR-1.** Done (commit 6f7f0e7)."
    print "3. **MANIFEST/manifest.json committed** (sub-thread surfaced during step 1)."
    print "   Done (VL-010, commit c0867a6)."
    print "4. **EVIDENCE/ reorganized into proofs/ and archive/.** Done"
    print "   (VL-011, commit e6345a5)."
    print ""
    print "Priority order for the G0 build track is in"
    print "`docs/restructure/04_current_vs_claimed.md` under \"Priority order.\""
    print "Suggested first move: the G0 rename + G6 + G10 disambiguation pass"
    print "(priority item 3), since it unblocks honest claims in public framing (G3)"
    print "and is a single naming-convention decision."
    print ""
    print "One known item is open but not scheduled: the VL-011 process finding on"
    print "pre-existing non-ASCII bytes in `EVIDENCE/archive/` files. Resolution is"
    print "a decision (normalize / preserve verbatim / VL-009 repo-wide pass), not"
    print "a blocking task on the G0 build track."
    print ""
    print "---"
    print ""
    in_section = 1
    next
  }
  in_section && /^## / { in_section = 0; print; next }  # next section ends it
  in_section { next }
  { print }
' "$STATE" > "${STATE}.tmp" && mv "${STATE}.tmp" "$STATE"

# --- Postcheck: verify edits landed ---

echo "=== Diff (preedit -> edited) ==="
diff -u "${STATE}.preedit" "$STATE" || true
echo
echo "=== Anchor verification (all four edits must have landed) ==="

declare -i pass=0 fail=0
check() {
  local label="$1"; local expr="$2"
  if grep -qF -- "$expr" "$STATE"; then
    echo "  [OK]   $label"
    pass+=1
  else
    echo "  [FAIL] $label"
    fail+=1
  fi
}
check "Edit 1: 'last ledger entry VL-011'" "last ledger entry VL-011"
check "Edit 2: 'EVIDENCE/ reorganized (VL-011)'" "EVIDENCE/ reorganized (VL-011)"
check "Edit 3: 'honest-base track is complete' (in Open bullet)" "**Open:** the honest-base track is complete"
check "Edit 4: 'Begin the **G0 build track**'" "Begin the **G0 build track**"
echo

echo "=== Non-ASCII check ==="
if LC_ALL=C grep -n '[^[:print:][:space:]]' "$STATE"; then
  echo "WARNING: non-ASCII bytes in STATE.md (see above)"
else
  echo "PASS: STATE.md pure ASCII"
fi
echo

if [ "$fail" -gt 0 ]; then
  echo "ABORT: ${fail} anchor(s) failed. Restoring preedit."
  mv "${STATE}.preedit" "$STATE"
  exit 1
fi

# Specific inverted check: the stale sentence MUST be gone.
if grep -qF -- "Steps 1-2 are done" "$STATE"; then
  echo "ABORT: stale 'Steps 1-2 are done' sentence still present. Restoring preedit."
  mv "${STATE}.preedit" "$STATE"
  exit 1
fi

rm -f "${STATE}.preedit"

echo "=== UPDATED: $STATE ==="
echo ""
echo "Next steps (manual):"
echo "  cat $STATE                # inspect - confirm narrative flow is intact"
echo "  git add scripts/update_state_vl011.sh $STATE"
echo "  git status                # confirm only those two files staged"
echo "  git commit -m \"Update STATE.md: VL-011, honest-base track complete; next action is G0 build track\""
