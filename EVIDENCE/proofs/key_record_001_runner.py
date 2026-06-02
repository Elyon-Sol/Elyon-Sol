"""
B-prime-2 key-record killer-property runner (VL-042). Repo path:
EVIDENCE/proofs/key_record_001_runner.py.

Reproduces the increment's definition of done with LIVE keypairs (g3/signing
runner format): a current issuer key is HONORED, a REVOKED key is refused
instantly, and a STALE key record is refused. Run from the repo root
(build_envelope reads CANON/canon.lock, MANIFEST/manifest.json,
IMPLEMENTATION/evaluator.py). Exits 0 iff every expected outcome holds.

Records are built inline (structure-identical to
EVIDENCE/published_keys_gen.py::build_key_record) so the runner does not depend
on EVIDENCE/ being an importable package. The root and issuer PRIVATE keys are
generated live and never persisted.
"""

import base64
import json
import sys
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from IMPLEMENTATION.envelope import build_envelope, sign_envelope, canonical_json
from IMPLEMENTATION.key_record_source import load_key_record_from_bytes
from IMPLEMENTATION.verifier import (
    verify_envelope,
    ACCEPT_REASSERTED_AND_BOUND,
    REF_VERIFY_KEY_RECORD_STALE,
    REF_VERIFY_KEY_REVOKED,
)

NOW = datetime.now(timezone.utc)
ROOT_ID = "root-runner-1"
TARGET_URL = "https://example.test/hook"


def _pub_b64(public_key):
    raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def _interaction():
    return {
        "AP": ["auth.read"],
        "OP": ["op.forward"],
        "context": {"tenant": "t1"},
        "expected_manifest_version": "1",
        "expected_manifest_sha256": "pinned-manifest-sha-placeholder",
    }


def _signed_envelope(issuer_private, key_id):
    interaction = _interaction()
    env = build_envelope(
        decision="ELIGIBLE",
        target_url=TARGET_URL,
        normalized_interaction=interaction,
        manifest={"version": "0.9.8.4"},
        ac3=True,
        t26=True,
        manifest_integrity=True,
    )
    return sign_envelope(env, issuer_private, key_id), interaction


def _key_entry(key_id, public_key, revoked=False):
    nb = (NOW - timedelta(days=1)).isoformat()
    na = (NOW + timedelta(days=365)).isoformat()
    entry = {
        "key_id": key_id,
        "public_key": _pub_b64(public_key),
        "not_before": nb,
        "not_after": na,
        "revoked": revoked,
    }
    if revoked:
        entry["revoked_at"] = NOW.isoformat()
        entry["reason"] = "runner: compromised key"
    return entry


def _record_bytes(root_private, key_entries, serial, record_not_after):
    record = {
        "format": "elyon-sol-key-record",
        "version": 1,
        "root_key_id": ROOT_ID,
        "serial": serial,
        "issued_at": NOW.isoformat(),
        "not_after": record_not_after.isoformat(),
        "keys": list(key_entries),
    }
    record["publisher_signature"] = root_private.sign(
        canonical_json(record).encode("utf-8")
    ).hex()
    return json.dumps(record).encode("utf-8")


def main():
    root = Ed25519PrivateKey.generate()
    issuer = Ed25519PrivateKey.generate()
    pinned_root = {ROOT_ID: root.public_key()}
    fresh_until = NOW + timedelta(hours=24)
    checks = []

    # 1. current key honored
    raw = _record_bytes(root, [_key_entry("issuer-1", issuer.public_key())],
                        serial=1, record_not_after=fresh_until)
    loaded = load_key_record_from_bytes(raw, pinned_root, now=NOW)
    signed, interaction = _signed_envelope(issuer, "issuer-1")
    res = verify_envelope(signed, interaction, TARGET_URL,
                        key_record_view=loaded["trust_view"], now=NOW)
    ok = loaded["reason"] is None and res["reason"] == ACCEPT_REASSERTED_AND_BOUND
    checks.append(("current key honored", ok, res["reason"]))

    # 2. revoked key refused INSTANTLY (the detected-compromise kill)
    raw = _record_bytes(root, [_key_entry("issuer-1", issuer.public_key(),
                                        revoked=True)],
                        serial=2, record_not_after=fresh_until)
    loaded = load_key_record_from_bytes(raw, pinned_root, now=NOW)
    signed, interaction = _signed_envelope(issuer, "issuer-1")
    res = verify_envelope(signed, interaction, TARGET_URL,
                        key_record_view=loaded["trust_view"], now=NOW)
    ok = (not res["accepted"]) and res["reason"] == REF_VERIFY_KEY_REVOKED
    checks.append(("revoked key refused", ok, res["reason"]))

    # 3. stale key record refused (the freshness recursion)
    raw = _record_bytes(root, [_key_entry("issuer-1", issuer.public_key())],
                        serial=1, record_not_after=NOW - timedelta(hours=1))
    loaded = load_key_record_from_bytes(raw, pinned_root, now=NOW)
    ok = loaded["trust_view"] is None and loaded["reason"] == REF_VERIFY_KEY_RECORD_STALE
    checks.append(("stale record refused", ok, loaded["reason"]))

    all_ok = True
    for label, passed, reason in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_ok = False
        print("[%s] %s (reason=%s)" % (status, label, reason))

    print("RESULT: %s" % ("all checks passed" if all_ok else "FAILURES present"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
