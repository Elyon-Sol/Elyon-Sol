"""
Elyon-Sol Policy Enforcement Point (PEP).

This module is the HTTP boundary of the gate. It performs schema
validation BEFORE evaluation, evaluation BEFORE upstream forwarding,
and fail-closed on any exception. Schema validation order is
load-bearing per SPEC/request_schema.md "PEP boundary behavior."

Wired in VL-019 to close G2 in code. Prior to VL-019, this module
accepted a flat `{target_url, context}` body via a Pydantic model
and performed no schema validation; the wire shape changed to
`{target_url, interaction}` per SPEC/request_schema.md and the
validator from IMPLEMENTATION/request_validator.py (VL-018) is
called before evaluate(). The endpoint reads the raw JSON body
(no Pydantic body model) so that the validator can inspect the
full set of top-level keys; a Pydantic model with fixed fields
would silently drop extra top-level keys (like `AP`, `OP`, or
`ccs_valid` alongside a valid `interaction`), mapping
spec-distinguished refusals (REF_SCHEMA_FLAT_KEYS,
REF_SCHEMA_RESERVED_CCS) onto a generic REF_SCHEMA_TOP_LEVEL.

Refusal payloads at the schema layer use the seven-code vocabulary
named in SPEC/request_schema.md "PEP boundary behavior" and exported
from IMPLEMENTATION/request_validator.py:
  REF_SCHEMA_PARSE_ERROR              (emitted here by the
                                       JSON-decode catch)
  REF_SCHEMA_TOP_LEVEL                (emitted by the validator)
  REF_SCHEMA_BAD_URL                  (emitted by the validator)
  REF_SCHEMA_FLAT_KEYS                (emitted by the validator)
  REF_SCHEMA_MANIFEST_PINNING_MISSING (emitted by the validator)
  REF_SCHEMA_RESERVED_CCS             (emitted by the validator)
  REF_SCHEMA_TYPE_MISMATCH            (emitted by the validator)

REF_SCHEMA_TOP_LEVEL is emitted directly by the validator (see
request_validator.py lines 308 and 337-342); the PEP does not
import it because it does not emit it. The PARSE_ERROR import is
the only schema-vocabulary constant used at this boundary.

Extended in VL-029 to emit admissibility envelopes on ELIGIBLE per
docs/restructure/05_admissibility_envelope_spec.md build-order step 5.
On ELIGIBLE, the PEP calls safe_manifest + the three condition
functions (ac3_valid, t26_valid, manifest_integrity_valid) per
Decision C1, then calls build_envelope() to construct the envelope,
then attaches the envelope to the response payload per Decision E
({"decision": "ELIGIBLE", "envelope": <envelope>}). REFUSE response
shape is unchanged from VL-019; envelope-on-REFUSE is build-outward
scope per artifact 05 open question 3 (G4 territory).

VL-047 mandatory signing cutover: the ELIGIBLE branch now SIGNS the
envelope (sign_envelope) before pushing and returning it, using a signing
key from a runtime source (_get_signing_key; an env var or an injected key
object, never the repo). A gate with no configured key FAILS CLOSED
(REF_PEP_FAIL_CLOSED via the envelope-construction try/except), never a
downgrade to an unsigned forward. verify_envelope's unsigned mode is
unaffected (it remains for target-side enforcement and A1-bypass
demonstrations). DEFAULT_SECURE goes green (EVIDENCE/readiness.json).

VL-099 issuance log: when configured (pep._INJECTED_ISSUANCE_LOG or
ELYON_ISSUANCE_LOG_PATH), the ELIGIBLE branch appends each SIGNED
envelope to a JSONL issuance log (IMPLEMENTATION/issuance_log.py) after
sign_envelope and before the upstream push, inside the fail-closed
catch: a configured gate that cannot record an issuance refuses
(REF_PEP_FAIL_CLOSED) and never calls the target. Default None is
byte-behavior-identical to pre-VL-099. The log is the gate-produced
input to `envelope_inspector reconcile --issued` (spec 28).
"""

import json
import os
import threading
import uuid
from datetime import datetime, timezone, timedelta

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from IMPLEMENTATION.evaluator import (
    load_manifest,
    evaluate,
    decide,
    safe_manifest,
    resolve_required_sets,
    ac3_valid,
    t26_valid,
    manifest_integrity_valid,
)
from IMPLEMENTATION.envelope import build_envelope, canonical_json, sign_envelope
from IMPLEMENTATION.issuance_log import issuance_log_from_env, approval_log_from_env
from IMPLEMENTATION.impact import requires_approval
from IMPLEMENTATION.approval import (
    verify_grant,
    REF_APPROVAL_REPLAY,
    REF_APPROVAL_REQUEST_UNKNOWN,
)
from IMPLEMENTATION.replay_cache import InMemoryReplayCache, replay_cache_from_env
from IMPLEMENTATION.domain_validity import (
    resolve_domain_manifest, DM_STATUS_MALFORMED,
)
from IMPLEMENTATION.domain_control import (
    control as domain_control,
    CONTROL_PASS, CONTROL_HOLD_FOR_VERDICT, CONTROL_HOLD_FOR_HIL, CONTROL_REFUSE,
    D_OVERRIDE_MISMATCH,
)
from IMPLEMENTATION.domain_verdict import claim_verdict_once
from IMPLEMENTATION.domain_authority import (
    resolve_domain_authority_keys, PROVENANCE_SIGNED_KEY_RECORD,
)
from IMPLEMENTATION.pending_store import (
    pending_store_from_env,
    InMemoryPendingApprovals,
)
from IMPLEMENTATION.request_validator import (
    validate_request,
    REF_SCHEMA_PARSE_ERROR,
)
from IMPLEMENTATION.transport import post_to_target

