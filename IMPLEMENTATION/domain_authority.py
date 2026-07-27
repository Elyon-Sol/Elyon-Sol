"""
Domain-authority trust - provenance + role for the policy authority whose signed
domain-verdicts the gate accepts (STAIRCASE S2; docs/design/domain_validity_D_architecture.md).

Direct mirror of approver_trust.py. There, SoD is ROLE-DISTINCTNESS in the signed
key-record chain: only a key whose signed record-role is exactly "approver" may
authorize an approval, structurally excluding the gate's "issuer" key. Here the
same discipline governs WHO may sign a domain-compliance verdict: only a key whose
signed record-role is exactly `domain_authority` is eligible. Because a key entry
carries exactly one signed role, `domain_authority` is structurally disjoint from
both `issuer` (mints envelopes) and `approver` (authorizes HIL) - so a policy
authority can never mint or approve, and the gate/approver can never sign a
verdict. That role separation is what keeps the policy agent a SENSOR, not an
actuator (the load-bearing constraint from the architecture doc).

PURE and ABOVE G(I). Consumes the SAME validated trust view
key_record_source.load_key_record_from_bytes produces ({key_id: {public_key, role,
revoked, not_before, not_after}}) - so evaluator/impact/envelope/verifier and the
whole G(I) core are byte-UNCHANGED. Returns the {key_id: public_key} map that
domain_verdict.verify_verdict / domain_control expect as `authority_public_keys`.

Build-then-wire: no caller on the default path. A key record that publishes NO
`domain_authority` role yields NO authority keys (fail-closed): a deployment using
signed-chain verdict trust MUST publish an explicit domain_authority role.
WHITE-BOX; NOT a G5 referent; no readiness predicate goes green on this module.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

# The domain-authority role token. Distinct from approver_trust.APPROVER_ROLE
# ("approver") and ISSUER_ROLE ("issuer"); a single signed role per key entry
# makes the three mutually exclusive. Only this value makes a key eligible to
# sign a domain-verdict; every other value (incl. approver/issuer/None) is
# treated as NOT-a-domain-authority (fail-closed).
DOMAIN_AUTHORITY_ROLE = "domain_authority"


def resolve_domain_authority_keys(
    key_record_trust_view: Any,
    *,
    gate_key_id: Optional[str] = None,
    now: Optional[datetime] = None,
    clock_skew: timedelta = timedelta(0),
) -> Dict[str, Any]:
    """
    From a VALIDATED signed key-record trust view (the output of
    key_record_source.load_key_record_from_bytes), return the {key_id: public_key}
    map of keys eligible to SIGN a domain-compliance verdict. Drop-in for
    domain_verdict.verify_verdict()'s / domain_control()'s `authority_public_keys`.

    A key is eligible IFF ALL hold (each fail-closed; anything not provably an
    active domain-authority key is excluded, never raised into an accepted verdict):
      - its signed record-role is EXACTLY DOMAIN_AUTHORITY_ROLE
        [ROLE-DISTINCTNESS - the load-bearing separation from issuer/approver];
      - it is NOT revoked;
      - now is within [not_before - clock_skew, not_after + clock_skew)
        (mirrors verify_envelope's VL-075 issuer-key window and approver_trust);
      - key_id != gate_key_id (belt-and-braces: a key sharing the gate's id is
        never a domain authority even if it claims the role).

    `now` defaults to datetime.now(timezone.utc). clock_skew must be non-negative
    (a negative value narrows the window - a config error) and raises ValueError.
    A non-dict view, a non-dict entry, or malformed key material contributes
    nothing rather than raising.
    """
    if clock_skew < timedelta(0):
        raise ValueError("clock_skew must be non-negative")
    if not isinstance(key_record_trust_view, dict):
        return {}
    if now is None:
        now = datetime.now(timezone.utc)

    resolved: Dict[str, Any] = {}
    for key_id, info in key_record_trust_view.items():
        if not isinstance(key_id, str) or not isinstance(info, dict):
            continue
        if gate_key_id is not None and key_id == gate_key_id:
            continue
        if info.get("role") != DOMAIN_AUTHORITY_ROLE:
            continue
        if info.get("revoked") is True:
            continue
        public_key = info.get("public_key")
        if public_key is None:
            continue
        not_before = info.get("not_before")
        not_after = info.get("not_after")
        if not isinstance(not_before, datetime) or not isinstance(not_after, datetime):
            continue
        if not (not_before - clock_skew <= now < not_after + clock_skew):
            continue
        resolved[key_id] = public_key
    return resolved
