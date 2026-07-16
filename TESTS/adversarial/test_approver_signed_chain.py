"""
pep resolves approver trust IN-PROCESS from the pinned-root SIGNED key-record
chain, and labels it SIGNED_CHAIN provenance - the GL-01-refine (VL-124) fix.

Before this increment the load-bearing R1 resolution lived only in the deploy
shim, which INJECTED the map; pep could not tell a signed-chain map from any
other injected map, so the startup guard could only require injectedness, not
provenance. These tests drive pep's OWN resolver over a REAL publisher-signed key
record on disk (built with the production EVIDENCE.published_keys_gen +
IMPLEMENTATION.key_record_source + IMPLEMENTATION.approver_trust path), and prove:

  1. a record with an `approver`-role key -> pep resolves it, provenance SIGNED_CHAIN;
  2. a record with NO approver role -> empty map, still SIGNED_CHAIN (fail-closed G-06);
  3. a wrong pinned root -> empty map, still SIGNED_CHAIN (fail-closed);
  4. the trio unset -> falls through to STATIC_PIN / NONE (byte-compatible default);
  5. the startup guard PASSES a high-impact gate wired via the signed chain, and
     FAILS the same gate if the identical keys are merely INJECTED (the residual).

Repo path: TESTS/adversarial/test_approver_signed_chain.py.
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.governance_wiring import (
    assert_high_impact_wiring,
    APPROVER_PROV_SIGNED_CHAIN,
    APPROVER_PROV_INJECTED,
    APPROVER_PROV_STATIC_PIN,
    APPROVER_PROV_NONE,
)
from EVIDENCE.published_keys_gen import (
    build_key_record, make_key_entry, public_key_b64, write_key_record,
)

NOW = datetime.now(timezone.utc)
ROOT_ID = "root-test-1"
APPROVER_ID = "approver-test-1"
GATE_ID = "gate-test-1"


def _write_record(path, *, entries, root_priv, serial=1, root_id=ROOT_ID):
    record = build_key_record(
        root_key_id=root_id, root_private_key=root_priv, keys=entries,
        serial=serial, not_after=NOW + timedelta(days=30),
    )
    write_key_record(str(path), record)


def _approver_entry(pub, role="approver"):
    e = make_key_entry(APPROVER_ID, pub,
                       not_before=NOW - timedelta(minutes=5),
                       not_after=NOW + timedelta(days=365))
    if role is not None:
        e["role"] = role
    return e


def _set_trio(monkeypatch, record_path, root_priv, *, root_id=ROOT_ID):
    root_b64 = public_key_b64(root_priv.public_key())
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", None)  # ensure seam is off
    monkeypatch.setenv("ELYON_APPROVER_KEY_RECORD_PATH", str(record_path))
    monkeypatch.setenv("ELYON_PINNED_ROOT_KEY_ID", root_id)
    monkeypatch.setenv("ELYON_PINNED_ROOT_PUBKEY_B64", root_b64)
    monkeypatch.setenv("ELYON_SIGNING_KEY_ID", GATE_ID)


# --------------------------------------------------------------------------
# pep resolves the signed chain in-process, with SIGNED_CHAIN provenance
# --------------------------------------------------------------------------

def test_signed_chain_approver_resolves_with_provenance(tmp_path, monkeypatch):
    approver = Ed25519PrivateKey.generate()
    root = Ed25519PrivateKey.generate()
    rec = tmp_path / "key_record.json"
    _write_record(rec, entries=[_approver_entry(approver.public_key())], root_priv=root)
    _set_trio(monkeypatch, rec, root)

    keys, prov = pep._get_approver_keys_with_provenance()
    assert prov == APPROVER_PROV_SIGNED_CHAIN
    assert set(keys) == {APPROVER_ID}          # the approver-role key resolved
    # the resolved public key actually verifies that approver's signature
    sig = approver.sign(b"probe")
    keys[APPROVER_ID].verify(sig, b"probe")    # no raise == correct key material


def test_no_approver_role_fails_closed_but_stays_signed_chain(tmp_path, monkeypatch):
    # an issuer-role-only record: role-distinctness excludes it -> empty map.
    approver = Ed25519PrivateKey.generate()
    root = Ed25519PrivateKey.generate()
    rec = tmp_path / "key_record.json"
    _write_record(rec, entries=[_approver_entry(approver.public_key(), role="issuer")],
                  root_priv=root)
    _set_trio(monkeypatch, rec, root)

    keys, prov = pep._get_approver_keys_with_provenance()
    assert keys == {}                          # fail-closed: no approver-role key
    assert prov == APPROVER_PROV_SIGNED_CHAIN   # configured -> still the signed path


def test_wrong_pinned_root_fails_closed(tmp_path, monkeypatch):
    approver = Ed25519PrivateKey.generate()
    root = Ed25519PrivateKey.generate()
    other_root = Ed25519PrivateKey.generate()
    rec = tmp_path / "key_record.json"
    _write_record(rec, entries=[_approver_entry(approver.public_key())], root_priv=root)
    # pin a DIFFERENT root than the one that signed the record
    _set_trio(monkeypatch, rec, other_root)

    keys, prov = pep._get_approver_keys_with_provenance()
    assert keys == {}                          # signature does not verify -> empty
    assert prov == APPROVER_PROV_SIGNED_CHAIN


def test_tampered_record_fails_closed(tmp_path, monkeypatch):
    approver = Ed25519PrivateKey.generate()
    root = Ed25519PrivateKey.generate()
    rec = tmp_path / "key_record.json"
    _write_record(rec, entries=[_approver_entry(approver.public_key())], root_priv=root)
    doc = json.loads(rec.read_text())
    doc["keys"][0]["key_id"] = "attacker-swapped"   # mutate a signed field
    rec.write_text(json.dumps(doc))
    _set_trio(monkeypatch, rec, root)

    keys, prov = pep._get_approver_keys_with_provenance()
    assert keys == {}
    assert prov == APPROVER_PROV_SIGNED_CHAIN


def test_missing_record_file_fails_closed(tmp_path, monkeypatch):
    root = Ed25519PrivateKey.generate()
    _set_trio(monkeypatch, tmp_path / "does_not_exist.json", root)
    keys, prov = pep._get_approver_keys_with_provenance()
    assert keys == {}
    assert prov == APPROVER_PROV_SIGNED_CHAIN


# --------------------------------------------------------------------------
# provenance ordering: seam > signed-chain > static pin > none
# --------------------------------------------------------------------------

def test_static_pin_provenance_when_no_trio(monkeypatch):
    for var in ("ELYON_APPROVER_KEY_RECORD_PATH", "ELYON_PINNED_ROOT_KEY_ID",
                "ELYON_PINNED_ROOT_PUBKEY_B64"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", None)
    pub_hex = Ed25519PrivateKey.generate().public_key().public_bytes_raw().hex()
    monkeypatch.setenv("ELYON_APPROVER_KEY_ID", "pin-1")
    monkeypatch.setenv("ELYON_APPROVER_PUBKEY_HEX", pub_hex)
    keys, prov = pep._get_approver_keys_with_provenance()
    assert set(keys) == {"pin-1"}
    assert prov == APPROVER_PROV_STATIC_PIN


def test_none_provenance_when_nothing_configured(monkeypatch):
    for var in ("ELYON_APPROVER_KEY_RECORD_PATH", "ELYON_PINNED_ROOT_KEY_ID",
                "ELYON_PINNED_ROOT_PUBKEY_B64", "ELYON_APPROVER_KEY_ID",
                "ELYON_APPROVER_PUBKEY_HEX"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", None)
    keys, prov = pep._get_approver_keys_with_provenance()
    assert keys == {}
    assert prov == APPROVER_PROV_NONE


def test_injection_seam_wins_and_is_labelled_injected(monkeypatch):
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", {"x": object()})
    _, prov = pep._get_approver_keys_with_provenance()
    assert prov == APPROVER_PROV_INJECTED


# --------------------------------------------------------------------------
# End-to-end at the guard: signed-chain passes, the SAME keys injected fail
# --------------------------------------------------------------------------

HI = {"version": "1.0", "AR": ["identity", "role"], "R": ["session", "request"],
      "HIGH_IMPACT": ["role"]}


def test_guard_passes_signed_chain_fails_injected(tmp_path, monkeypatch):
    approver = Ed25519PrivateKey.generate()
    root = Ed25519PrivateKey.generate()
    rec = tmp_path / "key_record.json"
    _write_record(rec, entries=[_approver_entry(approver.public_key())], root_priv=root)
    _set_trio(monkeypatch, rec, root)

    keys, prov = pep._get_approver_keys_with_provenance()
    # signed-chain: the high-impact gate is allowed to start
    assert_high_impact_wiring(
        manifest=HI, approver_keys=keys, approver_provenance=prov,
        approval_log_configured=True, pending_redis_url=None, replay_redis_url=None,
    )
    # the SAME resolved keys, but presented as INJECTED, are refused at G-01 -
    # this is the residual GL-01-refine closes: injectedness is not provenance.
    with pytest.raises(RuntimeError) as e:
        assert_high_impact_wiring(
            manifest=HI, approver_keys=keys, approver_provenance=APPROVER_PROV_INJECTED,
            approval_log_configured=True, pending_redis_url=None, replay_redis_url=None,
        )
    assert "G-01" in str(e.value)


def test_real_pep_startup_hook_with_signed_chain_high_impact(tmp_path, monkeypatch):
    # Drive the REAL pep startup hook with a high-impact manifest + a signed-chain
    # approver map + a configured log + coherent stores: the gate starts.
    from fastapi.testclient import TestClient

    approver = Ed25519PrivateKey.generate()
    root = Ed25519PrivateKey.generate()
    rec = tmp_path / "key_record.json"
    _write_record(rec, entries=[_approver_entry(approver.public_key())], root_priv=root)
    _set_trio(monkeypatch, rec, root)

    monkeypatch.setattr(pep, "load_manifest", lambda: HI)
    monkeypatch.setattr(pep, "_get_approval_log", lambda: object())

    with TestClient(pep.app):
        pass  # startup hook ran without raising == the signed-chain gate is wired


def test_real_pep_startup_hook_refuses_static_pin_high_impact(tmp_path, monkeypatch):
    # Same high-impact manifest, but only the bare static pin: startup FAILS closed.
    from fastapi.testclient import TestClient

    for var in ("ELYON_APPROVER_KEY_RECORD_PATH", "ELYON_PINNED_ROOT_KEY_ID",
                "ELYON_PINNED_ROOT_PUBKEY_B64"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", None)
    pub_hex = Ed25519PrivateKey.generate().public_key().public_bytes_raw().hex()
    monkeypatch.setenv("ELYON_APPROVER_KEY_ID", "pin-1")
    monkeypatch.setenv("ELYON_APPROVER_PUBKEY_HEX", pub_hex)
    monkeypatch.setattr(pep, "load_manifest", lambda: HI)
    monkeypatch.setattr(pep, "_get_approval_log", lambda: object())

    with pytest.raises(RuntimeError) as e:
        with TestClient(pep.app):
            pass
    assert "G-01" in str(e.value)
