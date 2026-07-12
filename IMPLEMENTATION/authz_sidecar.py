"""
HTTP ext-authz admissibility sidecar for Elyon-Sol
(docs/design/opa_sidecar_design.md sections 2/4/5/11 step 1).

This is the transport adapter that makes the SHIPPED admissibility verifier
consumable by an OPA/Envoy deployment without the user writing Python. It is the
IMPLEMENTATION/reference_target.py consume-path (read the X-Elyon-Sol-Envelope
header -> resolve out-of-band trust -> verify_envelope -> honor/refuse) refactored
from "a target that ACTS" into "an authorizer that ANSWERS allow/deny," so it can
sit as an Envoy ext_authz filter in front of ANY target, including an OPA-gated one.

==============================================================
What it does (and does NOT do)
==============================================================

On every authorization check (POST /authz) the sidecar, by its OWN out-of-band
configuration, decides ALLOW or DENY for the incoming request:

  1. Resolve out-of-band configuration (never from the repo): the target_url this
     surface serves (for the binding check), the local published-record bytes +
     the pinned anchor, the pinned gate signing public key, the optional
     clock-skew tolerance, and (optionally) a pinned publisher key enabling
     SIGNED-record freshness mode (F-01, VL-112). Incomplete / malformed
     configuration FAILS CLOSED
     (REF_TARGET_NOT_CONFIGURED) - the same per-request fail-closed posture
     reference_target.py and pep.py take when the trust base is unconfigured.
  2. Read the X-Elyon-Sol-Envelope attestation header (absent / unparseable ->
     treated as no envelope). A direct, un-attested caller (adversary A1) reaches
     the gate with envelope=None and is refused (REF_VERIFY_ENVELOPE_ABSENT).
  3. Extract the live interaction (the load-bearing design point, section 5). The
     DEFAULT (attested-forward) extractor reads the gate-normalized interaction
     from the structured X-Elyon-Sol-Interaction header (canonical-JSON). The
     CUSTOM declarative-mapping extractor (gate-less / INLINE deployments) is
     build-order step 4 and is now provided by `build_request_body_extractor`
     (B-01): it derives the interaction from the ext_authz request body so the
     binding covers the bytes the upstream executes. Both are injectable through
     the same seam; the DEFAULT stays header-read, so no default path changes.
  4. Hand (envelope, interaction) to the PRODUCTION ExecutorGate.check, which
     composes verify_envelope (signature -> reassert/currency -> binding ->
     freshness) and the VL-076 ReplayCache seam. The sidecar performs NO
     admissibility logic and NO cryptography of its own; it imports the gate and
     surfaces its Decision.

Response (decision contract, design section 4):
  - 200 + `x-elyon-decision: ALLOW`  on accept.
  - 403 + `x-elyon-decision: DENY` + `x-elyon-reason: <REF_*>` on refuse.
  - 403 + `REF_TARGET_*` on any internal / anchor / parse / config error
    (fail closed; never a 5xx-as-allow).

This mirrors verify_envelope's accept/reason dict and the reference target's
200/403, surfaced over the ext_authz boundary instead of the /target act boundary.

==============================================================
Reuse, not re-implementation (kickoff guardrails)
==============================================================

REUSES: ExecutorGate (executor_sdk), verify_envelope (the whole chain via the
gate), the ReplayCache seam (replay_cache_from_env), the published-record anchor
reader (executor_sdk -> published_source), the REF_VERIFY_* / REF_TARGET_*
vocabularies. ADDS only an HTTP ext_authz envelope (request <-> check contract)
and the default header-read interaction extractor. No new admissibility logic, no
new cryptography, no new refusal code, no new canonical invariant (canon section
14). Normalization stays byte-identical to issuance because verify_envelope
normalizes AP/OP symmetrically (verifier._normalize_set_field), the same rule the
PEP applied.

Build-then-wire (the project discipline since VL-025): this module adds a NEW
service with NO change to any existing default path. pep.py / reference_target.py
are byte-unchanged; nothing imports this module. The container + Envoy example
(deploy/elyon-authz, deploy/envoy.example.yaml) is the wiring.

==============================================================
Out-of-band configuration (parity with reference_target.config_from_env and
the replay_cache_from_env / issuance_log_from_env *_from_env seam)
==============================================================

Resolved from the environment, never from the repo:

  ELYON_TARGET_URL          - the target identity envelopes bind to; the
                              envelope's target_url must equal it (binding).
  ELYON_RECORD_PATH         - local path to the published-record bytes
                              (published_hashes.json); the deployer mounts it.
  ELYON_PINNED_ROOT_SHA256  - the out-of-band published-record anchor (sha256 of
                              the authentic record bytes), distributed out-of-band,
                              NEVER fetched alongside the record (circular).
  ELYON_GATE_KEY_ID         - the pinned gate signing key id.
  ELYON_GATE_PUBLIC_KEY_HEX - the pinned gate signing public key (raw Ed25519
                              public bytes as hex).
  ELYON_CLOCK_SKEW_SECONDS  - optional non-negative skew tolerance (seconds,
                              default 0; verify_envelope clock_skew, VL-075).
  ELYON_REPLAY_REDIS_URL    - optional; a shared Redis-backed ReplayCache for
                              cross-instance exactly-once (replay_cache_from_env,
                              VL-076/094). Absent -> per-instance InMemoryReplayCache.
  ELYON_PUBLISHER_KEY_ID    - optional (F-01 signed mode); the pinned publisher
                              signing key id. Present with _HEX -> SIGNED mode.
  ELYON_PUBLISHER_KEY_HEX   - optional (F-01); the pinned publisher signing public
                              key (raw Ed25519 public bytes as hex).
  ELYON_EXT_AUTHZ_INLINE    - SES-6 (VL-144) posture declaration: set to 1/true/yes
                              when the sidecar sits INLINE (Envoy ext_authz) in
                              front of a body-carrying upstream. Under this
                              declaration the header-read default extractor is
                              refused (fail closed) and the body-deriving
                              extractor is resolved from ELYON_INLINE_AP / _OP /
                              _MANIFEST_VERSION / _MANIFEST_SHA256 / _TOOL
                              (/ _ARGS_FIELD); an absent/incomplete mapping
                              DENIES every check (REF_TARGET_NOT_CONFIGURED).
                              Unset -> standalone header-read default, unchanged.
  ELYON_SIGNED_RECORD_PATH  - optional (F-01); local path to the SIGNED record
                              (published_hashes_signed.json). Defaults to the
                              ELYON_RECORD_PATH sibling filename. In signed mode the
                              sidecar validates this record's publisher signature +
                              freshness + serial per request and uses it as the
                              gate's record_source; a stale/invalid record fails
                              closed (REF_VERIFY_PUBLISHED_RECORD_STALE / _INVALID).
                              Absent publisher key -> byte-anchor path unchanged.

Secure distribution of the anchor and the public-key pin is the named G5 floor
(Decision F; external_verification_readiness gate 5): acknowledged, not defended
here.
"""

