"""
Reference downstream enforcing target for Elyon-Sol
(docs/restructure/12_g5_transport_design.md step 4).

This is the standalone, deployable enforcing target that supersedes the
8-line IMPLEMENTATION/target.py stub. It promotes the embedded scaffolding -
the TARGET_DRIVER subprocess string in
EVIDENCE/proofs/g5_signed_cross_host_001_runner.py and the in-process
_build_cross_host_target_app / build_enforcing_target_app helpers in
TESTS/adversarial/test_cross_host.py and TESTS/adversarial/test_enforcement.py -
into one real service a deployer can run and an external attacker can point at.

==============================================================
What it does (the reference policy)
==============================================================

On every POST to /target the target, by its OWN policy, decides whether to
honor or refuse the call:

  1. Resolve out-of-band configuration (never from the repo): the URL this
     target serves (for the binding check), the publisher URL, the pinned
     published-record anchor, and the pinned gate signing public key.
     Incomplete / malformed configuration FAILS CLOSED
     (REF_TARGET_NOT_CONFIGURED) - the target refuses rather than act on an
     unconfigured trust base, the same per-request fail-closed posture pep.py
     takes when no signing key is configured.
  2. Read the X-Elyon-Sol-Envelope attestation header (absent / unparseable
     -> treated as no envelope). A direct, un-attested caller (adversary A1)
     therefore reaches step 4 with envelope=None and is refused there
     (REF_VERIFY_ENVELOPE_ABSENT). A1 is closed by THIS target's policy of
     requiring a valid attestation, NOT by the gate (verifier.py lines 67-72;
     artifact 08 section 4.4; artifact 12 step 4).
  3. Fetch the published record from the publisher and anchor-verify it
     against the pinned root (published_source.fetch_published_record). A
     transport failure, a non-200, or a record whose bytes do not hash to the
     pinned anchor returns None -> refuse (REF_TARGET_ANCHOR_MISMATCH) before
     any envelope currency claim is trusted (fail-closed, canon section 9).
  4. Call verifier.verify_envelope(envelope, interaction, target_url,
     record_source=<fetched record>, pinned_public_keys=<pinned gate key>).
     Because a pinned key is supplied, the issuer signature is REQUIRED and
     verified fail-closed BEFORE currency (the signed path; the production gate
     signs every default forward per VL-047). Currency is checked against the
     FETCHED record, not local disk (Decision C / D-b; VL-039). The interaction
     binding (request_context + target_url) closes same-state replay (A3).
     Honor (200, act) iff verify_envelope accepts; otherwise refuse (403) and
     do not act.

==============================================================
Reference policy, NOT authored-to-pass (the finish-line-(B) requirement)
==============================================================

The acceptance criterion is exactly "verify_envelope accepts against the
anchor-verified fetched record AND the pinned gate signature verifies." It is
not tuned to any author happy-path test vector: the target consults only its
out-of-band pins and the production verifier. This is the load-bearing property
for finish line (B) - a target an EXTERNAL attacker can point at must not be
calibrated to the author's vectors (artifact 12 sections 2, 4). Per GR-3, any
attack run in-loop against this target is characterization, not certification;
G5 CLOSED requires the external attacker (artifact 12 section 1).

==============================================================
No new canonical invariant (canon section 14)
==============================================================

The target verifies and acts or refuses; it does not decide admissibility and
it does not execute the gate's logic. Fetching a record and verifying an
envelope are verification I/O - the same posture published_source.py and
verifier.py already hold (artifact 08 section 5; transport.py header).

==============================================================
Out-of-band configuration (custody parallel to pep._get_signing_key and
transport.py's ELYON_TLS_* and the published-record anchor)
==============================================================

Resolved from the environment, never from the repo:

  ELYON_TARGET_URL          - the URL this target serves; the envelope's
                              target_url must equal it (binding).
  ELYON_PUBLISHER_URL       - where the published record is fetched.
  ELYON_PINNED_ROOT_SHA256  - the out-of-band published-record anchor (sha256
                              of the authentic published-record bytes),
                              distributed out-of-band, NEVER fetched alongside
                              the record (that would be circular;
                              published_source.py header lines 22-27).
  ELYON_GATE_KEY_ID         - the pinned gate signing key id.
  ELYON_GATE_PUBLIC_KEY_HEX - the pinned gate signing public key, raw Ed25519
                              public bytes as hex.

Secure distribution of the anchor and the public-key pin is itself the named G5
floor (Decision F; external_verification_readiness gate 5): acknowledged, not
defended here.

Build-then-wire (the project discipline since VL-025): this module adds a real
service with NO change to the gate's default path. pep.py does not import it;
the gate only POSTs to a target_url. Wiring the two-node harness to run THIS
target as node B (replacing the stub) is artifact 12 step 2.

Deploy:  uvicorn IMPLEMENTATION.reference_target:app --host 0.0.0.0 --port 9000
(with the ELYON_* environment configured out-of-band).

Ledger: VL-061 (T-G5-transport; artifact 12 step 4 reference enforcing target).
"""

