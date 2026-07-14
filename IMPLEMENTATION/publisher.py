"""
Standing published-record publisher for Elyon-Sol
(docs/restructure/12_g5_transport_design.md steps 2-3).

Promotes the ephemeral http.server the cross-host runners spin up
(EVIDENCE/proofs/g5_*_runner.py `_serve`) into a real, deployable service: a
standing endpoint that serves the committed published hash record over HTTP (dev)
or HTTPS (real transport, via `uvicorn --ssl-*`). It is the publisher node of the
gate -> target -> publisher chain.

The record served is EVIDENCE/published_hashes.json (the committed, hash-locked
record; CANON/canon.lock -> published_hashes.json -> the pinned root anchor the
target holds out-of-band). The bytes are served verbatim so their sha256 equals
the anchor the target was configured with (published_source.anchor_sha256). The
path served is /published_hashes.json, matching the URL a target's
ELYON_PUBLISHER_URL points at and the `_REQUIRED_RECORD_KEYS` the fetch side
anchor-verifies.

No new canonical invariant (canon section 14): serving the record is verification
I/O; the publisher decides nothing and executes nothing. Trust is NOT placed in
the transport - the target anchor-verifies the fetched bytes against its pinned
root (published_source.load_record_from_bytes), so a substituted or tampered
record fails closed regardless of how it was served. Secure distribution of the
pinned anchor itself remains the named G5 floor (Decision F).

Configuration (out-of-band, never hard-coded):
  ELYON_PUBLISHED_RECORD - path to the published record bytes to serve
                           (default: EVIDENCE/published_hashes.json, relative to
                           the working directory).

Deploy:  uvicorn IMPLEMENTATION.publisher:app --host 0.0.0.0 --port 9100 \
             --ssl-certfile <cert> --ssl-keyfile <key>

Ledger: VL-063 (T-G5-transport; multi-process + real-TLS chain, artifact 12 steps 2-3 in-env).
"""

import os

from fastapi import FastAPI, HTTPException, Response

PUBLISHED_RECORD_PATH = os.environ.get(
    "ELYON_PUBLISHED_RECORD", "EVIDENCE/published_hashes.json"
)

app = FastAPI(title="Elyon-Sol published-record publisher")


@app.get("/published_hashes.json")
def published_hashes():
    """Serve the committed published record bytes verbatim (so their sha256
    equals the target's pinned anchor). A missing record file is a fail-closed
    503 rather than a fabricated body."""
    try:
        with open(PUBLISHED_RECORD_PATH, "rb") as f:
            data = f.read()
    except OSError:
        raise HTTPException(status_code=503, detail="published record unavailable")
    return Response(content=data, media_type="application/json")


# Optional SIGNED published-record endpoint (VL-091, wiring B1). When a publisher
# signing key is configured, serve a freshly-signed record (live currency pins +
# a not_after window), re-signed per request so the served record is always
# fresh. A configured target in signed mode fetches THIS endpoint and refuses a
# stale record. Absent the signing key the endpoint 503s; the byte-anchor
# endpoint above is unchanged. The publisher PRIVATE key arrives by environment,
# never the repo.
ENV_PUBLISHER_SIGNING_KEY_HEX = "ELYON_PUBLISHER_SIGNING_KEY_HEX"
ENV_PUBLISHER_KEY_ID = "ELYON_PUBLISHER_KEY_ID"
ENV_RECORD_MAX_AGE = "ELYON_RECORD_MAX_AGE_SECONDS"


@app.get("/published_hashes_signed.json")
def published_hashes_signed():
    """Serve a freshly publisher-signed record (the live currency pins under a
    not_after window). 503 if no signing key is configured (the byte-anchor
    deployment). Fail-closed: any signing error is a 503, never a bad body."""
    import json as _json
    from datetime import datetime, timedelta, timezone

    key_hex = os.environ.get(ENV_PUBLISHER_SIGNING_KEY_HEX)
    key_id = os.environ.get(ENV_PUBLISHER_KEY_ID)
    if not (key_hex and key_id):
        raise HTTPException(status_code=503, detail="signed record not configured")
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from EVIDENCE.published_hashes_signed_gen import build_signed_record

        priv = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(key_hex))
        max_age = int(os.environ.get(ENV_RECORD_MAX_AGE, "300"))
        now = datetime.now(timezone.utc)
        record = build_signed_record(
            publisher_key_id=key_id,
            publisher_private_key=priv,
            serial=int(now.timestamp()),
            not_after=now + timedelta(seconds=max_age),
        )
    except Exception as exc:
        # The publisher is NOT a trust surface (the target signature- + freshness-verifies the
        # record regardless), so surfacing the cause here aids deployment debugging without
        # weakening the gate. Fail-closed 503.
        raise HTTPException(status_code=503, detail="signed record unavailable: %r" % exc)
    return Response(
        content=_json.dumps(record, ensure_ascii=True, sort_keys=True),
        media_type="application/json",
    )


