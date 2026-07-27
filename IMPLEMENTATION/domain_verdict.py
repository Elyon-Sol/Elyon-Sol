"""
Domain-compliance verdict - the signed attestation a POLICY AUTHORITY produces
out-of-band about the domain-semantic validity of an already-admissible
interaction (STAIRCASE S1; docs/design/domain_validity_D_architecture.md).

A domain-verdict is to domain-compliance what an approval grant (approval.py) is
to human oversight: a small signed object produced by a NON-deterministic external
party (here a domain policy agent / engine, e.g. an OPA or Biscuit verifier, or a
clinical/financial policy service) whose output the gate verifies DETERMINISTICALLY.
This module is the deterministic verification half; producing the verdict (the
out-of-band, possibly-networked, non-deterministic step) is operator-locus and
lives OUTSIDE G(I) - the determinism firewall (canon section 9). It mirrors
approval.py field-for-field: the same Ed25519 duck-typed signing/verifying, the
same canonical_json discipline, reused not re-implemented.

WHY THIS IS SAFE (the trust model, identical to approvals):
- The policy authority is a SENSOR, never an actuator. It attests a fact
  (SAFE / UNSAFE) about the content; it does NOT admit, sign an envelope, or mint.
  It holds a `domain_authority` role, structurally distinct from the gate's
  `issuer` role and the human's `approver` role (role-distinctness enforced from
  the signed key-record chain at S2, mirroring approver_trust.py).
- The verdict is BOUND to decision_sha256 (so a verdict for action A cannot
  release action B), DOMAIN-bound, FRESH (not_after), and SINGLE-USE (verdict_id
  claimed exactly once - stateful, wired later like the grant's single-use).

WHAT verify_verdict() DECIDES vs WHAT THE WIRING DECIDES.
verify_verdict() is a PURE function of the verdict plus the trust inputs the
caller passes (expected decision hash, expected domain, the authority trust map,
the gate key id, the clock). It establishes cryptographic provenance, action +
domain binding, role separation (belt-and-braces id check), and freshness, and
surfaces the attested SAFE/UNSAFE value. It does NOT consume the verdict:
single-use (claiming verdict_id once) and any pending-set are stateful concerns
wired later (mirroring approval 1c). Build-then-wire: NO caller on the default
pep path; canon untouched; the verdict lives above G(I).
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.verifier import not_after_valid


VERDICT_VERSION = "1.0"

# The attested domain-compliance values (closed set).
VERDICT_SAFE = "SAFE"
VERDICT_UNSAFE = "UNSAFE"
_VERDICT_VALUES = frozenset({VERDICT_SAFE, VERDICT_UNSAFE})

# Keys excluded from the authority-signature region. The signature covers
# everything else - including verdict_id, decision_sha256, domain, verdict,
# not_after, and authority_key_id - so all of them are tamper-proof.
_SIGNATURE_EXCLUDED_KEYS = ("authority_signature",)

# Verdict-verification refusal vocabulary (REF_VERDICT_* boundary layer; parallels
# REF_APPROVAL_* / REF_VERIFY_*). This is the VERIFICATION (transport/boundary)
# vocabulary - distinct from the evaluator G_* admissibility reasons and from the
# D_* domain-admissibility outcomes that domain_control emits. Three clean layers.
REF_VERDICT_MALFORMED = "REF_VERDICT_MALFORMED"
REF_VERDICT_MISSING_ID = "REF_VERDICT_MISSING_ID"
REF_VERDICT_SIGNATURE_INVALID = "REF_VERDICT_SIGNATURE_INVALID"
REF_VERDICT_KEY_UNKNOWN = "REF_VERDICT_KEY_UNKNOWN"
REF_VERDICT_SOD = "REF_VERDICT_SOD"
REF_VERDICT_BINDING_MISMATCH = "REF_VERDICT_BINDING_MISMATCH"
REF_VERDICT_DOMAIN_MISMATCH = "REF_VERDICT_DOMAIN_MISMATCH"
REF_VERDICT_VALUE_INVALID = "REF_VERDICT_VALUE_INVALID"
REF_VERDICT_EXPIRED = "REF_VERDICT_EXPIRED"
# DV-03/DV-04: a caller omitted a LOAD-BEARING verification input (gate key id,
# expected decision hash, expected domain, trust map). Fail closed rather than
# silently degrade SoD or action binding.
REF_VERDICT_CONTRACT_VIOLATION = "REF_VERDICT_CONTRACT_VIOLATION"
# DV-07 / DV-08: schema version not supported; findings blob over the bound.
REF_VERDICT_VERSION_UNSUPPORTED = "REF_VERDICT_VERSION_UNSUPPORTED"
REF_VERDICT_FINDINGS_TOO_LARGE = "REF_VERDICT_FINDINGS_TOO_LARGE"
# DV-05: single-use of the verdict (verdict_id already claimed). Enforced by
# claim_verdict_once() against a ReplayCache, NOT by the pure verify_verdict.
REF_VERDICT_REPLAY = "REF_VERDICT_REPLAY"

# Upper bound on the canonical-JSON size of the optional `findings` field.
_MAX_FINDINGS_BYTES = 4096

ACCEPT_VERDICT_VALID = "VERDICT_VALID"

_REQUIRED_VERDICT_KEYS = (
    "verdict_version",
    "decision_sha256",
    "domain",
    "verdict",
    "verdict_id",
    "not_after",
    "authority_key_id",
    "authority_signature",
)


def build_verdict(
    *,
    decision_sha256: str,
    domain: str,
    verdict: str,
    verdict_id: str,
    not_after: datetime,
    findings: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Construct an UNSIGNED domain-compliance verdict.

    - decision_sha256: the exact admissible decision this verdict is about;
      binding to it transitively binds target_url, AP, OP, context and the
      manifest pins (all inside the envelope's hashed region), so a verdict for
      action A cannot release a different action B.
    - domain: the declared domain the verdict pertains to (bound + checked).
    - verdict: SAFE or UNSAFE - the attested domain-compliance value.
    - verdict_id: a unique, MANDATORY id; the key the gate claims exactly once
      for single-use. A verdict without it is rejected by verify_verdict.
    - not_after: a tz-AWARE expiry (verdict freshness). Naive -> ValueError,
      mirroring sign_envelope / build_grant.
    - findings: OPTIONAL, non-load-bearing detail (e.g. which predicate/fact
      drove UNSAFE). Signed (tamper-proof) but never gates - operator/audit only.
    """
    if not isinstance(verdict_id, str) or not verdict_id:
        raise ValueError("verdict_id is mandatory and must be a non-empty string")
    if verdict not in _VERDICT_VALUES:
        raise ValueError("verdict must be one of %s" % sorted(_VERDICT_VALUES))
    if not_after.tzinfo is None:
        raise ValueError("not_after must be timezone-aware (UTC)")
    v: Dict[str, Any] = {
        "verdict_version": VERDICT_VERSION,
        "decision_sha256": decision_sha256,
        "domain": domain,
        "verdict": verdict,
        "verdict_id": verdict_id,
        "not_after": not_after.isoformat(),
    }
    if findings is not None:
        v["findings"] = findings
    return v