import hashlib
import inspect
import json
import os
from datetime import timedelta
from typing import Any, Callable, Dict, List, Optional, Union

from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool

from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.executor_sdk import ExecutorGate
from IMPLEMENTATION.published_record_source import load_signed_record_from_bytes
from IMPLEMENTATION.reference_target import (
    REF_TARGET_ANCHOR_MISMATCH,
    REF_TARGET_NOT_CONFIGURED,
)
from IMPLEMENTATION.replay_cache import replay_cache_from_env


# The attestation header the gate pushes on its ELIGIBLE forward (pep.py line 329;
# canonical_json of the signed envelope). Re-exported name, not a new constant.
ENVELOPE_HEADER = "X-Elyon-Sol-Envelope"
# The structured header carrying the gate-normalized interaction (design section 5,
# DEFAULT attested-forward extractor). canonical-JSON of the normalized interaction.
INTERACTION_HEADER = "X-Elyon-Sol-Interaction"

# Decision headers on the ext_authz response (design section 4).
DECISION_HEADER = "x-elyon-decision"
REASON_HEADER = "x-elyon-reason"
DECISION_ALLOW = "ALLOW"
DECISION_DENY = "DENY"

# Out-of-band configuration environment variable names.
ENV_TARGET_URL = "ELYON_TARGET_URL"
ENV_RECORD_PATH = "ELYON_RECORD_PATH"
ENV_PINNED_ROOT = "ELYON_PINNED_ROOT_SHA256"
ENV_GATE_KEY_ID = "ELYON_GATE_KEY_ID"
ENV_GATE_PUBLIC_KEY_HEX = "ELYON_GATE_PUBLIC_KEY_HEX"
ENV_CLOCK_SKEW_SECONDS = "ELYON_CLOCK_SKEW_SECONDS"
# Optional signed-record (freshness) mode env vars (F-01, VL-112; parity with
# reference_target's ELYON_PUBLISHER_KEY_*). When a pinned publisher key is
# present the sidecar consults a LOCAL SIGNED record (publisher signature +
# freshness + serial) instead of the byte-anchor record. Absent -> byte-anchor
# path unchanged.
ENV_PUBLISHER_KEY_ID = "ELYON_PUBLISHER_KEY_ID"
ENV_PUBLISHER_KEY_HEX = "ELYON_PUBLISHER_KEY_HEX"
ENV_SIGNED_RECORD_PATH = "ELYON_SIGNED_RECORD_PATH"
# SES-6 (VL-144) inline-posture declaration + declarative body-extractor mapping.
# An INLINE deployment (Envoy ext_authz in front of a body-carrying upstream)
# MUST declare ELYON_EXT_AUTHZ_INLINE=1; under that declaration the header-read
# default extractor is REFUSED (fail closed, REF_TARGET_NOT_CONFIGURED) and the
# body-deriving extractor is resolved from the ELYON_INLINE_* mapping instead
# (the R-02 declare-or-fail pattern: the process cannot SEE its own topology,
# so the declaration is load-bearing). Standalone (flag unset) is unchanged.
ENV_EXT_AUTHZ_INLINE = "ELYON_EXT_AUTHZ_INLINE"
ENV_INLINE_AP = "ELYON_INLINE_AP"                              # comma-separated
ENV_INLINE_OP = "ELYON_INLINE_OP"                              # comma-separated
ENV_INLINE_MANIFEST_VERSION = "ELYON_INLINE_MANIFEST_VERSION"
ENV_INLINE_MANIFEST_SHA256 = "ELYON_INLINE_MANIFEST_SHA256"
ENV_INLINE_TOOL = "ELYON_INLINE_TOOL"    # literal | "path" | "header:<Name>"
ENV_INLINE_ARGS_FIELD = "ELYON_INLINE_ARGS_FIELD"              # optional


