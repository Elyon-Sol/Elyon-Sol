"""
Domain control - the state machine that composes D-structural validity with the
out-of-band domain-verdict, and decides how an admissible interaction is handled
in its domain (STAIRCASE S4; docs/design/domain_validity_D_architecture.md).

This is the glue described as "control an interaction with the policy agent." It
answers, for an interaction that has ALREADY passed G(I) admissibility:

    PASS               - domain-valid; nothing more required; forward.
    HOLD_FOR_VERDICT   - a signed out-of-band policy verdict is required (or the
                         one supplied did not verify); acquire/replace it.
    HOLD_FOR_HIL       - an AUTHENTIC verdict says UNSAFE; a human must
                         re-determine (route into the 202/signed-grant path;
                         resolution -> gate re-mints -> required re-pin).
    REFUSE             - the content is structurally domain-INVALID (D-structural).

=========================================================================
The determinism firewall, expressed in code
=========================================================================
control() is PURE with respect to its inputs. The domain verdict is passed IN as
an argument; control() NEVER calls the policy agent, opens a socket, or does any
non-deterministic I/O. The non-deterministic step (obtaining the verdict) happens
OUTSIDE, in the operator/monitor layer, and its signed result is handed to this
function. So the decision logic stays deterministic (canon section 9) even though
the domain judgment upstream of it is not - exactly as verify_grant() is pure
while the human who signed the grant is not.

=========================================================================
Layering / namespaces (three clean layers)
=========================================================================
- G_*  : evaluator admissibility reasons (evaluator.py).
- D_*  : domain-admissibility outcomes (domain_validity.py + the three below).
- REF_*: boundary/transport verification (domain_verdict.verify_verdict, etc.).
control() returns a D_* code; a failed verdict's REF_VERDICT_* reason is carried
in `detail` for audit, never conflated with the admissibility code.

Build-then-wire: NO caller on the default pep path. Frozen core untouched.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from IMPLEMENTATION.domain_validity import (
    assess, safe_domain_manifest, D_MANIFEST_MALFORMED,
)
from IMPLEMENTATION.domain_verdict import verify_verdict, VERDICT_UNSAFE


# ---------------------------------------------------------------------------
# Control outcomes (closed set)
# ---------------------------------------------------------------------------

CONTROL_PASS = "PASS"
CONTROL_HOLD_FOR_VERDICT = "HOLD_FOR_VERDICT"
CONTROL_HOLD_FOR_HIL = "HOLD_FOR_HIL"
CONTROL_REFUSE = "REFUSE"

# ---------------------------------------------------------------------------
# Control-layer domain-admissibility reason codes (D_ namespace; disjoint from
# G_ and REF_). The structural D_ codes come from domain_validity.assess().
# ---------------------------------------------------------------------------

D_VERDICT_REQUIRED = "D_VERDICT_REQUIRED"      # requires_verdict, none supplied -> HOLD_FOR_VERDICT
D_VERDICT_UNVERIFIED = "D_VERDICT_UNVERIFIED"  # a verdict was supplied but failed verification (fail-closed)
D_VERDICT_UNSAFE = "D_VERDICT_UNSAFE"          # authentic verdict attests UNSAFE -> HOLD_FOR_HIL
D_VERDICT_CONTRACT = "D_VERDICT_CONTRACT"      # DV-03/DV-04: caller omitted a load-bearing input


def control(
    ctx: Any,
    domain_manifest: Any,
    *,
    verdict: Optional[Dict[str, Any]] = None,
    expected_decision_sha256: Optional[str] = None,
    authority_public_keys: Optional[Dict[str, Any]] = None,
    gate_key_id: Optional[str] = None,
    now: Optional[datetime] = None,
    clock_skew: timedelta = timedelta(0),
) -> Tuple[str, Optional[str], Optional[Dict[str, Any]]]:
    """
    Decide the domain-control outcome for an admissible interaction.

    Returns (outcome, code, detail):
      outcome - one of CONTROL_PASS / _HOLD_FOR_VERDICT / _HOLD_FOR_HIL / _REFUSE
      code    - a D_ code on any non-PASS outcome, else None
      detail  - optional dict locating the reason, else None

    Deterministic and fail-closed. When `requires_verdict` is declared for the
    interaction's domain, `expected_decision_sha256`, `authority_public_keys`,
    and `gate_key_id` MUST be supplied; a missing/invalid verdict input fails
    CLOSED to HOLD_FOR_VERDICT (never PASS).
    """
    # 1. D-structural first: is the CONTENT structurally domain-valid? A missing
    #    required attestation (e.g. a CAT scan assigned but not approved) is a
    #    structural REFUSE - caught here without any out-of-band call.
    dstate, dcode, detail = assess(ctx, domain_manifest)
    if dstate != "VALID":
        return CONTROL_REFUSE, dcode, detail

    # assess() already validated the manifest; re-derive the spec (None-safe).
    dm = safe_domain_manifest(domain_manifest)
    if dm is None:
        return CONTROL_REFUSE, D_MANIFEST_MALFORMED, None

    declared = ctx.get("domain") if isinstance(ctx, dict) else None
    domains = dm.get("domains") or {}
    spec = domains.get(declared) if declared else None

    # 2. Does this domain require a substantive out-of-band verdict?
    if not (spec and spec.get("requires_verdict")):
        return CONTROL_PASS, None, None

    # 3. A verdict is required. CALLER-CONTRACT first (DV-03/DV-04): the
    #    load-bearing verification inputs must be present BEFORE we treat any
    #    verdict as releasing. Omitting gate_key_id would disable the SoD
    #    id-check; omitting expected_decision_sha256 would satisfy action
    #    binding by None == None. Either omission fails closed to a hold, never
    #    to PASS - a misconfigured caller gets oversight, not a bypass.
    if not (isinstance(expected_decision_sha256, str) and expected_decision_sha256
            and isinstance(gate_key_id, str) and gate_key_id):
        return CONTROL_HOLD_FOR_VERDICT, D_VERDICT_CONTRACT, {"domain": declared}

    if verdict is None:
        return CONTROL_HOLD_FOR_VERDICT, D_VERDICT_REQUIRED, {"domain": declared}

    # Only the domain's PINNED authority is accepted (a finance authority cannot
    # sign a healthcare verdict). Restrict the trust map to the pinned key id.
    authority_key_id = spec.get("authority_key_id")
    keys = authority_public_keys or {}
    trusted = (
        {authority_key_id: keys[authority_key_id]}
        if authority_key_id in keys else {}
    )

    v = verify_verdict(
        verdict,
        expected_decision_sha256=expected_decision_sha256,
        expected_domain=declared,
        authority_public_keys=trusted,
        gate_key_id=gate_key_id,
        now=now,
        clock_skew=clock_skew,
    )
    if not v["accepted"]:
        # Forged / stale / rebound / wrong-authority / wrong-domain verdict:
        # fail closed to a hold (acquire a valid one), carrying the REF_ reason.
        return CONTROL_HOLD_FOR_VERDICT, D_VERDICT_UNVERIFIED, {
            "domain": declared, "verify_reason": v["reason"],
        }

    if v["verdict"] == VERDICT_UNSAFE:
        # Authentic UNSAFE -> a human must re-determine out-of-band (not an
        # automatic refuse, not an automatic pass): route to the 202/grant path.
        return CONTROL_HOLD_FOR_HIL, D_VERDICT_UNSAFE, {"domain": declared}

    # Authentic + SAFE.
    return CONTROL_PASS, None, None
