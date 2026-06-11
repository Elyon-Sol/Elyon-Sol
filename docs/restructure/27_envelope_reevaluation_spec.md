# 27 - Envelope semantic re-evaluation spec (VL-098)

Status: CONFIRMED at VL-102 (drafted SINGLE-SOURCE in the VL-098 session from primary sources
`IMPLEMENTATION/evaluator.py` and `IMPLEMENTATION/envelope.py` /
`IMPLEMENTATION/envelope_inspector.py`, read in full this session per
SESSION_PROTOCOL step 4 / VL-008 task-to-source binding). Cross-model verified at VL-102: every claim for this spec was classified Supported by two procedurally-clean verifier runs (Grok, OpenAI) under the committed VL-100 request (a third run, Gemini, was discarded as a VL-008 rule-(b) procedure violation; its one Contradicted was examined on the merits in VL-102 and found not to hold). Status: SINGLE-SOURCE -> CONFIRMED.

---

## 1. The gap this closes

The reassertion protocol names an outcome it does not perform:
`reassert()` returns RE-EVALUATE-REQUIRED when the evaluator or manifest
has transitioned (artifact 05 rows 3-4; canon section 12.4), and then no
tool performs the re-evaluation - it is left to a human. Separately, an
envelope's recorded `decision` and `condition_results` can contradict
each other (e.g. `decision: ELIGIBLE` with `condition_results.ac3:
false`), and nothing flags the contradiction; the hash region protects
those fields against TAMPER, not against an issuer that wrote an
internally inconsistent artifact.

VL-098 adds the two missing judgments to the inspector (VL-097),
completing its evaluation ladder: shape (inspect) -> provenance
(verify_issuer) -> currency (reassert) -> **semantics (reevaluate)**.

## 2. API: `reevaluate_envelope(envelope, manifest=None) -> dict`

In `IMPLEMENTATION/envelope_inspector.py` (the audit layer; one-sided
boundary preserved - the inspector imports evaluator.py, nothing imports
the inspector). Two checks, then a verdict:

### 2.1 Internal consistency (recorded decision vs recorded conditions)

`condition_results` must be present, a dict, with `ac3` / `t26` /
`manifest_integrity` all booleans (`ccs` is None at issuance per VL-029
Decision A and is NOT consulted - it is reassert-time, not issue-time).
Then, mirroring `evaluate()`'s short-circuit logic:

- `decision == "ELIGIBLE"` is consistent iff all three are True.
- `decision == "REFUSE"` is consistent iff at least one is False.
- Any other decision value, or missing/malformed `condition_results`,
  is inconsistent (fail-closed, canon section 9).

### 2.2 Live re-evaluation (would this be admitted TODAY?)

Rebuild the evaluator ctx from the envelope's recorded
`request_context` (AP, OP, expected_manifest_version,
expected_manifest_sha256 - the four fields `evaluate()` consults;
`context` does not enter AC3/T26/integrity) and run the PRODUCTION
`evaluate(ctx, manifest)` plus the three condition functions
individually, against the live `load_manifest()` by default.

Live-state semantics are inherent, not a choice: `manifest_integrity_
valid()` fails closed unless the passed manifest equals the on-disk
`MANIFEST/manifest.json` (the G11 fix, VL-053), so re-evaluation is
definitionally "against the live repository state". The `manifest`
parameter exists for test injection of malformed manifests only.

An ELIGIBLE envelope issued under a since-transitioned manifest
correctly re-evaluates REFUSE (its recorded pins no longer match) -
that IS the answer to RE-EVALUATE-REQUIRED, not a tool defect.

### 2.3 Return shape

`{"ok": True, "consistent": bool, "inconsistency": None | str,
"recorded_decision": str, "live_decision": str,
"live_conditions": {"ac3", "t26", "manifest_integrity"},
"reproduced": bool}` where `reproduced` is
`live_decision == recorded_decision`. Structural failure returns
`{"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}` (the verifier's
guard, same as inspect). The function judges; it never raises on
content (canon section 9: undecidable content -> the conservative
verdict, here inconsistent / not-reproduced).

Consistency-verdict constants (closed set): `RECORD_CONSISTENT`,
`RECORD_INCONSISTENT` are NOT emitted as strings in the return (the
booleans carry it); they exist only as the CLI's printed summary words.

## 3. CLI

`python -m IMPLEMENTATION.envelope_inspector reevaluate <envelope.json>`
prints the full result; exit 0 iff `ok and consistent and reproduced`.
No new dependency; no `--keys` (provenance is verify_issuer's job; the
ladder's rungs stay orthogonal and composable).

## 4. Honest scope (GR-3 / canon section 14)

Reuses `evaluate()` and the three condition functions VERBATIM - no
re-derivation, no new invariant, no production-module change, no
default-path caller. Re-evaluation answers exactly one question: "would
the recorded request be admitted against the live state now?" It does
NOT assert provenance (verify_issuer), currency-of-pins (reassert), or
log completeness (reconcile). A reviewer composes the rungs. Not a G5
closer.

## 5. Tests

Extend `TESTS/adversarial/test_envelope_inspector.py`: reproduced
ELIGIBLE positive control; per-condition consistency violations
(ELIGIBLE with each of ac3/t26/manifest_integrity False; REFUSE with
all True; REFUSE with one False is consistent); missing/malformed
condition_results fail-closed; ccs None is ignored; live DECISION_
CHANGED on a stale manifest pin (recorded sha != live -> live REFUSE,
reproduced False); structural fail-closed parity; CLI exit codes
(0 reproduced+consistent; 1 otherwise).