def config_from_env() -> Optional[Dict[str, Any]]:
    """
    Resolve the sidecar's out-of-band configuration from the environment.

    Returns a config dict on success:
        {"target_url", "record_bytes", "pinned_root_sha256",
         "pinned_public_keys": {key_id: Ed25519PublicKey}, "clock_skew"}
    or None if any required value is absent, the record file is unreadable, the
    pinned public-key material is malformed, or the clock skew is malformed /
    negative. None is the caller's signal to fail closed
    (REF_TARGET_NOT_CONFIGURED): an unconfigured or mis-keyed sidecar must not
    answer ALLOW. cryptography is imported lazily so this module stays
    import-clean (matching reference_target.config_from_env and pep._get_signing_key).
    """
    target_url = os.environ.get(ENV_TARGET_URL)
    record_path = os.environ.get(ENV_RECORD_PATH)
    pinned_root = os.environ.get(ENV_PINNED_ROOT)
    key_id = os.environ.get(ENV_GATE_KEY_ID)
    key_hex = os.environ.get(ENV_GATE_PUBLIC_KEY_HEX)
    if not (target_url and record_path and pinned_root and key_id and key_hex):
        return None

    try:
        with open(record_path, "rb") as f:
            record_bytes = f.read()
    except OSError:
        return None

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey,
        )
        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(key_hex))
    except Exception:
        return None

    # Optional clock-skew tolerance (VL-075). Absent -> 0 (strict). A malformed or
    # negative value is a configuration error -> fail closed rather than silently
    # widen / narrow the honored window.
    skew_raw = os.environ.get(ENV_CLOCK_SKEW_SECONDS)
    if skew_raw is None:
        clock_skew = timedelta(0)
    else:
        try:
            seconds = float(skew_raw)
        except ValueError:
            return None
        if seconds < 0:
            return None
        clock_skew = timedelta(seconds=seconds)

    config = {
        "target_url": target_url,
        "record_bytes": record_bytes,
        "pinned_root_sha256": pinned_root,
        "pinned_public_keys": {key_id: public_key},
        "clock_skew": clock_skew,
    }

    # Optional signed-record (freshness) mode (F-01, VL-112): pin a publisher key
    # and point at a LOCAL signed record. When present, the sidecar validates the
    # signed record per request (publisher signature + freshness + serial via
    # published_record_source.load_signed_record_from_bytes) and uses the
    # validated record as the gate's record_source instead of the byte-anchor
    # record; a stale/invalid record fails closed with the reader's
    # REF_VERIFY_PUBLISHED_RECORD_* reason. Absent -> the byte-anchor path is
    # byte-behaviour-unchanged. The signed-record bytes are READ here (an
    # unreadable file is a config fault -> None -> REF_TARGET_NOT_CONFIGURED); the
    # freshness/signature decision is made per request in the handler so it
    # surfaces the right reason. The signed path defaults to the byte-anchor
    # path's sibling filename (published_hashes.json -> published_hashes_signed.json),
    # the same derivation reference_target uses for its signed URL.
    pub_key_id = os.environ.get(ENV_PUBLISHER_KEY_ID)
    pub_key_hex = os.environ.get(ENV_PUBLISHER_KEY_HEX)
    if pub_key_id and pub_key_hex:
        try:
            publisher_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_key_hex))
        except Exception:
            return None
        signed_record_path = os.environ.get(ENV_SIGNED_RECORD_PATH) or \
            record_path.replace("published_hashes.json", "published_hashes_signed.json")
        try:
            with open(signed_record_path, "rb") as f:
                signed_record_bytes = f.read()
        except OSError:
            return None
        config["pinned_publisher_keys"] = {pub_key_id: publisher_key}
        config["signed_record_bytes"] = signed_record_bytes

    return config