def sign_verdict(verdict: Dict[str, Any], signing_key: Any, key_id: str) -> Dict[str, Any]:
    """
    Sign a verdict with the AUTHORITY key (Ed25519 duck-typed, like sign_grant).

    Returns a NEW verdict dict with authority_key_id + authority_signature added;
    the input is not modified. signing_key exposes .sign(bytes) -> bytes;
    this module does NOT import cryptography (the caller supplies the key object).
    The signature covers canonical_json(verdict minus authority_signature), which
    includes authority_key_id - so the claimed signer is itself bound.
    """
    signed = dict(verdict)
    signed["authority_key_id"] = key_id
    region = {k: v for k, v in signed.items() if k not in _SIGNATURE_EXCLUDED_KEYS}
    signature = signing_key.sign(canonical_json(region).encode("utf-8"))
    signed["authority_signature"] = signature.hex()
    return signed


def _reject(reason: str) -> Dict[str, Any]:
    return {"accepted": False, "reason": reason, "verdict": None}


def _accept(value: str) -> Dict[str, Any]:
    return {"accepted": True, "reason": ACCEPT_VERDICT_VALID, "verdict": value}


def verify_verdict(
    verdict: Any,
    *,
    expected_decision_sha256: str,
    expected_domain: str,
    authority_public_keys: Dict[str, Any],
    gate_key_id: str,
    now: Optional[datetime] = None,
    clock_skew: timedelta = timedelta(0),
    require_version: str = VERDICT_VERSION,
    freshness_waived_for_verdict_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Decide whether a domain-verdict is an authentic, bound, fresh attestation for
    the held decision. Returns {"accepted", "reason", "verdict"} where on accept
    "verdict" is the attested SAFE/UNSAFE value (and None on any rejection).

    Order (fail-closed, canon section 9; first failure wins) - mirrors verify_grant:
      1. structural presence   -> REF_VERDICT_MALFORMED
      2. mandatory verdict_id  -> REF_VERDICT_MISSING_ID
      3. separation of duties (authority_key_id != gate_key_id)
                               -> REF_VERDICT_SOD
      4. known authority key   -> REF_VERDICT_KEY_UNKNOWN
      5. signature verifies    -> REF_VERDICT_SIGNATURE_INVALID
      6. action binding (decision_sha256)
                               -> REF_VERDICT_BINDING_MISMATCH
      7. domain binding (domain == expected_domain)
                               -> REF_VERDICT_DOMAIN_MISMATCH
      8. verdict value in {SAFE, UNSAFE}
                               -> REF_VERDICT_VALUE_INVALID
      9. freshness (mandatory; via not_after_valid)
                               -> REF_VERDICT_EXPIRED
     10. accept                -> VERDICT_VALID (+ the SAFE/UNSAFE value)

    SoD is checked BEFORE the signature so a verdict the gate could mint with its
    own key is rejected even if well-signed - the policy authority must be a party
    distinct from the gate. The load-bearing custody invariant (the authority's
    role comes from the signed key-record chain, role `domain_authority` disjoint
    from issuer/approver) is the S2 wiring; authority_public_keys is the trust map
    the caller supplies (a static pin now; the signed key-record view at S2).

    NOTE the attested SAFE/UNSAFE value is NOT an admissibility decision here -
    this function only authenticates the artifact. domain_control maps a valid
    UNSAFE into a HOLD_FOR_HIL (re-determination), keeping this layer pure.
    """
    # 0. CALLER-CONTRACT (DV-03/DV-04 mitigation). These arguments are
    #    LOAD-BEARING, not optional: a None gate_key_id silently disables the
    #    SoD id-check (a gate-signed verdict would verify), and a None
    #    expected_decision_sha256 satisfies action binding by None == None
    #    (a verdict built with decision_sha256=None would release any action).
    #    Both are ordinary caller OMISSIONS, so they fail closed here rather
    #    than degrading the guarantee silently. Same discipline for the domain.
    if not isinstance(expected_decision_sha256, str) or not expected_decision_sha256:
        return _reject(REF_VERDICT_CONTRACT_VIOLATION)
    if not isinstance(expected_domain, str) or not expected_domain:
        return _reject(REF_VERDICT_CONTRACT_VIOLATION)
    if not isinstance(gate_key_id, str) or not gate_key_id:
        return _reject(REF_VERDICT_CONTRACT_VIOLATION)
    if not isinstance(authority_public_keys, dict):
        return _reject(REF_VERDICT_CONTRACT_VIOLATION)

    # 1. structural presence
    if not isinstance(verdict, dict):
        return _reject(REF_VERDICT_MALFORMED)
    for k in _REQUIRED_VERDICT_KEYS:
        if k not in verdict:
            return _reject(REF_VERDICT_MALFORMED)

    # 1b. schema version gate (DV-07): a foreign/future verdict schema is not
    #     honored under current semantics.
    if verdict.get("verdict_version") != require_version:
        return _reject(REF_VERDICT_VERSION_UNSUPPORTED)

    # 1c. findings bound (DV-08): signed and non-gating, but it flows into audit
    #     logs; refuse an unbounded blob rather than propagate it.
    if "findings" in verdict:
        try:
            if len(canonical_json(verdict["findings"])) > _MAX_FINDINGS_BYTES:
                return _reject(REF_VERDICT_FINDINGS_TOO_LARGE)
        except (TypeError, ValueError):
            return _reject(REF_VERDICT_MALFORMED)

    # 2. mandatory verdict_id
    verdict_id = verdict.get("verdict_id")
    if not isinstance(verdict_id, str) or not verdict_id:
        return _reject(REF_VERDICT_MISSING_ID)

    key_id = verdict.get("authority_key_id")
    signature_hex = verdict.get("authority_signature")
    if not isinstance(key_id, str) or not isinstance(signature_hex, str):
        return _reject(REF_VERDICT_SIGNATURE_INVALID)

    # 3. separation of duties - before signature: a gate-minted verdict is not an
    #    independent attestation even if well-formed.
    if key_id == gate_key_id:
        return _reject(REF_VERDICT_SOD)

    # 4. known authority key
    public_key = authority_public_keys.get(key_id)
    if public_key is None:
        return _reject(REF_VERDICT_KEY_UNKNOWN)

    # 5. signature verifies (duck-typed; covers everything but the signature)
    region = {k: v for k, v in verdict.items() if k not in _SIGNATURE_EXCLUDED_KEYS}
    message = canonical_json(region).encode("utf-8")
    try:
        public_key.verify(bytes.fromhex(signature_hex), message)
    except Exception:
        return _reject(REF_VERDICT_SIGNATURE_INVALID)

    # 6. action binding
    if verdict.get("decision_sha256") != expected_decision_sha256:
        return _reject(REF_VERDICT_BINDING_MISMATCH)

    # 7. domain binding
    if verdict.get("domain") != expected_domain:
        return _reject(REF_VERDICT_DOMAIN_MISMATCH)

    # 8. verdict value in the closed set
    value = verdict.get("verdict")
    if value not in _VERDICT_VALUES:
        return _reject(REF_VERDICT_VALUE_INVALID)

    # 9. freshness - mandatory presence, then the shared primitive.
    #
    # WAIVER (human-override path only). When a valid domain-override grant names
    # THIS verdict_id, not_after is waived. Rationale: a verdict lives minutes;
    # human re-determination does not. Without the waiver the verdict that
    # triggered the hold expires before the approver can act, and the grant they
    # signed becomes unusable - the override path would be decorative.
    #
    # The waiver is deliberately NARROW and cannot be turned into a bypass:
    #   * it is keyed to one exact verdict_id, supplied by the CALLER of this
    #     function (pep, from the signed grant) - not by the verdict itself;
    #   * every other check still runs first - signature, pinned authority, SoD,
    #     decision binding, domain binding, value - so the waived verdict is
    #     still a genuine authority-signed attestation about THIS decision;
    #   * an expired verdict with no matching override is still REF_VERDICT_EXPIRED.
    not_after_raw = verdict.get("not_after")
    if not_after_raw is None:
        return _reject(REF_VERDICT_EXPIRED)
    _waived = (
        isinstance(freshness_waived_for_verdict_id, str)
        and freshness_waived_for_verdict_id
        and freshness_waived_for_verdict_id == verdict_id
    )
    if not _waived and not not_after_valid(not_after_raw, now=now, clock_skew=clock_skew):
        return _reject(REF_VERDICT_EXPIRED)

    # 10. accept - surface the authenticated SAFE/UNSAFE value.
    return _accept(value)


def claim_verdict_once(
    verdict: Dict[str, Any],
    replay_cache: Any,
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Consume a verdict's SINGLE-USE claim (DV-05). Returns {"accepted", "reason"}.

    verify_verdict() is PURE and therefore stateless: it authenticates a verdict
    but cannot detect that the SAME verdict was presented before. Single-use is a
    STATEFUL concern, so - exactly as the approval grant claims grant_id via the
    ReplayCache seam (VL-076 / approval 1c) - the verdict's mandatory verdict_id
    is claimed here, atomically, against the same seam.

    Call AFTER verify_verdict() accepts and BEFORE acting on the verdict. The
    claim is keyed on verdict_id and bounded by the verdict's not_after (so the
    cache entry expires with the verdict itself). A verdict_id already claimed
    returns REF_VERDICT_REPLAY.

    replay_cache is any object satisfying the ReplayCache protocol
    (check_and_claim(id, not_after, *, now) -> True to honor / False on replay).
    """
    if not isinstance(verdict, dict):
        return _reject(REF_VERDICT_MALFORMED)
    verdict_id = verdict.get("verdict_id")
    if not isinstance(verdict_id, str) or not verdict_id:
        return _reject(REF_VERDICT_MISSING_ID)
    if replay_cache is None:
        # No cache configured: single-use CANNOT be enforced. Fail closed rather
        # than silently honoring a replayable verdict.
        return _reject(REF_VERDICT_CONTRACT_VIOLATION)

    not_after: Optional[datetime] = None
    raw = verdict.get("not_after")
    if isinstance(raw, str):
        try:
            parsed = datetime.fromisoformat(raw)
            not_after = parsed if parsed.tzinfo is not None else None
        except ValueError:
            not_after = None

    try:
        honored = replay_cache.check_and_claim(verdict_id, not_after, now=now)
    except Exception:
        return _reject(REF_VERDICT_REPLAY)  # fail closed on a cache error
    if not honored:
        return _reject(REF_VERDICT_REPLAY)
    return {"accepted": True, "reason": ACCEPT_VERDICT_VALID, "verdict": verdict.get("verdict")}
