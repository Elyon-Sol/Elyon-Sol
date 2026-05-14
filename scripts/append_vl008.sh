#!/usr/bin/env bash
# append_vl008.sh
# Appends VL-008 to the verification ledger: the cross-model verification
# finding (task-to-source binding) and G0's third independent derivation.
# Does NOT commit - writes only. Inspect, then commit manually.
# Part of the Elyon-Sol restructure. Committed to scripts/ as method-of-record.

set -euo pipefail
cd "$(dirname "$0")/.."

LEDGER="EVIDENCE/verification_ledger.md"

if [ ! -f "$LEDGER" ]; then
  echo "ABORT: $LEDGER not found."; exit 1
fi

cat >> "$LEDGER" << 'LEDGER_EOF'

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
LEDGER_EOF

echo "APPENDED: VL-008 to $LEDGER"
echo ""
echo "Non-ASCII check (should print nothing of concern):"
LC_ALL=C grep -n '[^[:print:][:space:]]' "$LEDGER" && echo "WARNING: non-ASCII found above" || echo "PASS: ledger still pure ASCII"
echo ""
echo "Next steps (manual):"
echo "  cat $LEDGER          # inspect - confirm VL-008 appended cleanly, VL-001..007 intact"
echo "  git add scripts/append_vl008.sh $LEDGER"
echo "  git status           # confirm only those two files staged"
echo "  git commit -m \"Ledger VL-008: cross-model verification finding; G0 third derivation\""
