"""
SES-9a: tests for the SIGNED KEY-RECORD publisher endpoint
(/published_keys_signed.json in IMPLEMENTATION.publisher).

Parity with the signed hash-record endpoint (published_hashes_signed): when a
key-record ROOT signing key + gate entry are configured, the endpoint serves a
freshly ROOT-signed KEY record, re-signed per request. These tests prove:

  - unconfigured  -> 503 (fail-closed, no fabricated body);
  - configured    -> the served bytes VALIDATE against the pinned ROOT via the
                     real reader (load_key_record_from_bytes), the gate key is
                     in the trust view, revoked=False;
  - revoked flip  -> ELYON_KEY_RECORD_GATE_REVOKED=1 yields a record whose gate
                     entry validates with revoked=True (the in-band drill);
  - serial        -> monotonic (int(now.timestamp())), so a restore always
                     carries a higher serial than a revoke.

The ROOT keypair is generated in-test; the reader pins the ROOT PUBLIC key,
matching the canonicalization the gen side signs over.
"""

import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi.testclient import TestClient

import IMPLEMENTATION.publisher as publisher
from IMPLEMENTATION.key_record_source import load_key_record_from_bytes

ROOT_ID = "root-test-1"
GATE_KEY_ID = "gate-test-1"


def _fresh_env(monkeypatch, revoked="0"):
    root_priv = Ed25519PrivateKey.generate()
    gate_priv = Ed25519PrivateKey.generate()
    gate_pub_hex = gate_priv.public_key().public_bytes(
        Encoding.Raw, PublicFormat.Raw
    ).hex()
    monkeypatch.setenv("ELYON_KEY_RECORD_SIGNING_KEY_HEX",
                       root_priv.private_bytes_raw().hex())
    monkeypatch.setenv("ELYON_KEY_RECORD_ROOT_ID", ROOT_ID)
    monkeypatch.setenv("ELYON_KEY_RECORD_GATE_KEY_ID", GATE_KEY_ID)
    monkeypatch.setenv("ELYON_KEY_RECORD_GATE_PUBLIC_KEY_HEX", gate_pub_hex)
    monkeypatch.setenv("ELYON_KEY_RECORD_GATE_REVOKED", revoked)
    return root_priv, gate_pub_hex


def test_unconfigured_is_503(monkeypatch):
    for var in ("ELYON_KEY_RECORD_SIGNING_KEY_HEX", "ELYON_KEY_RECORD_ROOT_ID",
                "ELYON_KEY_RECORD_GATE_KEY_ID",
                "ELYON_KEY_RECORD_GATE_PUBLIC_KEY_HEX"):
        monkeypatch.delenv(var, raising=False)
    client = TestClient(publisher.app)
    assert client.get("/published_keys_signed.json").status_code == 503


def test_served_record_validates_and_honors_gate_key(monkeypatch):
    root_priv, _ = _fresh_env(monkeypatch, revoked="0")
    client = TestClient(publisher.app)
    resp = client.get("/published_keys_signed.json")
    assert resp.status_code == 200
    res = load_key_record_from_bytes(
        resp.content, {ROOT_ID: root_priv.public_key()}
    )
    assert res["reason"] is None, res
    assert GATE_KEY_ID in res["trust_view"]
    assert res["trust_view"][GATE_KEY_ID]["revoked"] is False


def test_revoked_flip_is_enforced_in_the_signed_record(monkeypatch):
    root_priv, _ = _fresh_env(monkeypatch, revoked="1")
    client = TestClient(publisher.app)
    resp = client.get("/published_keys_signed.json")
    assert resp.status_code == 200
    res = load_key_record_from_bytes(
        resp.content, {ROOT_ID: root_priv.public_key()}
    )
    # The record itself is well-formed and ROOT-signed; the gate entry carries
    # revoked=True, which the verifier consume-side turns into a live REFUSE.
    assert res["reason"] is None, res
    assert res["trust_view"][GATE_KEY_ID]["revoked"] is True


def test_wrong_root_pin_is_rejected(monkeypatch):
    _fresh_env(monkeypatch, revoked="0")
    client = TestClient(publisher.app)
    resp = client.get("/published_keys_signed.json")
    other_root = Ed25519PrivateKey.generate()
    res = load_key_record_from_bytes(
        resp.content, {ROOT_ID: other_root.public_key()}
    )
    assert res["trust_view"] is None
    assert res["reason"] is not None


def test_serial_is_monotonic_across_requests(monkeypatch):
    root_priv, _ = _fresh_env(monkeypatch, revoked="0")
    client = TestClient(publisher.app)
    r1 = client.get("/published_keys_signed.json")
    time.sleep(1.1)
    r2 = client.get("/published_keys_signed.json")
    s1 = load_key_record_from_bytes(r1.content, {ROOT_ID: root_priv.public_key()})["serial"]
    s2 = load_key_record_from_bytes(r2.content, {ROOT_ID: root_priv.public_key()})["serial"]
    assert s2 > s1
