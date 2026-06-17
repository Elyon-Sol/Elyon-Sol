"""
F-01 tests: optional SIGNED-record (freshness) mode in the ext-authz sidecar
(VL-112; mirrors reference_target's signed mode, VL-091).

The byte-anchor record the sidecar consults by default has NO temporal dimension:
a stale-but-anchor-matching record is honored arbitrarily later (F-01 / A3b
sub-case (b)). Signed mode pins a publisher key and consults a LOCAL signed
record carrying serial + not_after, validated per request via
published_record_source.load_signed_record_from_bytes, so a stale or invalid
record fails closed. These tests prove: a fresh signed record is honored; a stale
one is refused (REF_VERIFY_PUBLISHED_RECORD_STALE); a tampered / wrong-key one is
refused (REF_VERIFY_PUBLISHED_RECORD_INVALID); the byte-anchor default path is
unchanged; and config_from_env reads/validates the signed-mode env fail-closed.

Envelopes are minted by the REAL gate (pep); the signed record is signed in-test
by a generated publisher Ed25519 key, matching the reader's canonicalization
(canonical_json over the record minus publisher_signature).
"""

import json
from datetime import timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
import IMPLEMENTATION.authz_sidecar as sidecar
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.published_source import anchor_sha256
from IMPLEMENTATION.authz_sidecar import (
    build_authz_sidecar_app, ENVELOPE_HEADER, INTERACTION_HEADER,
    DECISION_HEADER, REASON_HEADER, DECISION_ALLOW, DECISION_DENY,
)
from IMPLEMENTATION.reference_target import REF_TARGET_NOT_CONFIGURED
from IMPLEMENTATION.verifier import (
    REF_VERIFY_PUBLISHED_RECORD_STALE,
    REF_VERIFY_PUBLISHED_RECORD_INVALID,
)

TARGET_ID = "mcp://elyon-sol/tool-server"
RECORD_PATH = "EVIDENCE/published_hashes.json"
PUB_KEY_ID = "pub-test-1"
FAR_FUTURE = "2099-01-01T00:00:00+00:00"
PAST = "2000-01-01T00:00:00+00:00"


def _record_bytes():
    with open(RECORD_PATH, "rb") as f:
        return f.read()


def _admit(tool, args):
    class _R:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        return _R()

    orig = pep.requests.post
    pep.requests.post = fake_post
    try:
        r = TestClient(pep.app).post(
            "/governed-call",
            json={"target_url": TARGET_ID, "interaction": interaction_for(tool, args)},
        )
        assert r.status_code == 200, r.text
        return r.json()["envelope"]
    finally:
        pep.requests.post = orig


def _sign_record(priv, *, not_after, serial=1, tamper_after_sign=False,
                 key_id=PUB_KEY_ID):
    """Build a signed published record with the LIVE currency pins, signed the way
    the reader verifies it (canonical_json over the record minus the signature)."""
    pins = json.loads(_record_bytes())
    rec = {
        "format": "elyon-sol-published-record",
        "version": "1.0",
        "publisher_key_id": key_id,
        "serial": serial,
        "issued_at": "2026-06-17T00:00:00+00:00",
        "not_after": not_after,
        "canon_sha256": pins["canon_sha256"],
        "evaluator_sha256": pins["evaluator_sha256"],
        "manifest_sha256": pins["manifest_sha256"],
    }
    rec["publisher_signature"] = priv.sign(canonical_json(rec).encode("utf-8")).hex()
    if tamper_after_sign:
        rec["manifest_sha256"] = "0" * 64  # signature no longer covers the bytes
    return json.dumps(rec).encode("utf-8")


def _signed_config(gate_signing, pinned_pub_key, signed_bytes):
    rb = _record_bytes()
    return {
        "target_url": TARGET_ID,
        "record_bytes": rb,
        "pinned_root_sha256": anchor_sha256(rb),
        "pinned_public_keys": {gate_signing["key_id"]: gate_signing["public_key"]},
        "clock_skew": timedelta(0),
        "pinned_publisher_keys": {PUB_KEY_ID: pinned_pub_key},
        "signed_record_bytes": signed_bytes,
    }


def _byte_anchor_config(gate_signing):
    rb = _record_bytes()
    return {
        "target_url": TARGET_ID,
        "record_bytes": rb,
        "pinned_root_sha256": anchor_sha256(rb),
        "pinned_public_keys": {gate_signing["key_id"]: gate_signing["public_key"]},
        "clock_skew": timedelta(0),
    }


def _client(config):
    return TestClient(build_authz_sidecar_app(config_provider=lambda: config))


def _check(client, tool, args, env):
    headers = {
        ENVELOPE_HEADER: canonical_json(env),
        INTERACTION_HEADER: canonical_json(interaction_for(tool, args)),
    }
    return client.post("/authz", headers=headers)


# --------------------------------------------------------------------------- #
# Signed mode: honor a fresh record, refuse stale / invalid
# --------------------------------------------------------------------------- #