def default_interaction_extractor(request: Request) -> Optional[Dict[str, Any]]:
    """
    DEFAULT (attested-forward) interaction extractor (design section 5).

    The upstream gate (pep.py) already normalized and forwarded the interaction;
    the sidecar reads it from the structured X-Elyon-Sol-Interaction header
    (canonical-JSON) and lets verify_envelope check the envelope binds to it.
    Zero per-deployment mapping. An absent or unparseable header yields None - the
    gate then refuses at the binding check (envelope present) or the presence
    guard (envelope absent); never an exception, never a fail-open.

    The CUSTOM declarative-mapping extractor (gate-less / direct / INLINE
    deployments, design section 5) is build-order step 4 and is provided by
    `build_request_body_extractor` below; a deployment that needs it injects that
    extractor (or its own) with this same signature.

    SECURITY SCOPE (B-01, cross-model finding): this default reads the interaction
    from a CLIENT-CONTROLLABLE header. It is safe for the standalone decision
    endpoint (the sidecar only answers ALLOW/DENY; nothing executes a body behind
    it). It is NOT safe INLINE in front of a body-carrying upstream (Envoy
    ext_authz) with this default, because the header need not match the bytes the
    upstream executes. For inline use, inject `build_request_body_extractor`
    (B-01 step 4), which derives the interaction from the ext_authz request body
    so the binding covers the bytes the upstream executes; or require the upstream
    to re-verify the same envelope it executes. Do NOT place the sidecar inline
    with this default header-read extractor.

    SES-6 (VL-144): the warning above is now ENFORCED via declare-or-fail. An
    inline deployment declares ELYON_EXT_AUTHZ_INLINE=1, under which this
    header-read extractor is refused (REF_TARGET_NOT_CONFIGURED) and the
    body-deriving extractor is resolved from the ELYON_INLINE_* mapping
    (resolve_interaction_extractor_from_env). The process cannot detect its own
    topology, so the declaration is load-bearing (the R-02 / VL-123 G-02
    operator-declaration pattern); an UNDECLARED inline placement remains an
    operator error this module cannot see.
    """
    # P-01: a duplicate interaction header is ambiguous (which value binds would
    # depend on header ordering) -> treat as absent, fail closed at the binding check.
    if len(request.headers.getlist(INTERACTION_HEADER)) > 1:
        return None
    raw = request.headers.get(INTERACTION_HEADER)
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