import json
import os
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from datetime import datetime, timezone

from fastapi.concurrency import run_in_threadpool

from IMPLEMENTATION.published_source import fetch_published_record
from IMPLEMENTATION.verifier import verify_envelope, REF_VERIFY_REPLAY


# Target-layer reason vocabulary (REF_TARGET_*; parallels the REF_VERIFY_* layer
# owned by verifier.py and the REF_SCHEMA_* layer owned by
# request_validator.py). Two codes the target itself emits; every other refusal
# reason is the REF_VERIFY_* code verify_envelope returns, surfaced unchanged.
# REF_TARGET_ANCHOR_MISMATCH matches the name used by the scaffolding this module
# promotes (TESTS/adversarial/test_cross_host.py;
# EVIDENCE/proofs/g5_signed_cross_host_001_runner.py).
REF_TARGET_NOT_CONFIGURED = "REF_TARGET_NOT_CONFIGURED"
REF_TARGET_ANCHOR_MISMATCH = "REF_TARGET_ANCHOR_MISMATCH"

# The attestation header the gate pushes on its ELIGIBLE forward
# (pep.py line 280; canonical_json of the signed envelope).
ENVELOPE_HEADER = "X-Elyon-Sol-Envelope"

# Out-of-band configuration environment variable names.
ENV_TARGET_URL = "ELYON_TARGET_URL"
ENV_PUBLISHER_URL = "ELYON_PUBLISHER_URL"
ENV_PINNED_ROOT = "ELYON_PINNED_ROOT_SHA256"
ENV_GATE_KEY_ID = "ELYON_GATE_KEY_ID"
ENV_GATE_PUBLIC_KEY_HEX = "ELYON_GATE_PUBLIC_KEY_HEX"


def config_from_env() -> Optional[Dict[str, Any]]:
    """
    Resolve the target's out-of-band configuration from the environment.

    Returns a config dict on success:
        {"target_url", "publisher_url", "pinned_root_sha256",
         "pinned_public_keys": {key_id: Ed25519PublicKey}}
    or None if any required value is absent or the pinned public-key material is
    malformed. None is the caller's signal to fail closed
    (REF_TARGET_NOT_CONFIGURED): an unconfigured or mis-keyed target must not
    act. cryptography is imported lazily so this module stays import-clean
    (matching pep._get_signing_key and the envelope / verifier duck-typing).
    """
    target_url = os.environ.get(ENV_TARGET_URL)
    publisher_url = os.environ.get(ENV_PUBLISHER_URL)
    pinned_root = os.environ.get(ENV_PINNED_ROOT)
    key_id = os.environ.get(ENV_GATE_KEY_ID)
    key_hex = os.environ.get(ENV_GATE_PUBLIC_KEY_HEX)
    if not (target_url and publisher_url and pinned_root and key_id and key_hex):
        return None
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey,
        )
        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(key_hex))
    except Exception:
        return None
    return {
        "target_url": target_url,
        "publisher_url": publisher_url,
        "pinned_root_sha256": pinned_root,
        "pinned_public_keys": {key_id: public_key},
    }


def _refuse(reason: str) -> HTTPException:
    return HTTPException(
        status_code=403,
        detail={"honored": False, "reason": reason},
    )