def test_signed_mode_allows_fresh_record(gate_signing):
    priv = Ed25519PrivateKey.generate()
    signed = _sign_record(priv, not_after=FAR_FUTURE)
    client = _client(_signed_config(gate_signing, priv.public_key(), signed))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW
    assert r.headers[REASON_HEADER] == "REASSERTED_AND_BOUND"


def test_signed_mode_refuses_stale_record(gate_signing):
    """A signed record past its not_after -> STALE, fail closed. This is the
    freshness the byte-anchor mode cannot provide (the record's bytes still hash
    fine; it is simply too old)."""
    priv = Ed25519PrivateKey.generate()
    signed = _sign_record(priv, not_after=PAST)
    client = _client(_signed_config(gate_signing, priv.public_key(), signed))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 403
    assert r.headers[DECISION_HEADER] == DECISION_DENY
    assert r.headers[REASON_HEADER] == REF_VERIFY_PUBLISHED_RECORD_STALE


def test_signed_mode_refuses_tampered_record(gate_signing):
    """A record mutated after signing -> publisher signature fails -> INVALID."""
    priv = Ed25519PrivateKey.generate()
    signed = _sign_record(priv, not_after=FAR_FUTURE, tamper_after_sign=True)
    client = _client(_signed_config(gate_signing, priv.public_key(), signed))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_PUBLISHED_RECORD_INVALID


def test_signed_mode_refuses_wrong_publisher_key(gate_signing):
    """A record signed by a key other than the pinned one -> INVALID."""
    signer = Ed25519PrivateKey.generate()
    other = Ed25519PrivateKey.generate()
    signed = _sign_record(signer, not_after=FAR_FUTURE)
    client = _client(_signed_config(gate_signing, other.public_key(), signed))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_PUBLISHED_RECORD_INVALID


# --------------------------------------------------------------------------- #
# Byte-anchor default unchanged (no publisher key)
# --------------------------------------------------------------------------- #

def test_byte_anchor_default_still_allows(gate_signing):
    """No publisher key configured -> the unchanged byte-anchor path honors a
    valid attested request (build-then-wire: the default is untouched)."""
    client = _client(_byte_anchor_config(gate_signing))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


# --------------------------------------------------------------------------- #
# config_from_env signed-mode resolution / fail-closed
# --------------------------------------------------------------------------- #

def _set_required_env(monkeypatch, tmp_path):
    rb = _record_bytes()
    rec_file = tmp_path / "published_hashes.json"
    rec_file.write_bytes(rb)
    monkeypatch.setenv(sidecar.ENV_TARGET_URL, TARGET_ID)
    monkeypatch.setenv(sidecar.ENV_RECORD_PATH, str(rec_file))
    monkeypatch.setenv(sidecar.ENV_PINNED_ROOT, anchor_sha256(rb))
    monkeypatch.setenv(sidecar.ENV_GATE_KEY_ID, "gate-1")
    monkeypatch.setenv(
        sidecar.ENV_GATE_PUBLIC_KEY_HEX,
        Ed25519PrivateKey.generate().public_key().public_bytes_raw().hex(),
    )
    return rec_file


def test_config_from_env_signed_mode_resolves(monkeypatch, tmp_path):
    _set_required_env(monkeypatch, tmp_path)
    priv = Ed25519PrivateKey.generate()
    signed_file = tmp_path / "published_hashes_signed.json"
    signed_file.write_bytes(_sign_record(priv, not_after=FAR_FUTURE))
    monkeypatch.setenv(sidecar.ENV_PUBLISHER_KEY_ID, PUB_KEY_ID)
    monkeypatch.setenv(
        sidecar.ENV_PUBLISHER_KEY_HEX, priv.public_key().public_bytes_raw().hex()
    )
    monkeypatch.setenv(sidecar.ENV_SIGNED_RECORD_PATH, str(signed_file))
    config = sidecar.config_from_env()
    assert config is not None
    assert PUB_KEY_ID in config["pinned_publisher_keys"]
    assert config["signed_record_bytes"] == signed_file.read_bytes()


def test_config_from_env_signed_mode_malformed_pub_key_returns_none(monkeypatch, tmp_path):
    _set_required_env(monkeypatch, tmp_path)
    monkeypatch.setenv(sidecar.ENV_PUBLISHER_KEY_ID, PUB_KEY_ID)
    monkeypatch.setenv(sidecar.ENV_PUBLISHER_KEY_HEX, "not-hex")
    assert sidecar.config_from_env() is None


def test_config_from_env_signed_mode_missing_signed_file_returns_none(monkeypatch, tmp_path):
    _set_required_env(monkeypatch, tmp_path)
    priv = Ed25519PrivateKey.generate()
    monkeypatch.setenv(sidecar.ENV_PUBLISHER_KEY_ID, PUB_KEY_ID)
    monkeypatch.setenv(
        sidecar.ENV_PUBLISHER_KEY_HEX, priv.public_key().public_bytes_raw().hex()
    )
    monkeypatch.setenv(sidecar.ENV_SIGNED_RECORD_PATH, str(tmp_path / "nope.json"))
    assert sidecar.config_from_env() is None