# Optional SIGNED KEY-RECORD endpoint (SES-9a / K-01). Parity with the signed
# hash-record endpoint above: when a key-record ROOT signing key is configured,
# serve a freshly ROOT-signed KEY record (one gate-key entry under a record
# not_after window), re-signed per request so the served record is always fresh.
# A target/sidecar in signed key-record mode fetches THIS endpoint (or a synced
# copy) and enforces the gate key's revoked flag + validity window in-band. The
# ROOT PRIVATE key arrives by environment (the 0600 file on the publisher),
# never the repo. Absent the signing key -> 503 (parity with the hash endpoint).
#
# The published gate entry (id + public key) and its revoked flag come from env
# so revocation is an operational flip (set ELYON_KEY_RECORD_GATE_REVOKED=1 +
# restart) rather than a code change; the serial is int(now.timestamp()) so a
# restored record always carries a HIGHER serial than a revoked one (the
# consumer's monotonic high-water mark refuses a rollback for free).
ENV_KEY_RECORD_SIGNING_KEY_HEX = "ELYON_KEY_RECORD_SIGNING_KEY_HEX"
ENV_KEY_RECORD_ROOT_ID = "ELYON_KEY_RECORD_ROOT_ID"
ENV_KEY_RECORD_GATE_KEY_ID = "ELYON_KEY_RECORD_GATE_KEY_ID"
ENV_KEY_RECORD_GATE_PUBLIC_KEY_HEX = "ELYON_KEY_RECORD_GATE_PUBLIC_KEY_HEX"
ENV_KEY_RECORD_GATE_REVOKED = "ELYON_KEY_RECORD_GATE_REVOKED"
ENV_KEY_RECORD_KEY_MAX_AGE = "ELYON_KEY_RECORD_KEY_MAX_AGE_SECONDS"


@app.get("/published_keys_signed.json")
def published_keys_signed():
    """Serve a freshly ROOT-signed KEY record (one gate-key entry under a
    not_after freshness window, re-signed per request). 503 if no ROOT signing
    key is configured. Fail-closed: any signing error is a 503, never a bad
    body. Mirrors published_hashes_signed(); the publisher is not a trust
    surface (the consumer signature- + freshness-verifies against its pinned
    ROOT)."""
    import json as _json
    from datetime import datetime, timedelta, timezone

    root_hex = os.environ.get(ENV_KEY_RECORD_SIGNING_KEY_HEX)
    root_id = os.environ.get(ENV_KEY_RECORD_ROOT_ID)
    gate_key_id = os.environ.get(ENV_KEY_RECORD_GATE_KEY_ID)
    gate_pub_hex = os.environ.get(ENV_KEY_RECORD_GATE_PUBLIC_KEY_HEX)
    if not (root_hex and root_id and gate_key_id and gate_pub_hex):
        raise HTTPException(status_code=503, detail="signed key record not configured")
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
            Ed25519PublicKey,
        )
        from EVIDENCE.published_keys_gen import build_key_record, make_key_entry

        root_priv = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(root_hex))
        gate_pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(gate_pub_hex))
        revoked = os.environ.get(ENV_KEY_RECORD_GATE_REVOKED, "0") == "1"
        # Record freshness parity with the hash record; the KEY entry's own
        # lifecycle window is long (a key is valid for far longer than a record
        # is fresh) and configurable.
        record_max_age = int(os.environ.get(ENV_RECORD_MAX_AGE, "300"))
        key_max_age = int(os.environ.get(ENV_KEY_RECORD_KEY_MAX_AGE, str(365 * 24 * 3600)))
        now = datetime.now(timezone.utc)
        entry = make_key_entry(
            key_id=gate_key_id,
            public_key=gate_pub,
            not_before=now - timedelta(minutes=5),
            not_after=now + timedelta(seconds=key_max_age),
            revoked=revoked,
            revoked_at=(now if revoked else None),
            reason=("operational revocation" if revoked else None),
        )
        record = build_key_record(
            root_key_id=root_id,
            root_private_key=root_priv,
            keys=[entry],
            serial=int(now.timestamp()),
            not_after=now + timedelta(seconds=record_max_age),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="signed key record unavailable: %r" % exc)
    return Response(
        content=_json.dumps(record, ensure_ascii=True, sort_keys=True),
        media_type="application/json",
    )