# --- SSRF guard (L1 fix): the gate must not be coerced into POSTing a signed
# envelope to internal/loopback/link-local/metadata space. ---
import ipaddress as _ipaddress
import socket as _socket
from urllib.parse import urlparse as _urlparse
from fastapi.concurrency import run_in_threadpool

REF_PEP_TARGET_URL_BLOCKED = "REF_PEP_TARGET_URL_BLOCKED"


def _target_url_allowed(url):
    """SSRF guard: reject non-http(s) schemes and hosts resolving to loopback,
    link-local (incl. metadata 169.254.169.254), private, reserved, multicast or
    unspecified space. ELYON_TARGET_URL_ALLOWLIST -> strict allowlist;
    ELYON_ALLOW_PRIVATE_TARGETS=1 -> dev/test opt-out. Fail-closed on error."""
    try:
        p = _urlparse(url)
    except Exception:
        return False
    if p.scheme not in ("http", "https"):
        return True  # not an http(s) forward -> not an SSRF-to-internal vector
    host = p.hostname
    if not host:
        return False
    allow = os.environ.get("ELYON_TARGET_URL_ALLOWLIST")
    if allow:
        return host.lower() in {h.strip().lower() for h in allow.split(",") if h.strip()}
    if os.environ.get("ELYON_ALLOW_PRIVATE_TARGETS", "").strip().lower() in ("1", "true", "yes"):
        return True
    try:
        addrs = [str(_ipaddress.ip_address(host))]
    except ValueError:
        try:
            port = p.port or (443 if p.scheme == "https" else 80)
            addrs = [i[4][0] for i in _socket.getaddrinfo(host, port, proto=_socket.IPPROTO_TCP)]
        except Exception:
            return False
    for a in addrs:
        try:
            ip = _ipaddress.ip_address(a)
        except ValueError:
            return False
        if (ip.is_loopback or ip.is_link_local or ip.is_private
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return False
    return True


# ===========================================================================
# Governance Feature 1 (human oversight) - gate-side state + helpers (VL-115).
# requires_approval/verify_grant are the pure halves (VL-113/VL-114); this is
# the STATEFUL wiring half. Build-then-wire ended here: the approval branch is
# on the default path, but with the default manifest (HIGH_IMPACT: []) it is a
# no-op, so the default forward stays byte-behavior-identical.
# ===========================================================================

# Approver public-key trust map (key_id -> public_key with .verify). The approver
# PRIVATE key is NEVER resolvable by the gate ([FIX H5] custody): the gate holds
# only public keys here.
#
# Provenance (GL-01-refine, VL-124). _get_approver_keys_with_provenance resolves,
# in order, and labels WHERE the map came from so the startup guard can require
# the load-bearing source under a high-impact manifest:
#   1. _INJECTED_APPROVER_KEYS seam            -> APPROVER_PROV_INJECTED
#      (tests/harness only; gate-controllable, so it does NOT satisfy G-01)
#   2. the pinned-root signed key-record trio  -> APPROVER_PROV_SIGNED_CHAIN
#      (the load-bearing path: pep resolves the map ITSELF from the signed chain
#      with an explicit `approver` role - what a gate cannot forge; the analog,
#      for the approver key, of SES-9a/K-01 for the issuer key)
#   3. the bare ELYON_APPROVER_* static pin    -> APPROVER_PROV_STATIC_PIN
#      (no provenance, no role; retained for back-compat, does NOT satisfy G-01)
#   4. nothing configured                      -> APPROVER_PROV_NONE ({} map)
_INJECTED_APPROVER_KEYS = None  # set to {key_id: public_key} by a harness/deploy

# The in-process signed-chain approver trio (mirrors the deploy-shim contract, now
# read natively by pep so provenance is intrinsic rather than shim-supplied).
ENV_APPROVER_KEY_RECORD_PATH = "ELYON_APPROVER_KEY_RECORD_PATH"
ENV_PINNED_ROOT_KEY_ID = "ELYON_PINNED_ROOT_KEY_ID"
ENV_PINNED_ROOT_PUBKEY_B64 = "ELYON_PINNED_ROOT_PUBKEY_B64"


def _resolve_signed_chain_approver_keys():
    """Resolve the role-distinct approver map from the pinned-root SIGNED key
    record, in-process. Returns (map, present): `present` is True iff the signed-
    chain trio is configured (so the caller can label provenance SIGNED_CHAIN even
    when the resolved map is empty - an empty map from a real record is a fail-
    closed G-06 case, distinct from 'no signed-chain configured'). Fail-closed:
    any missing/invalid/wrong-root/no-approver-role input yields ({}, present)
    rather than raising into startup."""
    import base64
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from IMPLEMENTATION.key_record_source import load_key_record_from_bytes
    from IMPLEMENTATION.approver_trust import resolve_approver_keys

    record_path = os.environ.get(ENV_APPROVER_KEY_RECORD_PATH)
    root_id = os.environ.get(ENV_PINNED_ROOT_KEY_ID)
    root_b64 = os.environ.get(ENV_PINNED_ROOT_PUBKEY_B64)
    if not record_path or not root_id or not root_b64:
        return {}, False  # trio not configured -> not the signed-chain path

    try:
        pinned = {root_id: Ed25519PublicKey.from_public_bytes(
            base64.b64decode(root_b64, validate=True))}
        with open(record_path, "rb") as fh:
            record_bytes = fh.read()
    except (OSError, ValueError, TypeError):
        return {}, True  # configured but unreadable/malformed pin -> fail closed

    skew_s = os.environ.get("ELYON_CLOCK_SKEW_SECONDS")
    skew = timedelta(seconds=int(skew_s)) if skew_s else timedelta(0)
    gate_key_id = os.environ.get("ELYON_SIGNING_KEY_ID")
    try:
        loaded = load_key_record_from_bytes(record_bytes, pinned, clock_skew=skew)
    except Exception:
        return {}, True  # any validation failure -> fail closed (still signed-chain)
    view = loaded.get("trust_view")
    if view is None:
        return {}, True
    return resolve_approver_keys(view, gate_key_id=gate_key_id, clock_skew=skew), True


def _get_approver_keys_with_provenance():
    """Return (approver_map, provenance) where provenance is one of the
    governance_wiring.APPROVER_PROV_* tokens. See the resolution order above."""
    from IMPLEMENTATION.governance_wiring import (
        APPROVER_PROV_SIGNED_CHAIN, APPROVER_PROV_INJECTED,
        APPROVER_PROV_STATIC_PIN, APPROVER_PROV_NONE,
    )
    if _INJECTED_APPROVER_KEYS is not None:
        return _INJECTED_APPROVER_KEYS, APPROVER_PROV_INJECTED

    signed_map, signed_present = _resolve_signed_chain_approver_keys()
    if signed_present:
        return signed_map, APPROVER_PROV_SIGNED_CHAIN

    key_id = os.environ.get("ELYON_APPROVER_KEY_ID")
    pub_hex = os.environ.get("ELYON_APPROVER_PUBKEY_HEX")
    if key_id and pub_hex:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey,
        )
        return ({key_id: Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))},
                APPROVER_PROV_STATIC_PIN)
    return {}, APPROVER_PROV_NONE  # no approver -> every grant KEY_UNKNOWN (fail closed)


