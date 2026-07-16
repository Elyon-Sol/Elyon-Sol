"""
Governance deployment-wiring guard (closes white-box review findings G-01, G-03,
G-04, G-06). docs/design/governance_layer_design.md sections 1.2-1.6.

The Feature-1/R1/R2 mechanisms are each fail-closed and correctly ordered (the
review found no exploitable path on a correctly-wired single-instance gate). The
residual risk is that the safety properties are OPT-IN per knob, and nothing
FORCES the safe wiring exactly when the manifest declares high-impact actions:

  - G-01: the bare static approver pin (ELYON_APPROVER_PUBKEY_HEX) enforces SoD
    only as approver_key_id != gate_key_id - a gate can self-approve under a
    DIFFERENT key_id with its own key material. R1 (role-distinctness resolved
    IN-PROCESS from the signed key-record chain) is the fix, but bare
    `uvicorn IMPLEMENTATION.pep:app` does not require it.

    GL-01-REFINE (VL-124, this increment): the earlier guard checked that the
    approver map was INJECTED (not the static pin) rather than that it had
    signed-chain PROVENANCE - so a gate-controlled map injected under a different
    key_id passed both the guard and verify_grant. Injectedness is not provenance:
    a process that can set the injection seam can supply any keys. The guard now
    requires the resolved approver map to carry SIGNED_CHAIN provenance - i.e.
    pep resolved it ITSELF from the pinned-root signed key record with an explicit
    `approver` role (IMPLEMENTATION/approver_trust.resolve_approver_keys). A merely
    INJECTED or STATIC_PIN map no longer satisfies G-01. This mirrors, for the
    APPROVER key, what SES-9a/K-01 did for the ISSUER key: move trust onto the
    signed chain the gate cannot forge, in-process.
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

# Approver-trust provenance vocabulary. The guard is the authority on which
# provenance is acceptable under a high-impact manifest; pep produces exactly one
# of these for the resolved approver map. Only SIGNED_CHAIN satisfies G-01: it
# means pep resolved the map IN-PROCESS from the pinned-root signed key record
# with an explicit `approver` role, which a gate cannot forge. INJECTED (the
# test/harness seam) and STATIC_PIN (the bare env pin) are gate-controllable and
# do NOT satisfy G-01 (GL-01-refine, VL-124). NONE = nothing resolved.
APPROVER_PROV_SIGNED_CHAIN = "signed_chain"
APPROVER_PROV_INJECTED = "injected"
APPROVER_PROV_STATIC_PIN = "static_pin"
APPROVER_PROV_NONE = "none"


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
    approver_provenance,
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
      approver_provenance     - one of APPROVER_PROV_* : where the approver map
                                came from. Only SIGNED_CHAIN (pep resolved it
                                in-process from the pinned-root signed key record
                                with an explicit `approver` role) satisfies G-01;
                                INJECTED and STATIC_PIN are gate-controllable and
                                do not (GL-01-refine, VL-124).
      approval_log_configured - True iff an approval log is configured/injected.
      pending_redis_url       - ELYON_PENDING_REDIS_URL (or None).
      replay_redis_url        - ELYON_REPLAY_REDIS_URL (or None).
    """
    if not high_impact_declared(manifest):
        return

    problems = []
    if approver_provenance != APPROVER_PROV_SIGNED_CHAIN:
        problems.append(
            "[G-01] approver trust must be resolved IN-PROCESS from the pinned-root signed "
            "key-record chain with an explicit `approver` role (provenance 'signed_chain'), "
            f"not '{approver_provenance}' - an injected or static-pinned map is gate-controllable, "
            "so its SoD is only a key_id compare a gate can defeat under a different key_id. Set "
            "ELYON_APPROVER_KEY_RECORD_PATH + ELYON_PINNED_ROOT_KEY_ID + ELYON_PINNED_ROOT_PUBKEY_B64"
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
