# G4 refused-bypass evidence (VL-038)

**Status:** Current proof.
**Commit anchor:** `33d0f5c` (the VL-038 commit; filled per the VL-012 self-referencing-hash discipline).
**Date of observation:** 2026-05-29.

## Claim

With the envelope delivered to a target (push) and an enforcing target that
verifies it against Elyon-Sol's **published, hash-locked record**
(`EVIDENCE/published_hashes.json`), the gate enforces admissibility for
routed-and-attested traffic:

- A valid call routed through the PEP is **honored** by the target (the
  target acts) exactly once.
- A call that did not come through the gate (no envelope), or carries a
  **forged**, **replayed / binding-mismatched**, **target_url-mismatched**,
  or **published-record-mismatched** envelope, is **refused** (the target
  returns a non-200 and does not act).
- The verification anchor is the committed published record, not the
  target's local disk, so the verdict is reproducible by a third party who
  clones the repository and does not trust the target's working files.

This is the first state in which the project is a **gate** (a refusal that
stops the action, holding across time via reassertion, against a defensible
source) rather than a validator that produces a correct verdict the target
can ignore.

## Method

Two-hop path exercised through the real FastAPI request/response cycle
(in-process `TestClient`; no external network). The runner is
`EVIDENCE/proofs/g4_refused_bypass_001_runner.py`.

- **Delivery.** `IMPLEMENTATION/pep.py` pushes the envelope on the ELIGIBLE
  forward as the out-of-band header `X-Elyon-Sol-Envelope` (canonical JSON
  of the envelope). The forwarded body is unchanged
  (`normalized_interaction`), so a routed call and a direct call differ only
  by the header.
- **Defensible verification.** The enforcing target compares the envelope's
  pinned canon / evaluator / manifest hashes against
  `EVIDENCE/published_hashes.json` (the published record), then reuses
  `IMPLEMENTATION/verifier.py::verify_envelope()` for `decision_sha256`
  integrity (closes forgery A2), the `request_context` / `target_url`
  binding check (closes same-state replay A3), and `reassert()` currency. It
  honors (200, acts) iff both the published-record check and
  `verify_envelope` pass; otherwise it returns 403 and does not act.

Published record anchor at observation (the three pinned hashes the target
checked against):

| Field | Value |
|---|---|
| `canon_sha256` | `d1c9d187953eed8145c2d67a98e052415ca2a4c8b722a8011280e21502b4d7bd` |
| `evaluator_sha256` | `cf311cb7fc99f170c4814eebeee63262946ac6b71099635986257887746e512b` |
| `manifest_sha256` | `a21dea8b79d459bd700ca44a30c2ca4a6efbee1447708cbc12c0bbb322d823b8` |

Six cases issued: one accept, five refuse.

## Observation

| Case | Adversary | Target HTTP status | Target acted? | Reason |
|---|---|---|---|---|
| Routed valid (end-to-end) | none | 200 | yes | `REASSERTED_AND_BOUND` |
| Direct, no envelope | A1 | 403 | no | `REF_VERIFY_ENVELOPE_ABSENT` |
| Forged (tampered, no rehash) | A2 | 403 | no | `REF_VERIFY_REASSERT_INVALIDATED` |
| Replay (envelope for X, body Y) | A3 | 403 | no | `REF_VERIFY_BINDING_MISMATCH` |
| target_url mismatch | A3 | 403 | no | `REF_VERIFY_BINDING_MISMATCH` |
| Published-record mismatch | (defensibility) | 403 | no | `REF_TARGET_PUBLISHED_RECORD_MISMATCH` |

Totals: 1 honored (200, acted), 5 refused (403, not acted), 1 total target
action. The runner asserts these invariants and exits non-zero if any fails.

The **published-record-mismatch** case is the load-bearing demonstration of
defensibility: that envelope passes local-disk `reassert()` and the binding
check, yet is refused because its pins do not match the published record.
The honor decision is therefore anchored to the committed published record,
not to the target's local files. This is the difference between verifying
the **decision** (the dodge) and verifying against a **defensible source**
(the gate property).

## Scope and honest limits

- **A1 (the declining caller)** is closeable only by the target running an
  admission policy that refuses un-attested calls; the gate cannot force a
  caller to route (artifact 08 section 4.4). The "Direct, no envelope" case
  demonstrates both the bypass and the target-side defense.
- **Cross-host transport** of the published record (the target fetching it
  from a canonical published location rather than a committed local copy) is
  named, not built; it is the remaining hardening after VL-038 (artifact 08
  section 6, the G5 deployment precondition). `reassert()` still reads local
  disk; co-located, that agrees with the published record, and the
  published-record check is what carries defensibility.
- This is enforcement for **routed-and-attested** traffic. G4 is therefore
  defensibly non-bypassable for that traffic; A1 and cross-host transport
  remain. G4 does not become a blanket RESOLVED.

## Reproducibility

1. Clone the repository and check out the VL-038 commit.
2. Confirm the published record matches live state:
   `sha256sum MANIFEST/manifest.json` equals `manifest_sha256`,
   `cat CANON/canon.lock` equals `canon_sha256`, and
   `python -c "import hashlib;print(hashlib.sha256(open('IMPLEMENTATION/evaluator.py','rb').read()).hexdigest())"`
   equals `evaluator_sha256`, all as recorded in
   `EVIDENCE/published_hashes.json`.
3. Run `PYTHONPATH=. python3 EVIDENCE/proofs/g4_refused_bypass_001_runner.py`.
   The output reproduces this proof's Observation table; the runner exits 0
   iff the invariants hold.
4. The suite-level claim is reproducible by `python -m pytest TESTS/` against
   the same commit (the enforcement tests are
   `TESTS/adversarial/test_enforcement.py`).

## Related artifacts

- Internal log: `EVIDENCE/proofs/g4_refused_bypass_001.log`.
- Runner: `EVIDENCE/proofs/g4_refused_bypass_001_runner.py`.
- Published record: `EVIDENCE/published_hashes.json`.
- Tests: `TESTS/adversarial/test_enforcement.py`; migrated
  `TESTS/test_pep.py` (forward carries the envelope header).
- Design: `docs/restructure/08_enforcement_design.md` (sections 4.2, 4.3,
  4.4, 6, 7, 8).
- Ledger entry: VL-038.