def _get_approver_keys():
    """The {key_id: public_key} map verify_grant trusts. Provenance-agnostic view
    for the request path; the startup guard uses the provenance-aware resolver."""
    return _get_approver_keys_with_provenance()[0]


# The gate-side pending-request set ([FIX H4]) and the grant single-use cache
# ([FIX H3]) now come from their sibling-module *_from_env builders (R2, VL-120).
# Default (no ELYON_* env): InMemoryPendingApprovals + InMemoryReplayCache - the
# per-process behavior pep had before R2, byte-behavior-identical. A gate that
# declares itself horizontally scaled (ELYON_REPLAY_MULTI_INSTANCE) without a
# shared store fails closed at startup (the R-02 declare-or-fail guard), instead
# of handing each replica a per-process set/cache that consumes the same
# approval_request_id / grant_id once EACH.
#
# _PendingApprovals is retained as a backward-compatible alias of the now-shared
# InMemoryPendingApprovals (callers/tests that construct a fresh in-process set).
_PendingApprovals = InMemoryPendingApprovals

_PENDING = pending_store_from_env()
_GRANT_REPLAY = replay_cache_from_env()


# ---------------------------------------------------------------------------
# Domain-validity gate (D) - OPT-IN wiring. See
# docs/design/domain_validity_D_architecture.md.
#
# Enabled ONLY when ELYON_DOMAIN_MANIFEST names a path. Unset -> _DOMAIN_ENABLED
# is False and every code path below is skipped, so the default deployment is
# byte-behavior-identical to the pre-D gate. This is PEP-layer enforcement, NOT a
# canon change: evaluator.decide() and G(I) are untouched, evaluator_sha256 does
# not move, and D is not (yet) an admissibility conjunct. The canon increment
# that makes D an invariant is a separate, author-ratified event (GR-1).
#
# The determinism firewall holds: the domain VERDICT is read off the REQUEST (a
# header, exactly like the approval grant) and passed INTO domain_control. The
# gate never calls a policy agent inline, so the decision path stays deterministic
# and non-blocking; obtaining the verdict is the caller's / monitor's job.
# ---------------------------------------------------------------------------

_DOMAIN_MANIFEST_PATH = os.environ.get("ELYON_DOMAIN_MANIFEST")
_DOMAIN_ENABLED = bool(_DOMAIN_MANIFEST_PATH)
_VERDICT_REPLAY = replay_cache_from_env()


def _extract_domain_verdict(request):
    """Read a domain-compliance verdict off the request, or None if absent
    (-> HOLD_FOR_VERDICT when the domain requires one). A present-but-unparseable
    verdict returns the raw string so verify_verdict maps it to
    REF_VERDICT_MALFORMED - junk is a refusal, not a free pass."""
    raw = request.headers.get("X-Elyon-Sol-Domain-Verdict")
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw


def _domain_authority_keys():
    """Trust map for domain-verdict signers, resolved from the pinned-root SIGNED
    key record in-process - the same chain and the same discipline
    _resolve_signed_chain_approver_keys() uses for approvers, but selecting the
    `domain_authority` role instead of `approver`.

    Fail-closed at every step: trio not configured, unreadable pin, validation
    failure, or no domain_authority role published -> {} -> no verdict can verify
    -> HOLD, never PASS. Role-distinctness (one signed role per key) is what keeps
    a policy authority from being an issuer or an approver."""
    import base64
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from IMPLEMENTATION.key_record_source import load_key_record_from_bytes

    record_path = os.environ.get(ENV_APPROVER_KEY_RECORD_PATH)
    root_id = os.environ.get(ENV_PINNED_ROOT_KEY_ID)
    root_b64 = os.environ.get(ENV_PINNED_ROOT_PUBKEY_B64)
    if not record_path or not root_id or not root_b64:
        return {}

    try:
        pinned = {root_id: Ed25519PublicKey.from_public_bytes(
            base64.b64decode(root_b64, validate=True))}
        with open(record_path, "rb") as fh:
            record_bytes = fh.read()
    except (OSError, ValueError, TypeError):
        return {}

    skew_s = os.environ.get("ELYON_CLOCK_SKEW_SECONDS")
    skew = timedelta(seconds=int(skew_s)) if skew_s else timedelta(0)
    try:
        loaded = load_key_record_from_bytes(record_bytes, pinned, clock_skew=skew)
    except Exception:
        return {}
    view = loaded.get("trust_view")
    if view is None:
        return {}
    return resolve_domain_authority_keys(
        view,
        provenance=PROVENANCE_SIGNED_KEY_RECORD,
        gate_key_id=os.environ.get("ELYON_SIGNING_KEY_ID"),
        clock_skew=skew,
    )


def _extract_grant(request):
    """Read an approval grant off the request, or None if absent (-> 202 hold).
    A present-but-unparseable grant returns the raw string so verify_grant maps
    it to REF_APPROVAL_MALFORMED (a junk grant is a refusal, not a hold)."""
    raw = request.headers.get("X-Elyon-Sol-Approval-Grant")
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw  # non-dict -> verify_grant -> REF_APPROVAL_MALFORMED


def _grant_not_after(grant):
    na = grant.get("not_after") if isinstance(grant, dict) else None
    if isinstance(na, str):
        try:
            return datetime.fromisoformat(na)
        except ValueError:
            return None
    return None


app = FastAPI(title="Elyon-Sol PEP")


@app.on_event("startup")
def _assert_governance_wiring_on_startup():
    """Fail closed at startup if the SHA-pinned manifest declares HIGH_IMPACT
    actions but the gate is not wired to honor oversight (review findings
    G-01/G-03/G-04/G-06). NO-OP for the default HIGH_IMPACT:[] manifest, so the
    non-high-impact deployment is byte-behavior-unchanged. Build-then-wire: the
    check lives in IMPLEMENTATION/governance_wiring.py (pure, tested directly);
    this hook only gathers live gate state and calls it."""
    from IMPLEMENTATION.governance_wiring import assert_high_impact_wiring

    approver_keys, approver_provenance = _get_approver_keys_with_provenance()
    assert_high_impact_wiring(
        manifest=load_manifest(),
        approver_keys=approver_keys,
        approver_provenance=approver_provenance,
        approval_log_configured=_get_approval_log() is not None,
        pending_redis_url=os.environ.get("ELYON_PENDING_REDIS_URL"),
        replay_redis_url=os.environ.get("ELYON_REPLAY_REDIS_URL"),
    )


# VL-065 decision freshness (A3b close): the default ELIGIBLE forward stamps a
# signed not_after (decision max-age) so a captured, validly-signed decision is
# NOT honored arbitrarily later. Verification-layer policy enforced by
# verify_envelope step 1.5b (the proven key-expiry primitive applied to the
# decision); no new canon invariant, no reassert() change. not_after is inside
# the signature (tamper-proof) and excluded from decision_sha256, so the wire
# decision hash is unchanged. Configurable out-of-band; defaults to 300s.
DECISION_MAX_AGE_SECONDS = int(os.environ.get("ELYON_DECISION_MAX_AGE_SECONDS", "300"))


# VL-047 mandatory signing cutover: the gate's default forward signs every
# emitted envelope, so the gate now needs a signing PRIVATE key at runtime.
# Custody (artifact 09 / artifact 05 "Key model"): the private key is NEVER in
# the repository. _get_signing_key() resolves, in order, a process-injected key
# object (a test harness or a deployment shim) then the ELYON_SIGNING_KEY_HEX +
# ELYON_SIGNING_KEY_ID environment pair. It returns (signing_key, key_id) or
# None; None makes the ELIGIBLE branch fail closed (REF_PEP_FAIL_CLOSED), never
# a downgrade to an unsigned forward. cryptography is imported lazily inside the
# function so this module stays import-clean (matching envelope/verifier
# duck-typing); the injected object need only expose .sign(bytes) -> bytes.
_INJECTED_SIGNING_KEY = None  # set to (signing_key, key_id) by a harness/deploy


def _get_signing_key():
    if _INJECTED_SIGNING_KEY is not None:
        return _INJECTED_SIGNING_KEY
    key_hex = os.environ.get("ELYON_SIGNING_KEY_HEX")
    key_id = os.environ.get("ELYON_SIGNING_KEY_ID")
    if key_hex and key_id:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )
        return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(key_hex)), key_id
    return None