# --------------------------------------------------------------------------- #
# CUSTOM (gate-less / INLINE) interaction extractor - B-01 build-order step 4
# --------------------------------------------------------------------------- #
#
# The DEFAULT extractor above reads the interaction from a header the upstream
# gate set. Placed INLINE in front of a body-carrying upstream, that header is
# client-controllable and need not match the bytes the upstream executes
# (finding B-01, cross-model convergent / rated High): an attacker can present a
# valid envelope plus a benign interaction header while sending a different body
# for the upstream to act on. This extractor closes that gap by deriving the live
# interaction from the ext_authz request ITSELF - specifically the request body
# Envoy forwards (the SAME bytes the upstream receives) - so context.args_sha256
# binds the envelope to what is actually EXECUTED, not to a side-channel header.
#
# It is the "declarative mapping" of design section 5: the deployer authors the
# static parts of the interaction (the authority/operation sets and manifest
# pinning the route requires, plus where the tool identity comes from); the args
# digest is taken from the body at request time. The mapping is config, not code
# - this factory turns it into an extractor with the SAME signature as
# default_interaction_extractor (an injectable seam, build-then-wire: no default
# path changes; nothing wires this on by default).


def _resolve_tool(
    tool_spec: Union[str, Dict[str, Any]], request: Request
) -> Optional[str]:
    """Resolve the interaction's context.tool from the declarative mapping.

    tool_spec is one of:
      - a literal str                  -> a constant tool identity (one tool per
                                          route).
      - {"from": "path"}               -> the request path (request.url.path).
      - {"from": "header", "name": H}  -> the value of request header H.

    Anything that does not resolve to a non-empty str returns None (the gate then
    fails closed at the binding check); never raises.
    """
    if isinstance(tool_spec, str):
        return tool_spec or None
    if isinstance(tool_spec, dict):
        src = tool_spec.get("from")
        if src == "path":
            return request.url.path or None
        if src == "header":
            name = tool_spec.get("name")
            if isinstance(name, str):
                return request.headers.get(name) or None
    return None


def build_request_body_extractor(
    *,
    ap: List[str],
    op: List[str],
    expected_manifest_version: str,
    expected_manifest_sha256: str,
    tool: Union[str, Dict[str, Any]],
    args_field: Optional[str] = None,
) -> Callable[[Request], Any]:
    """Build a CUSTOM interaction extractor that derives the interaction from the
    ext_authz request BODY (B-01 step 4; design section 5 CUSTOM mode).

    The returned extractor reproduces the canonical interaction shape that
    IMPLEMENTATION/mcp_server.interaction_for emits, so the gate's binding check
    compares byte-identically:

        {AP, OP, context: {tool, args_sha256},
         expected_manifest_version, expected_manifest_sha256}

    with the load-bearing difference that context.args_sha256 is
    sha256(canonical_json(args)) over args taken from the REQUEST BODY, not from a
    client header:
      - args_field=None  -> the whole parsed JSON body IS the args object.
      - args_field="X"   -> body["X"] is the args object (body must be a JSON
                            object with that field, else fail closed).

    Because Envoy forwards the same body to the sidecar and to the upstream, the
    digest binds the envelope to the bytes the upstream EXECUTES - the property
    the default header-read extractor cannot offer inline.

    Declarative mapping (the deployer-authored piece, design section 5):
      ap, op                            - the authority/operation sets the route
                                          requires. Normalized (sorted + deduped,
                                          the request_validator rule) so the
                                          binding comparison is byte-identical to
                                          issuance.
      expected_manifest_version/sha256  - the manifest pin the route admits under.
      tool                              - see _resolve_tool.
      args_field                        - None (whole body) or a body sub-field.

    The extractor is async (it must read request.body()); build_authz_sidecar_app
    awaits an awaitable extractor result, so the default sync extractor is
    unaffected. Every malformed input (unparseable body, missing args field,
    unresolvable tool) returns None, which the gate turns into a fail-closed
    refusal (binding mismatch / absent) - never an exception, never a fail-open.
    The extractor performs NO admissibility logic and NO cryptography; it only
    reconstructs the interaction the production gate then checks.
    """
    norm_ap = sorted(set(ap))
    norm_op = sorted(set(op))

    async def _extract(request: Request) -> Optional[Dict[str, Any]]:
        tool_id = _resolve_tool(tool, request)
        if tool_id is None:
            return None
        body_bytes = await request.body()
        try:
            parsed = json.loads(body_bytes)
        except (json.JSONDecodeError, ValueError, TypeError):
            return None
        if args_field is None:
            args = parsed
        elif isinstance(parsed, dict) and args_field in parsed:
            args = parsed[args_field]
        else:
            return None
        # The exact digest interaction_for uses, so a body equal to the args the
        # envelope was minted for yields an identical context.args_sha256.
        args_sha256 = hashlib.sha256(
            canonical_json(args).encode("utf-8")
        ).hexdigest()
        return {
            "AP": list(norm_ap),
            "OP": list(norm_op),
            "context": {"tool": tool_id, "args_sha256": args_sha256},
            "expected_manifest_version": expected_manifest_version,
            "expected_manifest_sha256": expected_manifest_sha256,
        }

    return _extract