def build_reference_target_app(
    config_provider: Callable[[], Optional[Dict[str, Any]]] = config_from_env,
    fetch: Callable[..., Optional[Dict[str, Any]]] = fetch_published_record,
) -> FastAPI:
    """
    Build the reference enforcing-target ASGI app.

    config_provider is called per request, so configuration (and tests that
    inject it) resolve at request time and a misconfigured deployment fails
    closed per request (REF_TARGET_NOT_CONFIGURED) rather than failing to boot -
    the same per-request fail-closed posture pep.py takes when no signing key is
    configured. fetch is injectable so tests can drive the published-record hop
    through a TestClient publisher; the default is the production cross-host
    fetch_published_record over a real socket.

    The acted-upon interactions are recorded on app.state.received (a list); a
    refused call never appends to it. This mirrors the `received` list the
    scaffolding targets expose, so a runner / test can assert the target acted
    exactly once on honor and never on refuse.
    """
    app = FastAPI(title="Elyon-Sol reference enforcing target")
    app.state.received = []
    app.state.seen = {}  # decision_id -> not_after (TTL-bounded replay cache)

    @app.post("/target")
    async def target(request: Request):
        config = config_provider()
        if config is None:
            raise _refuse(REF_TARGET_NOT_CONFIGURED)

        # Body (the normalized interaction the gate forwards). A non-JSON body
        # from an adversary is tolerated as None: a present envelope is then
        # refused at the binding check, an absent one at the presence guard -
        # never a 500.
        try:
            interaction = await request.json()
        except Exception:
            interaction = None

        raw = request.headers.get(ENVELOPE_HEADER)
        envelope = None
        if raw is not None:
            try:
                envelope = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                envelope = None  # unparseable header -> treated as absent (A1)

        # Published-record fetch + anchor verification, off the event loop
        # (fetch_published_record is a blocking requests.get). None means a
        # transport failure / non-200 / anchor mismatch -> fail closed before
        # trusting any currency claim.
        record = await run_in_threadpool(
            fetch, config["publisher_url"], config["pinned_root_sha256"]
        )
        if record is None:
            raise _refuse(REF_TARGET_ANCHOR_MISMATCH)

        # The production verifier is the SOLE acceptance authority. A pinned
        # gate key is supplied, so the issuer signature is required and checked
        # fail-closed before currency (the signed path). Currency is checked
        # against the FETCHED record; the binding closes same-state replay.
        result = verify_envelope(
            envelope,
            interaction,
            config["target_url"],
            record_source=record,
            pinned_public_keys=config["pinned_public_keys"],
        )
        if not result["accepted"]:
            raise _refuse(result["reason"])

        # Replay defense (exactly-once over the freshness window): refuse a
        # decision_id already honored. The window bounds the seen-set - entries
        # are pruned once their not_after passes (past which freshness refuses
        # them anyway). decision_id is in the signed region (tamper-proof) and is
        # stamped by the default gate forward. NOTE: a single in-memory set is
        # per-instance; a horizontally-scaled executor needs a SHARED cache
        # (e.g. Redis, TTL = max-age) or a replay can cross instances.
        decision_id = envelope.get("decision_id")
        if decision_id is not None:
            seen = app.state.seen
            now = datetime.now(timezone.utc)
            for k in [k for k, exp in seen.items() if exp is not None and exp <= now]:
                del seen[k]
            if decision_id in seen:
                raise _refuse(REF_VERIFY_REPLAY)
            exp = None
            na = envelope.get("not_after")
            if isinstance(na, str):
                try:
                    exp = datetime.fromisoformat(na)
                except ValueError:
                    exp = None
            seen[decision_id] = exp

        app.state.received.append(interaction)  # the target acts only here
        return {"honored": True, "reason": result["reason"]}

    @app.get("/received")
    async def received():
        """Observability (read-only): how many calls the target has acted on.

        Lets a multi-process / real-transport runner confirm an honor verdict over
        a real socket without redelivering the envelope. Not part of the admission
        policy and not a trust surface; it discloses only an integer count.
        """
        return {"count": len(app.state.received)}

    return app


# Module-level deployable app: resolves configuration from the environment per
# request. `uvicorn IMPLEMENTATION.reference_target:app` serves it.
app = build_reference_target_app()