# VL-099 issuance log: injected-then-env resolution, mirroring
# _get_signing_key(). None (the default) disables logging entirely.
_INJECTED_ISSUANCE_LOG = None  # set by a harness/deploy shim


def _get_issuance_log():
    if _INJECTED_ISSUANCE_LOG is not None:
        return _INJECTED_ISSUANCE_LOG
    return issuance_log_from_env()


# VL-116 ([FIX H8]): the approval log records the held-request + grant-consumption
# governance trail. Injected-then-env, default None (no records; byte-behavior
# identical to pre-VL-116). reconcile_approvals consumes it.
_INJECTED_APPROVAL_LOG = None  # set by a harness/deploy shim


def _get_approval_log():
    if _INJECTED_APPROVAL_LOG is not None:
        return _INJECTED_APPROVAL_LOG
    return approval_log_from_env()


def _schema_refusal_exception(code: str) -> HTTPException:
    """
    Build the standard schema-layer refusal HTTPException. Status
    403 with detail payload {"terminal_state": "REFUSE",
    "refusal_reason_code": <code>} per the assertions in
    TESTS/adversarial/test_request_schema.py.
    """
    return HTTPException(
        status_code=403,
        detail={
            "terminal_state": "REFUSE",
            "refusal_reason_code": code,
        },
    )


