"""
B1 wiring tests (docs/restructure/23_published_record_freshness_wiring_spec.md, VL-091).

The reference target's SIGNED consult mode: with a pinned publisher key it fetches the
freshness-checked signed record and refuses a STALE/INVALID one (closing A3b sub-case (b)), while
the byte-anchor mode (no publisher key) is unchanged. signed_fetch is injected so these stay
network-free; the publisher's real signed endpoint is exercised separately.
"""

import json
import os
import uuid

from fastapi.testclient import TestClient

from IMPLEMENTATION.envelope import build_envelope, sign_envelope, canonical_json
from IMPLEMENTATION.evaluator import load_manifest, manifest_sha256
from IMPLEMENTATION.published_source import anchor_sha256
from IMPLEMENTATION.reference_target import build_reference_target_app
from IMPLEMENTATION.verifier import (
    REF_VERIFY_PUBLISHED_RECORD_STALE,
    REF_VERIFY_PUBLISHED_RECORD_INVALID,
)

TARGET_URL = "http://tool-server.test/target"
PUBLISHED = "EVIDENCE/published_hashes.json"


def _published_bytes():
    return open(PUBLISHED, "rb").read()


def _interaction():
    return {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0", "expected_manifest_sha256": manifest_sha256(),
    }


def _signed_envelope(gate_signing, interaction):
    env = build_envelope(
        decision="ELIGIBLE", target_url=TARGET_URL, normalized_interaction=interaction,
        manifest=load_manifest(), ac3=True, t26=True, manifest_integrity=True,
        timestamp_utc="2026-06-09T00:00:00+00:00",
    )
    return sign_envelope(env, gate_signing["private_key"], gate_signing["key_id"],
                         decision_id=uuid.uuid4().hex)


def _signed_mode_client(gate_signing, signed_fetch):
    config = {
        "target_url": TARGET_URL,
        "publisher_url": "http://publisher.test/published_hashes.json",
        "pinned_root_sha256": anchor_sha256(_published_bytes()),
        "pinned_public_keys": {gate_signing["key_id"]: gate_signing["public_key"]},
        "pinned_publisher_keys": {"pub-1": gate_signing["public_key"]},  # any; signed_fetch injected
        "signed_record_url": "http://publisher.test/published_hashes_signed.json",
    }
    app = build_reference_target_app(config_provider=lambda: config, signed_fetch=signed_fetch)
    return TestClient(app)


def _post(client, interaction, envelope):
    headers = {"X-Elyon-Sol-Envelope": canonical_json(envelope)} if envelope else {}
    return client.post("/target", json=interaction, headers=headers)


def test_signed_mode_honors_a_fresh_record(gate_signing):
    # The validated signed record carries the live currency pins -> reassert honors.
    fresh = {"record": json.loads(_published_bytes()), "reason": None}
    client = _signed_mode_client(gate_signing, lambda *a, **k: fresh)
    interaction = _interaction()
    r = _post(client, interaction, _signed_envelope(gate_signing, interaction))
    assert r.status_code == 200, r.text
    assert r.json()["honored"] is True


def test_signed_mode_refuses_a_stale_record(gate_signing):
    stale = {"record": None, "reason": REF_VERIFY_PUBLISHED_RECORD_STALE}
    client = _signed_mode_client(gate_signing, lambda *a, **k: stale)
    interaction = _interaction()
    r = _post(client, interaction, _signed_envelope(gate_signing, interaction))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_PUBLISHED_RECORD_STALE


def test_signed_mode_refuses_an_invalid_record(gate_signing):
    invalid = {"record": None, "reason": REF_VERIFY_PUBLISHED_RECORD_INVALID}
    client = _signed_mode_client(gate_signing, lambda *a, **k: invalid)
    interaction = _interaction()
    r = _post(client, interaction, _signed_envelope(gate_signing, interaction))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_PUBLISHED_RECORD_INVALID


def test_publisher_serves_a_reader_valid_signed_record(gate_signing):
    # The publisher's /published_hashes_signed.json signs the live pins; the reader validates it.
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import IMPLEMENTATION.publisher as publisher
    from IMPLEMENTATION.published_record_source import load_signed_record_from_bytes

    priv = Ed25519PrivateKey.generate()
    os.environ["ELYON_PUBLISHER_SIGNING_KEY_HEX"] = priv.private_bytes_raw().hex()
    os.environ["ELYON_PUBLISHER_KEY_ID"] = "pub-1"
    try:
        r = TestClient(publisher.app).get("/published_hashes_signed.json")
        assert r.status_code == 200
        res = load_signed_record_from_bytes(r.content, {"pub-1": priv.public_key()})
        assert res["reason"] is None
        assert "evaluator_sha256" in res["record"]
    finally:
        del os.environ["ELYON_PUBLISHER_SIGNING_KEY_HEX"]
        del os.environ["ELYON_PUBLISHER_KEY_ID"]


def test_publisher_signed_endpoint_503_without_key(gate_signing):
    import IMPLEMENTATION.publisher as publisher
    os.environ.pop("ELYON_PUBLISHER_SIGNING_KEY_HEX", None)
    r = TestClient(publisher.app).get("/published_hashes_signed.json")
    assert r.status_code == 503
