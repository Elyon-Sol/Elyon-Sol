# Typed-impact deployment runbook (turning it on)

Turns the typed-impact capability (VL-132 evaluator + VL-133 wiring, both default-off and shipped)
into LIVE behavior: benign interactions forward, high-impact ones hold for a human grant. This is a
deliberate, coordinated, operator-gated step - NOT a drop-in. Read it whole before starting.

Candidate policy manifest: `deploy/manifest_typed_v1.1.candidate.json` (validated:
`safe_manifest` accepts it; benign `read` -> forward, sensitive `transfer` -> hold, unknown ->
refuse). Its `manifest_sha256 = b1b2128a9ba544ac676580f25db4cc83dd96ad6482040f49230ff5221c4849c4`.

## 0. What flips, and the two hashes in play

- The live `MANIFEST/manifest.json` changes from flat (`HIGH_IMPACT: []`, no `interaction_types`) to
  the typed candidate. This changes **`manifest_sha256`** (`ac18ac78...` -> `b1b2128a...`).
- `evaluator_sha256` is **already** `e307fab2...` on `main` (VL-132) but is **not yet deployed** to
  the public nodes, which still carry `89a30ffe...`. So this deploy re-pins **both** hashes at once.
- The record-consuming nodes (target, authz sidecar) pin the byte-anchor `sha256(published_hashes.json)`.
  Both hash changes move that anchor, so every such node must be re-pinned in the same window or it
  refuses every envelope (`REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED` for the evaluator delta; a
  manifest-pin mismatch for the manifest delta).

## 1. Decisions required first (operator)

1. **HIGH_IMPACT policy.** The candidate declares `["role","request"]`, so `transfer`-type actions
   hold and `read`-type forward. This is a real, DECLARED policy - it replaces the current live
   "everything-holds" state, which is a *missing-key malformation* (fail-closed), with an intentional
   one. Confirm the policy (and the tool->type taxonomy in `IMPLEMENTATION/mcp_server.py`:
   `_BENIGN_TOOLS` / `_SENSITIVE_TOOLS`) matches your operations.
2. **R1 chain must be wired.** A declared `HIGH_IMPACT` makes the startup wiring-guard active
   (`governance_wiring.assert_high_impact_wiring`): the gate refuses to boot unless approver trust is
   R1-injected (via `approver_trust_bootstrap`), the approver map is non-empty, an approval log is
   configured, and the pending/replay redis stores are coherent. Ensure all four before flipping.
3. **Key-record freshness** (independent, due before 2026-08-03): re-issue serial 2 or the gate
   fail-closes to refuse-all. See `deploy/governance/make_approver_key_record.py` and the root-pin
   caveat in the full-path notes.
4. **Reconcile the deployed-commit divergence** first: the ledger records the four nodes at
   `3343e32`; GLESAC's LIVE-1 records the gate at `bd1159b`. Confirm the actual per-node commit.

## 2. Repo flip + test migration (~85 tests)

`cp deploy/manifest_typed_v1.1.candidate.json MANIFEST/manifest.json` makes the typed manifest live in
the repo. Empirically this turns **85 of 541 tests RED** (they assume the flat manifest: full-authority
callers now hold instead of forward; `interaction_for` emits reduced/typed output; version pins `1.0`
vs `1.1`). This migration is REQUIRED and is the bulk of the work:

- Tests that submit a full-authority interaction expecting a forward must either use a benign type or
  expect a 202 + drive the approval leg.
- Tests asserting the pre-typed `interaction_for` output must expect the typed shape.
- Version/sha pins move `1.0`/`ac18ac78` -> `1.1`/`b1b2128a`.

Do NOT flip until the suite is green again on the typed manifest. This is a distinct, sizable commit
(propose VL-134): "typed manifest goes live + test migration."

## 3. Regenerate the pinned record

`PYTHONPATH=. python3 EVIDENCE/published_hashes_gen.py` -> new `EVIDENCE/published_hashes.json` with
`evaluator_sha256=e307fab2...` and `manifest_sha256=b1b2128a...`. The new out-of-band anchor is
`sha256(published_hashes.json)`.

## 4. Coordinated node deploy (version-matched; siblings must match)

Sync the whole `IMPLEMENTATION/` + `MANIFEST/` + `EVIDENCE/published_hashes.json` + `deploy/governance`
to every node at the SAME commit (`git archive HEAD ... | ssh ... tar -x`), never a one-file swap:

- **publisher**: serves the new `published_hashes.json` (byte-anchor + re-signs the 5-min record).
- **target** (reference_target): re-pin `ELYON_PINNED_ROOT_SHA256` = the new anchor; runs the new code.
- **authz sidecar**: update the LOCAL `ELYON_RECORD_PATH` file AND re-pin `ELYON_PINNED_ROOT_SHA256`.
- **gate**: runs the new code; started via `approver_trust_bootstrap:app` (R1), with the approver key
  record, pinned root (`ELYON_PINNED_ROOT_KEY_ID`/`_PUBKEY_B64` - the R1 root, distinct from the
  byte-anchor), approval log, and redis coherence set.

## 5. Fail-closed boot (the wiring-guard is now load-bearing)

With a declared `HIGH_IMPACT`, the gate refuses to start unless section 1.2's four conditions hold.
A refusal to boot is the intended proof the oversight is wired - fix the wiring, don't bypass it.

## 6. Verify on the live surface

- benign `read` mint -> gate FORWARDS, target `/received` increments (the challenge-doc positive
  control, restored);
- sensitive `transfer` mint -> 202 hold -> `glesac pending --approve` (approver key in laptop
  custody) -> present grant -> target acts exactly once -> replay refused;
- the Phase 1.4 attack-suite (`EVIDENCE/proofs/attack_suite_live_runner.py`) GREEN over real transport
  (its benign positive control now forwards; add the HIL control per the full-path spec 5.2).

## 7. Readiness re-attest

On green, update `EVIDENCE/readiness.json` `REAL_TRANSPORT` naming the new run log; keep the honest
residual explicit (author-run; G5 external-stranger still open).

## 8. Rollback

Revert `MANIFEST/manifest.json` to flat, regenerate `published_hashes.json`, re-pin the OLD anchor on
target + sidecar, restart. Because the flip is one manifest file + a pin, rollback is symmetric.

---
*Prereqs: VL-132 (evaluator) and VL-133 (wiring) committed and deployed as part of this coordinated
push. 8.2 alone needs no deploy; this runbook is the first step that changes production behavior.*