# --------------------------------------------------------------------------- #
# SES-6 (VL-144): inline posture declaration + env-wired body extractor
# --------------------------------------------------------------------------- #

def inline_declared() -> bool:
    """True iff the deployment declares itself INLINE (Envoy ext_authz in front
    of a body-carrying upstream) via ELYON_EXT_AUTHZ_INLINE. Same truthy
    convention as ELYON_REPLAY_MULTI_INSTANCE (the R-02 guard)."""
    return os.environ.get(ENV_EXT_AUTHZ_INLINE, "").strip().lower() in ("1", "true", "yes")


def _csv_tokens(raw: Optional[str]) -> Optional[List[str]]:
    """Parse a comma-separated token list; None/empty -> None (fail closed)."""
    if not raw:
        return None
    tokens = [t.strip() for t in raw.split(",") if t.strip()]
    return tokens or None


def body_extractor_from_env() -> Optional[Callable[[Request], Any]]:
    """Build the body-deriving extractor (build_request_body_extractor) from the
    ELYON_INLINE_* declarative mapping. Returns None if any required value is
    absent or malformed - the caller's signal to fail closed
    (REF_TARGET_NOT_CONFIGURED), never a silent fallback to the header default.

    ELYON_INLINE_TOOL forms: "path" -> the request path; "header:<Name>" -> the
    value of request header <Name>; anything else -> a literal tool identity.
    """
    ap = _csv_tokens(os.environ.get(ENV_INLINE_AP))
    op = _csv_tokens(os.environ.get(ENV_INLINE_OP))
    version = os.environ.get(ENV_INLINE_MANIFEST_VERSION)
    sha = os.environ.get(ENV_INLINE_MANIFEST_SHA256)
    tool_raw = os.environ.get(ENV_INLINE_TOOL)
    if not (ap and op and version and sha and tool_raw):
        return None
    tool_raw = tool_raw.strip()
    if not tool_raw:
        return None
    tool: Union[str, Dict[str, Any]]
    if tool_raw == "path":
        tool = {"from": "path"}
    elif tool_raw.startswith("header:"):
        name = tool_raw[len("header:"):].strip()
        if not name:
            return None
        tool = {"from": "header", "name": name}
    else:
        tool = tool_raw
    args_field = os.environ.get(ENV_INLINE_ARGS_FIELD) or None
    return build_request_body_extractor(
        ap=ap,
        op=op,
        expected_manifest_version=version,
        expected_manifest_sha256=sha,
        tool=tool,
        args_field=args_field,
    )


def resolve_interaction_extractor_from_env() -> Optional[Callable[[Request], Any]]:
    """SES-6 (VL-144): resolve the interaction extractor from the declared
    deployment posture. INLINE declared -> the body-deriving extractor from the
    ELYON_INLINE_* mapping (None if incomplete -> fail closed); standalone
    (flag unset) -> the header-read default, byte-behavior-unchanged."""
    if inline_declared():
        return body_extractor_from_env()
    return default_interaction_extractor


