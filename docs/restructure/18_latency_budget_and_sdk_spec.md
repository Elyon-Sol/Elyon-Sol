# 18 - Latency budget + executor SDK

Repo path: docs/restructure/18_latency_budget_and_sdk_spec.md. Increment VL-078 (B5, artifact 13
Phase B). The final Phase-B item: measure the latency the gate adds, and package the executor-
side integration as a thin SDK with a few-line example.

## 1. Purpose and scope

Every Elyon-Sol-gated surface built so far (the reference enforcing target VL-061, the MCP server
VL-077, the wedge demo VL-066) repeats the SAME executor sequence by hand: load + anchor-verify
the published record, call `verify_envelope`, then de-dup `decision_id` against a replay cache.
B5 (a) factors that sequence into one thin, reusable component so an integrator wires admission in
a few lines, and (b) measures the p50/p99 latency the verify path adds.

In scope (VL-078):
- `IMPLEMENTATION/executor_sdk.py`: an `ExecutorGate` that holds the trust material (pinned gate
  public keys, the published record or its bytes+anchor, the target identity, a `ReplayCache`,
  an optional `clock_skew`) and exposes one method, `check(envelope, interaction) -> Decision`,
  returning `Decision(honored: bool, reason: str)`. No gate logic is re-implemented; it composes
  the production `verify_envelope` + the VL-076 replay seam.
- A few-line integration example (in the module + this spec): construct an `ExecutorGate` once,
  call `.check(...)` per request, act only if `honored`.
- `EVIDENCE/proofs/latency_budget_001_runner.py`: a harness measuring the admit (gate sign) and
  verify (`ExecutorGate.check`) paths over N iterations - p50 / p95 / p99 / mean and throughput -
  printing a budget table.

Out of scope (named, not built):
- The representative-hardware NUMBERS of record. Locus AUTHOR: the sandbox is shared / virtualized,
  so its timings are indicative, not authoritative. The harness is the SANDBOX deliverable; the
  author re-runs it on representative hardware for the recorded budget.
- Wiring the SDK into the reference target / MCP server (those keep their inline sequences;
  adopting the SDK is a later refactor). Build-then-wire: the SDK has no caller on the default
  path this increment.
- Cross-host TLS transport cost (the G5 / Phase-C surface); these numbers are in-process verify
  cost, not network cost.

## 2. The Decision contract

`ExecutorGate.check(envelope, interaction, *, now=None)` returns `Decision(honored, reason)`:
- `honored=True, reason="REASSERTED_AND_BOUND"` only when the envelope verifies (signature ->
  reassert/currency -> binding -> freshness) AND the `decision_id` is a fresh replay claim.
- `honored=False, reason=<REF_*>` on any refusal, fail-closed: a missing / anchor-mismatched
  record (`REF_TARGET_ANCHOR_MISMATCH`), a `verify_envelope` non-accept (its `REF_VERIFY_*`
  reason surfaced unchanged), or a replay (`REF_VERIFY_REPLAY`). The SDK adds no new reason code.

The integrator acts on the side effect only when `honored` is True - the SDK never performs the
side effect itself; it only decides.

## 3. Few-line integration

    from datetime import timedelta
    from IMPLEMENTATION.executor_sdk import ExecutorGate

    gate = ExecutorGate(
        pinned_public_keys=PINNED_KEYS,      # {key_id: Ed25519PublicKey}
        target_id=TARGET_ID,                 # the identity envelopes bind to
        record_bytes=open(RECORD_PATH, "rb").read(),   # the published record
    )

    decision = gate.check(envelope, interaction)
    if decision.honored:
        do_the_side_effect()                 # act
    else:
        refuse(decision.reason)              # REF_VERIFY_* / REF_TARGET_*

## 4. The latency budget

The harness reports, over N iterations on a fixed warm keypair + record:
- ADMIT path: `pep` end-to-end sign of one decision (the gate's per-call cost).
- VERIFY path: `ExecutorGate.check` on a valid envelope (the executor's added per-call cost) -
  this is the number that matters for an integrator's tail latency.
- p50 / p95 / p99 / mean (milliseconds) and throughput (calls/sec) for each.

It applies only a LOOSE regression sanity bound (not a budget): the run fails only if it cannot
collect samples or if p50 verify exceeds a generous ceiling that a non-pathological machine clears
by orders of magnitude. The authoritative budget is the AUTHOR's representative-hardware run; the
sandbox figure is recorded as indicative.

## 5. No new canonical invariant (canon section 14)

The SDK composes the existing verify + replay steps; it implements no canon section and changes
no decision. The harness only measures. No canon / evaluator / MANIFEST / envelope contract change.

## 6. Build-then-wire scope

`IMPLEMENTATION/executor_sdk.py` is NEW with no caller on the default path; evaluator.py / pep.py /
verifier.py / envelope.py / reference_target.py / mcp_server.py / replay_cache.py /
published_hashes.json are byte-unchanged (no `evaluator_sha256` roll). The SDK is a second
consumer pattern for the VL-076 replay seam; existing surfaces keep their inline sequences until a
later adopt-the-SDK refactor.

## 7. Honest ceiling

This measures in-process verify cost on shared sandbox hardware; it is indicative, not the budget
of record. It does not measure network / TLS cost (Phase C) and makes no throughput guarantee for
a real deployment. The SDK packages ergonomics; it does not change what the gate decides or move
the external-validation axis.

## 8. Acceptance (VL-078)

- `TESTS/adversarial/test_executor_sdk.py`: `ExecutorGate.check` reproduces the executor matrix
  (admitted honored; un-attested / rebound-tool / rebound-args / drifted / stale / replayed
  refused with the named reason), the few-line construction works, and a shared `ReplayCache`
  injected across two gates catches a cross-instance replay (the SDK honors the VL-076 seam).
- `EVIDENCE/proofs/latency_budget_001_runner.py`: runs, prints the admit + verify budget table,
  and exits 0 (loose sanity bound met); records the sandbox figure as indicative.
- Full suite green; the default path byte-unchanged.
