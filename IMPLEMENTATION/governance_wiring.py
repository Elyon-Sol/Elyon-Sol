"""
Governance deployment-wiring guard (closes white-box review findings G-01, G-03,
G-04, G-06). docs/design/governance_layer_design.md sections 1.2-1.6.

The Feature-1/R1/R2 mechanisms are each fail-closed and correctly ordered (the
review found no exploitable path on a correctly-wired single-instance gate). The
residual risk is that the safety properties are OPT-IN per knob, and nothing
FORCES the safe wiring exactly when the manifest declares high-impact actions:

  - G-01: the bare static approver pin (ELYON_APPROVER_PUBKEY_HEX) enforces SoD
    only as approver_key_id != gate_key_id - a gate can self-approve under a
    DIFFERENT key_id with its own key material. R1 (role-distinctness from the
    signed key-record chain, injected via approver_trust_bootstrap) is the fix,
    but bare `uvicorn IMPLEMENTATION.pep:app` does not require it.
  - G-06: an empty resolved approver map starts silently and REFUSES every grant
    at request time (fail-closed, but not loud).
  - G-04: the [FIX H8] approval log is optional, so a configured-issuance/
    no-approval-log deployment forwards approved high-impact calls with no
    grant_consumed record -> reconcile_approvals cannot detect
    FORWARDED_WITHOUT_GRANT.
  - G-03: pending_store_from_env and replay_cache_from_env resolve independently,
    so a shared pending store WITHOUT a shared grant-replay store (or vice versa)
    leaves grant single-use per-process under horizontal scale.

This guard is a single fail-closed check, run at gate STARTUP, that fires ONLY
when the manifest declares HIGH_IMPACT actions. The default/live manifest is
HIGH_IMPACT: [] (the conscious opt-out), so the guard is a NO-OP there and the
non-high-impact path is byte-behavior-unchanged. Declaring HIGH_IMPACT is itself
an explicit opt-in, so a deployment that does so must also wire oversight safely
or the gate refuses to start.

NOT in scope (documented honest-residual): G-02 (an UNDECLARED multi-worker gate
- ELYON_REPLAY_MULTI_INSTANCE unset, ELYON_REPLAY_REDIS_URL unset, workers>1) is
not fully closable from inside a worker, which cannot observe the worker count;
the declare-or-fail guard + this G-03 coherence check narrow it, but the operator
declaration remains load-bearing. G-05 (verify_grant's expected_approval_request_id
is redundant in the pep wiring because the binding is carried by the pending-set
compare-and-delete) is defense-in-depth, not exploitable.

Pure and ABOVE G(I): reuses impact.safe_high_impact; no evaluator/envelope/canon
touch; no default-path behavior change.
"""

from IMPLEMENTATION.impact import safe_high_impact


def high_impact_declared(manifest) -> bool:
    """True iff the manifest declares any high-impact action. A malformed/missing
    HIGH_IMPACT (safe_high_impact -> None) is treated as DECLARED (fail-closed).
    Only an EXPLICIT empty HIGH_IMPACT (the conscious opt-out) is False."""
    hi = safe_high_impact(manifest)
    return hi is None or len(hi) > 0


def assert_high_impact_wiring(
    *,
    manifest,
    approver_keys,
    approver_from_injected,
    approval_log_configured,
    pending_redis_url,
    replay_redis_url,
):
    """Fail closed (raise RuntimeError) if the manifest declares HIGH_IMPACT but
    the gate is not wired to honor the oversight guarantee. NO-OP when no
    high-impact action is declared (default path byte-behavior-unchanged).

    Args (all gathered by the pep startup hook from the live gate state):
      manifest                - the SHA-pinned manifest dict (load_manifest()).
      approver_keys           - the resolved {key_id: public_key} approver map.
      approver_from_injected  - True iff the map came from the injection seam
                                (R1 / a deploy shim), not the bare static env pin.
      approval_log_configured - True iff an approval log is configured/injected.
      pending_redis_url       - ELYON_PENDING_REDIS_URL (or None).
      replay_redis_url        - ELYON_REPLAY_REDIS_URL (or None).
    """
    if not high_impact_declared(manifest):
        return

    problems = []
    if not approver_from_injected:
        problems.append(
            "[G-01] approver trust must flow through the signed key-record chain (R1: the "
            "approver_trust_bootstrap inject), not the static ELYON_APPROVER_PUBKEY_HEX pin - "
            "the bare pin's SoD is only a key_id compare a gate can defeat under a different key_id"
        )
    if not approver_keys:
        problems.append(
            "[G-06] no approver keys resolved: a high-impact gate with an EMPTY approver map can "
            "never honor an approval and silently REFUSES every grant"
        )
    if not approval_log_configured:
        problems.append(
            "[G-04] an approval log (ELYON_APPROVAL_LOG_PATH or an injected log) is required so "
            "reconcile_approvals can detect FORWARDED_WITHOUT_GRANT"
        )
    if bool(pending_redis_url) != bool(replay_redis_url):
        problems.append(
            "[G-03] the pending-set and grant-replay shared stores must be configured TOGETHER: "
            "set BOTH ELYON_PENDING_REDIS_URL and ELYON_REPLAY_REDIS_URL, or neither"
        )

    if problems:
        raise RuntimeError(
            "high-impact governance wiring is unsafe (fail-closed at startup); the manifest "
            "declares HIGH_IMPACT actions but: " + " | ".join(problems)
        )