@app.post("/governed-call")
async def governed_call(request: Request):
    """
    Boundary behavior order per SPEC/request_schema.md
    "PEP boundary behavior":

      1. Parse JSON. Failure -> REFUSE with REF_SCHEMA_PARSE_ERROR.
      2-5. Schema validation via validate_request(). Failure ->
         REFUSE with the validator-emitted code (REF_SCHEMA_TOP_LEVEL,
         REF_SCHEMA_BAD_URL, REF_SCHEMA_FLAT_KEYS,
         REF_SCHEMA_MANIFEST_PINNING_MISSING, REF_SCHEMA_RESERVED_CCS,
         or REF_SCHEMA_TYPE_MISMATCH).
      6. evaluate() on the validator's normalized interaction. REFUSE
         -> HTTPException(403, terminal_state=REFUSE). ELIGIBLE ->
         construct envelope (Decision C1: ac3/t26/manifest_integrity
         derived via the three condition functions on safe_manifest;
         build_envelope() per artifact 05 build-order step 5), sign it
         (VL-047 cutover; fail-closed if no key is configured), then
         forward to target_url, then return
         {"decision": "ELIGIBLE", "envelope": <envelope>} per
         Decision E.

    The endpoint reads the request body as raw bytes rather than
    binding to a Pydantic model because the validator owns
    full-body inspection: the spec's flat-key check
    (REF_SCHEMA_FLAT_KEYS) and the spec's top-level CCS check
    (REF_SCHEMA_RESERVED_CCS for keys like `ccs_valid` alongside
    a valid `interaction`) both require visibility of the original
    top-level keys. Pydantic projection to a fixed model
    (`{target_url, interaction}`) would silently drop the very keys
    the validator must refuse, mapping spec-distinguished refusals
    onto a single REF_SCHEMA_TOP_LEVEL diagnosis. Pydantic's role
    here would be redundant with the validator's own type checks;
    omitting it preserves the seven-code vocabulary discrimination
    the test suite requires.

    Schema-layer refusals do not call evaluate() and do not call
    requests.post; the function returns through HTTPException
    before reaching either. Evaluator-layer refusals do not call
    requests.post.

    The fail-closed exception catch wraps evaluate() and the
    upstream call only. Schema-layer parse and validation errors
    raise HTTPException directly; they do not flow through the
    catch.
    """
    # ----- Step 1: Parse JSON -----
    raw = await request.body()
    try:
        body = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        raise _schema_refusal_exception(REF_SCHEMA_PARSE_ERROR)

    # ----- Steps 2-5: Schema validation -----
    normalized_interaction, refusal = validate_request(body)
    if refusal is not None:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": refusal,
            },
        )

    # ----- SSRF guard (L1 fix): block a caller-supplied target_url pointing at
    # internal/loopback/link-local/metadata space BEFORE minting or forwarding. -----
    if not await run_in_threadpool(_target_url_allowed, body["target_url"]):
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": REF_PEP_TARGET_URL_BLOCKED,
            },
        )

    # ----- Evaluation -----
    try:
        manifest = load_manifest()
        result, reason = decide(normalized_interaction, manifest)
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                "error": str(e),
            },
        )

    if result != "ELIGIBLE":
        # Evaluator-layer REFUSE. The refusal now carries the evaluator's own
        # G_ reason code (evaluator.decide/refusal_reason) naming WHICH condition
        # failed - closing the gap this branch previously documented (it withheld
        # any code because the evaluator-layer refusal vocabulary was unspecified).
        # The G_ set is disjoint from the boundary REF_* vocabulary; additive -
        # prior callers saw {"terminal_state": "REFUSE"} with no code.
        raise HTTPException(
            status_code=403,
            detail={"terminal_state": "REFUSE", "refusal_reason_code": reason},
        )

    # ----- Envelope construction (unsigned) - VL-029 build half; SPLIT from
    # signing at VL-115 so the approval gate can read decision_sha256 BEFORE any
    # sign/issuance/forward side effect. Fail-closed (W2): any exception here ->
    # REF_PEP_FAIL_CLOSED. -----
    try:
        safe_mfst = safe_manifest(manifest)
        # Typed-impact (step 8.2): stamp ac3/t26 against the caller's declared
        # interaction type's required sets, consistent with evaluate(). Flat
        # manifest -> resolve returns the top-level sets (byte-identical).
        req_ar, req_r = resolve_required_sets(safe_mfst, normalized_interaction)
        ac3 = ac3_valid(normalized_interaction, req_ar)
        t26 = t26_valid(normalized_interaction, req_r)
        mi = manifest_integrity_valid(normalized_interaction, safe_mfst)
        envelope = build_envelope(
            decision="ELIGIBLE",
            target_url=body["target_url"],
            normalized_interaction=normalized_interaction,
            manifest=safe_mfst,
            ac3=ac3,
            t26=t26,
            manifest_integrity=mi,
        )
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                "error": str(e),
            },
        )

    # ----- Domain-validity gate (D) - OPT-IN, default-off -----
    # Runs AFTER the ELIGIBLE envelope exists (so decision_sha256 is available to
    # bind a verdict to) and BEFORE the approval gate, as EXPLICIT early
    # returns/raises so no outcome can be swallowed by a fail-closed except. A
    # domain REFUSE must not consume a 202 approval slot, and a domain HOLD must
    # not reach post_to_target. When ELYON_DOMAIN_MANIFEST is unset this whole
    # block is skipped and the path is byte-behavior-unchanged.
    _domain_hil = False
    _domain_hil_code = None
    _domain_hil_verdict_id = None
    _pre_grant = None
    _override_vid = None
    if _DOMAIN_ENABLED:
        try:
            dmanifest, dstatus, dm_sha = resolve_domain_manifest(_DOMAIN_MANIFEST_PATH)
            if dstatus == DM_STATUS_MALFORMED:
                # Deployed-but-broken ruleset: fail closed. Never degrade a
                # config error into "no domain policy" (S5b).
                raise HTTPException(
                    status_code=403,
                    detail={"terminal_state": "REFUSE",
                            "refusal_reason_code": "D_MANIFEST_MALFORMED"},
                )
            dverdict = _extract_domain_verdict(request)
            # A DOMAIN-OVERRIDE grant names, inside its signed region, the
            # UNSAFE verdict it overrules. Read that id here and hand it to
            # domain_control, which waives the freshness window for that one
            # verdict. The grant is NOT trusted at this point - it is verified
            # in the approval block below - but reading the id early cannot
            # weaken anything: an unverified grant only ever waives the
            # freshness of a verdict that must still pass signature, pinned
            # authority, decision binding and domain binding, and the release
            # itself still requires that grant to verify.
            _pre_grant = _extract_grant(request)
            _override_vid = (
                _pre_grant.get("overrides_verdict_id")
                if isinstance(_pre_grant, dict) else None
            )
            d_out, d_code, d_detail = domain_control(
                normalized_interaction,
                dmanifest,
                domain_manifest_sha256=dm_sha,
                verdict=dverdict,
                expected_decision_sha256=envelope["decision_sha256"],
                authority_public_keys=_domain_authority_keys(),
                gate_key_id=(_get_signing_key() or (None, None))[1],
                override_verdict_id=_override_vid,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=403,
                detail={"terminal_state": "REFUSE",
                        "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                        "error": str(e)},
            )

        if d_out == CONTROL_REFUSE:
            raise HTTPException(
                status_code=403,
                detail={"terminal_state": "REFUSE", "refusal_reason_code": d_code},
            )

        if d_out == CONTROL_HOLD_FOR_VERDICT:
            # 202 HOLD for a signed POLICY-AUTHORITY attestation. This is NOT a
            # human-approval hold: it does not open an approval slot, because the
            # thing missing is a machine-verifiable verdict, not a human decision.
            # Do NOT sign, issuance-log a forward, or post_to_target.
            return JSONResponse(
                status_code=202,
                content={
                    "terminal_state": "PENDING_DOMAIN_VERDICT",
                    "refusal_reason_code": d_code,
                    "decision_sha256": envelope["decision_sha256"],
                    "domain": (d_detail or {}).get("domain"),
                },
            )

        if d_out == CONTROL_HOLD_FOR_HIL:
            # An AUTHENTIC verdict attests UNSAFE: a HUMAN must re-determine
            # out-of-band. Rather than dead-ending in a bare 202 (which reported
            # the need but opened no slot a grant could fill, leaving the
            # interaction stuck), route it into the EXISTING approval machinery by
            # requiring approval for this call. The approval block below then
            # issues the approval_request_id, records the hold, and - when the
            # human presents a grant - verifies provenance/binding/SoD/freshness,
            # consumes the 202 slot and claims grant_id single-use before forward.
            # One release path, not two.
            _domain_hil = True
            _domain_hil_code = d_code
            _domain_hil_verdict_id = (d_detail or {}).get("verdict_id")
            # ANTI-LAUNDERING. A domain hold may be released ONLY by a grant that
            # explicitly overrides THIS verdict. A plain approval grant - e.g. one
            # a human signed for a HIGH_IMPACT hold - carries no
            # overrides_verdict_id and therefore cannot discharge a safety
            # finding it never referred to. Mismatch or absence is refused here
            # rather than falling through to the approval block, so the two hold
            # types can never substitute for one another.
            if isinstance(_pre_grant, dict) and _pre_grant.get("approval_request_id"):
                if _override_vid != _domain_hil_verdict_id:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "terminal_state": "REFUSE",
                            "refusal_reason_code": D_OVERRIDE_MISMATCH,
                        },
                    )

        if d_out == CONTROL_PASS and isinstance(dverdict, dict):
            # A verdict that RELEASED this call is single-use: claim verdict_id
            # exactly once, BEFORE any forward, so a captured SAFE verdict cannot
            # release the same decision twice within its freshness window.
            claimed = claim_verdict_once(dverdict, _VERDICT_REPLAY)
            if not claimed["accepted"]:
                raise HTTPException(
                    status_code=403,
                    detail={"terminal_state": "REFUSE",
                            "refusal_reason_code": claimed["reason"]},
                )

    # ----- Approval gate (governance Feature 1; design 1.3; [FIX H6]) -----
    # Placed AFTER the ELIGIBLE+envelope build and BEFORE the sign/forward
    # try-blocks, as EXPLICIT early returns/raises, so (a) a 202 hold can never
    # be swallowed by a fail-closed except and converted to a 403, and (b) no
    # high-impact call without a valid grant can reach post_to_target. The 202
    # leg and the approved leg are mutually exclusive; the approved leg falls
    # through to the single existing sign+forward (no second forward).
    # requires_approval is manifest-derived and fail-closed; for the default
    # manifest (HIGH_IMPACT: []) it is False and this whole block is a no-op
    # (the default forward path is byte-behavior-unchanged).
    try:
        needs_approval = requires_approval(normalized_interaction, manifest)
    except Exception:
        needs_approval = True  # fail closed
    # A domain re-determination hold is a HUMAN-approval hold: same machinery,
    # same SoD, same single-use, same audit - only the REASON differs.
    if _domain_hil:
        needs_approval = True
    if needs_approval:
        decision_sha256 = envelope["decision_sha256"]
        grant = _extract_grant(request)
        if grant is None:
            # 202 HOLD: do NOT sign, do NOT issuance-log a forward, do NOT
            # post_to_target. Issue an approval_request_id bound to this
            # decision and record it pending ([FIX H4]).
            approval_request_id = uuid.uuid4().hex
            _PENDING.issue(approval_request_id, decision_sha256)
            # [FIX H8] record the hold so reconcile_approvals can later prove a
            # forwarded high-impact decision had a recorded grant. Fail closed on
            # a CONFIGURED log (do not acknowledge a hold you cannot record).
            approval_log = _get_approval_log()
            if approval_log is not None:
                try:
                    hold_record = {
                        "type": "approval_request",
                        "decision_sha256": decision_sha256,
                        "approval_request_id": approval_request_id,
                        # WHY this is held. reconcile_approvals keys only on
                        # type/decision_sha256/approval_request_id, so this is
                        # additive - but an operator surface must be able to tell
                        # "a human must re-determine a domain-compliance failure"
                        # from "this interaction type is HIGH_IMPACT".
                        "hold_reason": (_domain_hil_code if _domain_hil
                                        else "HIGH_IMPACT"),
                        **({"overridden_verdict_id": _domain_hil_verdict_id}
                           if _domain_hil and _domain_hil_verdict_id else {}),
                        # PUBLIC decision context (already in the envelope) so an
                        # operator surface can show a human what is being held -
                        # additive keys; reconcile_approvals keys only on
                        # type/decision_sha256/approval_request_id.
                        "requested_at": datetime.now(timezone.utc).isoformat(),
                    }
                    for _ctx_key in ("target_url", "not_after"):
                        if envelope.get(_ctx_key):
                            hold_record[_ctx_key] = envelope[_ctx_key]
                    approval_log.append(hold_record)
                except Exception as e:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "terminal_state": "REFUSE",
                            "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                            "error": str(e),
                        },
                    )
            return JSONResponse(
                status_code=202,
                content={
                    "terminal_state": "PENDING_APPROVAL",
                    "approval_request_id": approval_request_id,
                    "decision_sha256": decision_sha256,
                    # Additive: names WHY a human is being asked. Absent-safe for
                    # existing clients, which only read the three fields above.
                    "hold_reason": (_domain_hil_code if _domain_hil
                                    else "HIGH_IMPACT"),
                },
            )
        # A grant is present: verify provenance/binding/SoD/freshness (pure),
        # then consume the 202 slot and claim the grant_id, both BEFORE forward.
        signing_meta = _get_signing_key()
        gate_key_id = signing_meta[1] if signing_meta else None
        grant_req_id = grant.get("approval_request_id") if isinstance(grant, dict) else None
        verdict = verify_grant(
            grant,
            expected_decision_sha256=decision_sha256,
            expected_approval_request_id=grant_req_id,
            approver_public_keys=_get_approver_keys(),
            gate_key_id=gate_key_id,
        )
        if not verdict["accepted"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "terminal_state": "REFUSE",
                    "refusal_reason_code": verdict["reason"],
                },
            )
        # [FIX H4] request identity + single 202->approval: the request_id must
        # be one the gate issued, unconsumed, and bound to THIS decision.
        if not _PENDING.check_and_consume(grant_req_id, decision_sha256):
            raise HTTPException(
                status_code=403,
                detail={
                    "terminal_state": "REFUSE",
                    "refusal_reason_code": REF_APPROVAL_REQUEST_UNKNOWN,
                },
            )
        # [FIX H3] single-use: claim grant_id exactly once, atomically, BEFORE
        # the forward. A replayed grant -> REFUSE (never a second execution).
        if not _GRANT_REPLAY.check_and_claim(grant["grant_id"], _grant_not_after(grant)):
            raise HTTPException(
                status_code=403,
                detail={
                    "terminal_state": "REFUSE",
                    "refusal_reason_code": REF_APPROVAL_REPLAY,
                },
            )
        # [FIX H8] record the grant consumption AFTER the claim and BEFORE the
        # forward: the auditable proof a human grant released this exact
        # decision. Fail closed on a CONFIGURED log - do not forward what you
        # cannot record (canon section 9).
        approval_log = _get_approval_log()
        if approval_log is not None:
            try:
                approval_log.append({
                    "type": "grant_consumed",
                    "decision_sha256": decision_sha256,
                    "approval_request_id": grant_req_id,
                    "grant_id": grant["grant_id"],
                    "approver_key_id": grant.get("approver_key_id"),
                    "hold_reason": (_domain_hil_code if _domain_hil else "HIGH_IMPACT"),
                    **({"overridden_verdict_id": grant.get("overrides_verdict_id")}
                       if grant.get("overrides_verdict_id") else {}),
                })
            except Exception as e:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "terminal_state": "REFUSE",
                        "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                        "error": str(e),
                    },
                )
        # approved -> fall through to the existing sign + issuance-log + forward.

    # ----- Sign + issuance-log (VL-047 + VL-099; SPLIT from build at VL-115) -----
    # Fail-closed (W2): no signing key, a signing error, or an issuance-log
    # append failure on a CONFIGURED log -> REF_PEP_FAIL_CLOSED, never a
    # downgrade to an unsigned forward and never an unrecorded issuance.
    try:
        signing = _get_signing_key()
        if signing is None:
            raise RuntimeError(
                "no signing key configured; gate fails closed rather than "
                "forward unsigned (VL-047 mandatory signing cutover)"
            )
        signing_key, key_id = signing
        not_after = datetime.now(timezone.utc) + timedelta(
            seconds=DECISION_MAX_AGE_SECONDS
        )
        envelope = sign_envelope(
            envelope, signing_key, key_id,
            not_after=not_after, decision_id=uuid.uuid4().hex,
        )
        issuance_log = _get_issuance_log()
        if issuance_log is not None:
            issuance_log.append(envelope)
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                "error": str(e),
            },
        )

    # ----- Upstream forwarding (ELIGIBLE) -----
    # VL-038 push delivery (artifact 08 section 4.3 push variant). The
    # envelope rides as an out-of-band attestation header so the
    # forwarded body stays byte-identical to a direct (un-routed) call;
    # an enforcing target keys on the header's presence and validity
    # (verify_envelope + published-record check), not on the body. Body
    # is unchanged (normalized_interaction). canonical_json gives an
    # ASCII (ensure_ascii=True) string, so the header value is
    # transport-safe. Push deepens the pre-existing canon section 14
    # tension (the gate does more on the execution hop); caller-carry is
    # the section-14-faithful later architecture (artifact 08 sections
    # 4.3 / 5; recorded in artifact 04 G4 + artifact 06 section 14).
    try:
        upstream = post_to_target(
            body["target_url"],
            normalized_interaction,
            {"X-Elyon-Sol-Envelope": canonical_json(envelope)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                "error": str(e),
            },
        )

    return {
        "decision": "ELIGIBLE",
        "envelope": envelope,
    }