def _deny(reason: str) -> Response:
    return Response(
        status_code=403,
        headers={DECISION_HEADER: DECISION_DENY, REASON_HEADER: reason},
    )


def _allow(reason: str) -> Response:
    return Response(
        status_code=200,
        headers={DECISION_HEADER: DECISION_ALLOW, REASON_HEADER: reason},
    )


def build_authz_sidecar_app(
    config_provider: Callable[[], Optional[Dict[str, Any]]] = config_from_env,
    interaction_extractor: Optional[Callable[[Request], Any]] = None,
    replay_cache=None,
) -> FastAPI:
    """
    Build the ext-authz sidecar ASGI app.

    config_provider is called per request, so configuration (and tests that
    inject it) resolve at request time and a misconfigured deployment fails closed
    per request (REF_TARGET_NOT_CONFIGURED) rather than failing to boot - the same
    per-request posture reference_target.py takes.

    The ReplayCache is the VL-076 seam and is created ONCE per app (so a
    decision_id honored on one request is refused on the next), shared across every
    ExecutorGate this app builds. Inject a single shared cache (or a Redis-backed
    one via replay_cache_from_env / ELYON_REPLAY_REDIS_URL) across app instances to
    get cross-instance exactly-once; the gate is otherwise stateless and rebuilt
    per request from config (parity with reference_target's per-request fail-closed).

    interaction_extractor is injectable so the CUSTOM declarative mapping
    (build_request_body_extractor, B-01 step 4) can be supplied without changing
    the decision path. It may be sync (the default header-read extractor) or
    async (the body-deriving extractor, which must read request.body()); an
    awaitable result is awaited.

    SES-6 (VL-144): interaction_extractor=None (the deployable default) resolves
    the extractor PER REQUEST from the declared posture
    (resolve_interaction_extractor_from_env): standalone -> the header-read
    default, byte-behavior-unchanged; ELYON_EXT_AUTHZ_INLINE declared -> the
    body-deriving extractor from the ELYON_INLINE_* mapping, or fail closed
    (REF_TARGET_NOT_CONFIGURED) if the mapping is absent/incomplete. Under an
    INLINE declaration the header-read default is REFUSED even when injected
    explicitly - the client-controllable header must never be the binding
    source in front of a body-carrying upstream (B-01/SES-6).
    """
    app = FastAPI(title="Elyon-Sol ext-authz admissibility sidecar")
    app.state.replay_cache = (
        replay_cache if replay_cache is not None else replay_cache_from_env()
    )

    async def _authz_handler(request: Request) -> Response:
        # Outermost fail-closed boundary (design section 4 / 8): ANY unexpected
        # exception -> 403 DENY, never a 5xx (which an ext_authz filter could be
        # configured to treat as allow) and never a fail-open. The two REF_TARGET_*
        # codes are the only sidecar-emitted reasons; every other DENY reason is the
        # REF_VERIFY_* / REF_TARGET_* code the gate's Decision carries, surfaced
        # unchanged. No new refusal code is introduced.
        try:
            config = config_provider()
            if config is None:
                return _deny(REF_TARGET_NOT_CONFIGURED)

            # Step 2: read the attestation header (absent / unparseable / DUPLICATE
            # -> A1). P-01: a duplicate envelope header is ambiguous (the verified
            # value would depend on header ordering), so treat it as absent -> fail closed.
            raw = (None if len(request.headers.getlist(ENVELOPE_HEADER)) > 1
                   else request.headers.get(ENVELOPE_HEADER))
            envelope = None
            if raw is not None:
                try:
                    envelope = json.loads(raw)
                except (json.JSONDecodeError, ValueError):
                    envelope = None

            # Step 3: extract the live interaction. SES-6 (VL-144): the active
            # extractor is resolved per request from the declared posture when
            # none was injected; an INLINE-declared deployment must never bind
            # from the client-controllable header, so the header-read default is
            # refused (fail closed) under that declaration - whether it arrived
            # by omission (incomplete ELYON_INLINE_* mapping -> None) or by
            # explicit injection. Standalone (no declaration) resolves to the
            # header-read default, byte-behavior-unchanged. An injected CUSTOM
            # extractor (B-01 step 4, build_request_body_extractor) is async, so
            # await an awaitable result; the sync default returns directly.
            extractor = (interaction_extractor
                         if interaction_extractor is not None
                         else resolve_interaction_extractor_from_env())
            if extractor is None or (
                inline_declared() and extractor is default_interaction_extractor
            ):
                return _deny(REF_TARGET_NOT_CONFIGURED)
            interaction = extractor(request)
            if inspect.isawaitable(interaction):
                interaction = await interaction

            # Step 4: the PRODUCTION gate is the SOLE acceptance authority. Build
            # it from out-of-band config, sharing the app's replay cache (the
            # VL-076 seam) so replay defense holds across requests and, with a
            # shared/Redis cache, across instances. record_bytes + the pinned
            # anchor reproduce reference_target's anchor-verified currency base; a
            # record whose bytes do not hash to the pin makes the gate's record
            # load fail -> REF_TARGET_ANCHOR_MISMATCH (fail closed before any
            # currency claim is trusted).
            # F-01 (VL-112): SIGNED mode when a publisher key is pinned - validate
            # the LOCAL signed record (publisher signature + freshness + serial)
            # and use the validated record as the gate's record_source; a stale /
            # invalid record fails closed with the reader's REF_VERIFY_PUBLISHED_
            # RECORD_* reason (this is the freshness the byte-anchor path lacks).
            # BYTE-ANCHOR mode (default, no publisher key): the unchanged
            # record_bytes + pinned_root path (no temporal dimension).
            if config.get("pinned_publisher_keys"):
                signed = load_signed_record_from_bytes(
                    config["signed_record_bytes"],
                    config["pinned_publisher_keys"],
                    clock_skew=config["clock_skew"],
                )
                if signed["reason"] is not None:
                    return _deny(signed["reason"])
                gate = ExecutorGate(
                    pinned_public_keys=config["pinned_public_keys"],
                    target_id=config["target_url"],
                    record_source=signed["record"],
                    replay_cache=request.app.state.replay_cache,
                    clock_skew=config["clock_skew"],
                )
            else:
                gate = ExecutorGate(
                    pinned_public_keys=config["pinned_public_keys"],
                    target_id=config["target_url"],
                    record_bytes=config["record_bytes"],
                    pinned_root=config["pinned_root_sha256"],
                    replay_cache=request.app.state.replay_cache,
                    clock_skew=config["clock_skew"],
                )

            # ExecutorGate.check loads + anchor-verifies the record, which for a
            # local file is fast but is still synchronous I/O; run it off the event
            # loop for parity with reference_target's threadpool fetch.
            decision = await run_in_threadpool(gate.check, envelope, interaction)

            if decision.honored:
                return _allow(decision.reason)
            return _deny(decision.reason)
        except Exception:
            # Internal / anchor / parse error -> fail closed (design section 4/8).
            # Reuse the existing REF_TARGET_ANCHOR_MISMATCH (the gate's own
            # trust-resolution failure code); introduce no new code.
            return _deny(REF_TARGET_ANCHOR_MISMATCH)

    # Register the handler on the bare path AND on a catch-all suffix. Envoy's HTTP
    # ext_authz builds the check path as `path_prefix` + the original request path
    # (path_prefix "/authz" + "/api/x" -> "/authz/api/x"), so the sidecar must
    # answer any path under /authz; the decision reads only headers, never the path.
    app.add_api_route("/authz", _authz_handler, methods=["POST"])
    app.add_api_route("/authz/{rest:path}", _authz_handler, methods=["POST"])

    @app.get("/healthz")
    async def healthz() -> Dict[str, str]:
        """Liveness only (read-only): does NOT report admissibility config state,
        so it is not a trust surface and cannot leak whether a key/anchor is
        present. An unconfigured sidecar is still 'live' and still fails every
        /authz closed."""
        return {"status": "ok"}

    return app


# Module-level deployable app: resolves configuration from the environment per
# request, with the replay cache chosen by the environment (Redis if
# ELYON_REPLAY_REDIS_URL is set, else in-memory).
# `uvicorn IMPLEMENTATION.authz_sidecar:app` serves it.
app = build_authz_sidecar_app()
