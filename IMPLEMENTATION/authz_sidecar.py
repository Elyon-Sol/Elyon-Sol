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
     the pinned anchor, the pinned gate signing public key, and the optional
     clock-skew tolerance. Incomplete / malformed configuration FAILS CLOSED
     (REF_TARGET_NOT_CONFIGURED) - the same per-request fail-closed posture
     reference_target.py and pep.py take when the trust base is unconfigured.
  2. Read the X-Elyon-Sol-Envelope attestation header (absent / unparseable ->
     treated as no envelope). A direct, un-attested caller (adversary A1) reaches
     the gate with envelope=None and is refused (REF_VERIFY_ENVELOPE_ABSENT).
  3. Extract the live interaction (the load-bearing design point, section 5). The
     DEFAULT (attested-forward) extractor reads the gate-normalized interaction
     from the structured X-Elyon-Sol-Interaction header (canonical-JSON). The
     CUSTOM declarative-mapping extractor (gate-less deployments) is phase 4 and
     is NOT built here; the extractor is an injectable seam so that mode can land
     later without touching this module's decision path.
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

Secure distribution of the anchor and the public-key pin is the named G5 floor
(Decision F; external_verification_readiness gate 5): acknowledged, not defended
here.
"""

import json
import os
from datetime import timedelta
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool

from IMPLEMENTATION.executor_sdk import ExecutorGate
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

    return {
        "target_url": target_url,
        "record_bytes": record_bytes,
        "pinned_root_sha256": pinned_root,
        "pinned_public_keys": {key_id: public_key},
        "clock_skew": clock_skew,
    }


def default_interaction_extractor(request: Request) -> Optional[Dict[str, Any]]:
    """
    DEFAULT (attested-forward) interaction extractor (design section 5).

    The upstream gate (pep.py) already normalized and forwarded the interaction;
    the sidecar reads it from the structured X-Elyon-Sol-Interaction header
    (canonical-JSON) and lets verify_envelope check the envelope binds to it.
    Zero per-deployment mapping. An absent or unparseable header yields None - the
    gate then refuses at the binding check (envelope present) or the presence
    guard (envelope absent); never an exception, never a fail-open.

    The CUSTOM declarative-mapping extractor (gate-less / direct deployments,
    design section 5) is phase 4 and is deliberately NOT built here; a deployment
    that needs it injects its own extractor with this same signature.

    SECURITY SCOPE (B-01, cross-model finding): this default reads the interaction
    from a CLIENT-CONTROLLABLE header. It is safe for the standalone decision
    endpoint (the sidecar only answers ALLOW/DENY; nothing executes a body behind
    it). It is NOT safe INLINE in front of a body-carrying upstream (Envoy
    ext_authz) with this default, because the header need not match the bytes the
    upstream executes. For inline use, build the phase-4 extractor that derives the
    interaction from the ext_authz request itself (method/path/body), or require
    the upstream to re-verify the same envelope it executes. Until then, do not
    place the sidecar inline.
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
    interaction_extractor: Callable[[Request], Optional[Dict[str, Any]]] = default_interaction_extractor,
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

    interaction_extractor is injectable so the phase-4 CUSTOM declarative mapping
    can be supplied later without changing the decision path.
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

            # Step 3: extract the live interaction (default: header-read).
            interaction = interaction_extractor(request)

            # Step 4: the PRODUCTION gate is the SOLE acceptance authority. Build
            # it from out-of-band config, sharing the app's replay cache (the
            # VL-076 seam) so replay defense holds across requests and, with a
            # shared/Redis cache, across instances. record_bytes + the pinned
            # anchor reproduce reference_target's anchor-verified currency base; a
            # record whose bytes do not hash to the pin makes the gate's record
            # load fail -> REF_TARGET_ANCHOR_MISMATCH (fail closed before any
            # currency claim is trusted).
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