# ---------------------------------------------------------------------------
# Read-only observability endpoints (DEFAULT OFF). A generic operator surface:
# they expose ONLY public decision context already durably recorded in the
# governance logs - no secrets, no key material, no mutation, and they are
# DISABLED (404) unless ELYON_GATE_READ_ENDPOINTS=1. Intended to be reached
# over an operator tunnel; never expose them on the public gate surface.
# Build-then-wire: with the flag unset the gate is byte-behavior-unchanged.

READ_ENDPOINTS_ENV = "ELYON_GATE_READ_ENDPOINTS"


def _read_log_records(log):
    """Best-effort read of a JSONL governance log (issuance or approval)."""
    path = getattr(log, "path", None)
    if not path:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except (OSError, ValueError):
        return []


def _require_read_endpoints():
    if os.environ.get(READ_ENDPOINTS_ENV) != "1":
        raise HTTPException(status_code=404, detail="not found")


@app.get("/pending")
def pending_holds():
    """Currently-held 202 approval requests: approval_request records with no
    matching grant_consumed, derived from the durable approval log (so the view
    survives a gate restart and stays truthful under [FIX H8] record-before-act)."""
    _require_read_endpoints()
    recs = _read_log_records(_get_approval_log())
    consumed = {
        (r.get("decision_sha256"), r.get("approval_request_id"))
        for r in recs if r.get("type") == "grant_consumed"
    }
    return [
        r for r in recs
        if r.get("type") == "approval_request"
        and (r.get("decision_sha256"), r.get("approval_request_id")) not in consumed
    ]


@app.get("/audit")
def audit_tail(tail: int = 50):
    """Last N records from each governance log (issuance + approval). Read-only."""
    _require_read_endpoints()
    n = max(0, min(int(tail), 1000))
    return {
        "issuance": _read_log_records(_get_issuance_log())[-n:],
        "approval": _read_log_records(_get_approval_log())[-n:],
    }
