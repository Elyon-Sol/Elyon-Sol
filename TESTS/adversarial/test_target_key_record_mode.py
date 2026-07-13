"""SES-9a (K-01, VL-110): signed key-record mode ON THE ENFORCE PATH.

The verifier has had a key_record_view branch since VL-042 (issuer-key
revocation + validity window, record-exclusive), but every enforce surface
passed the static pin only, so revoking a compromised gate key required an
out-of-band re-pin on every consumer. SES-9a threads the publisher-signed key
record (IMPLEMENTATION/key_record_source.py) onto the three enforce surfaces -
ExecutorGate (executor_sdk.py), the reference enforcing target
(reference_target.py, ELYON_KEY_RECORD_URL trio), and the ext-authz sidecar
(authz_sidecar.py, ELYON_KEY_RECORD_PATH trio) - default-off / build-then-wire.

Every test here drives the REAL surface (the target handler over TestClient,
the real ExecutorGate.check, the real sidecar app from env config) and the REAL
reader (load_key_record_from_bytes via an injected transport, the same seam the
SES-8 signed_fetch tests use). Key records are built inline, byte-identical in
structure to EVIDENCE/published_keys_gen.build_key_record output (same signed
region: canonical_json(record minus publisher_signature)), the
test_key_record.py pattern.

REVERT-CATCHER (test_revoked_gate_key_refused_at_target): if the wiring is
reverted - the target passes pinned_public_keys instead of the validated
key_record_view - a validly-signed envelope from a REVOKED key is honored
again and the test goes RED.
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi.testclient import TestClient

from IMPLEMENTATION.envelope import build_envelope, sign_envelope, canonical_json
from IMPLEMENTATION.evaluator import load_manifest, manifest_sha256
from IMPLEMENTATION.executor_sdk import ExecutorGate
from IMPLEMENTATION.key_record_source import load_key_record_from_bytes
from IMPLEMENTATION.published_source import anchor_sha256
from IMPLEMENTATION.reference_target import build_reference_target_app
from IMPLEMENTATION.replay_cache import InMemoryReplayCache
from IMPLEMENTATION.authz_sidecar import (
    build_authz_sidecar_app,
    DECISION_HEADER,
    REASON_HEADER,
    DECISION_ALLOW,
    DECISION_DENY,
    ENVELOPE_HEADER as SIDECAR_ENVELOPE_HEADER,
    INTERACTION_HEADER,
)
from IMPLEMENTATION.reference_target import (
    ENVELOPE_HEADER,
    REF_TARGET_NOT_CONFIGURED,
)
from IMPLEMENTATION.verifier import (
    ACCEPT_REASSERTED_AND_BOUND,
    REF_VERIFY_KEY_RECORD_INVALID,
    REF_VERIFY_KEY_RECORD_STALE,
    REF_VERIFY_KEY_REVOKED,
    REF_VERIFY_KEY_OUT_OF_WINDOW,
    REF_VERIFY_ROOT_REVOKED,
    REF_VERIFY_ROOT_RETIRED,
    REF_VERIFY_SIGNATURE_UNKNOWN_KEY,
)

TARGET = "https://target.elyon-sol.io:9443/target"
KID = "gate-ed25519-001"
ROOT_ID = "root-ed25519-001"

ISSUER_PRIV = Ed25519PrivateKey.generate()
ROOT_PRIV = Ed25519PrivateKey.generate()


# --------------------------------------------------------------------------- #
# Helpers (the SES-8 test_fix_serial_rollback pattern: real envelope, real
# manifest/canon from disk, injected transport)
# --------------------------------------------------------------------------- #

def _pub_b64(public_key):
    raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def _pub_hex(public_key):
    return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def inter():
    return {"AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
            "expected_manifest_version": "1.0",
            "expected_manifest_sha256": manifest_sha256()}


def signed_env(did, priv=ISSUER_PRIV, kid=KID):
    e = build_envelope(decision="ELIGIBLE", target_url=TARGET,
                       normalized_interaction=inter(), manifest=load_manifest(),
                       ac3=True, t26=True, manifest_integrity=True,
                       timestamp_utc="2026-07-13T00:00:00+00:00")
    return sign_envelope(e, priv, kid, decision_id=did)


_e0 = signed_env("d-pins")
PINS = {"canon_sha256": _e0["canon"]["canon_sha256"],
        "evaluator_sha256": _e0["evaluator"]["evaluator_sha256"],
        "manifest_sha256": _e0["evaluated_against"]["manifest_sha256"]}


def _now():
    return datetime.now(timezone.utc)


def _key_entry(kid=KID, public_key=None, not_before=None, not_after=None,
               revoked=False, role=None):
    if public_key is None:
        public_key = ISSUER_PRIV.public_key()
    if not_before is None:
        not_before = _now() - timedelta(days=1)
    if not_after is None:
        not_after = _now() + timedelta(days=365)
    entry = {"key_id": kid, "public_key": _pub_b64(public_key),
             "not_before": not_before.isoformat(),
             "not_after": not_after.isoformat(), "revoked": revoked}
    if role is not None:
        entry["role"] = role
    return entry


def kr_bytes(entries=None, serial=1, record_not_after=None, tamper=False):
    """Inline signed key record, byte-identical in structure to
    published_keys_gen.build_key_record (signed region: canonical_json of the
    record minus publisher_signature)."""
    if entries is None:
        entries = [_key_entry()]
    if record_not_after is None:
        record_not_after = _now() + timedelta(hours=24)
    record = {"format": "elyon-sol-key-record", "version": 1,
              "root_key_id": ROOT_ID, "serial": serial,
              "issued_at": _now().isoformat(),
              "not_after": record_not_after.isoformat(), "keys": list(entries)}
    message = canonical_json(record).encode("utf-8")
    record["publisher_signature"] = ROOT_PRIV.sign(message).hex()
    if tamper:
        record["serial"] = record["serial"] + 1  # break the signed region
    return json.dumps(record).encode("utf-8")


def make_target(key_record=True, kr_state=None):
    """Reference target in BYTE-ANCHOR hash-record mode (the unchanged base),
    plus SES-9a signed key-record mode when key_record=True. The injected
    key_record_fetch drives the REAL reader (load_key_record_from_bytes) over
    the state's bytes - the same injection seam the F-01/SES-8 signed_fetch
    tests use for the hash record."""
    if kr_state is None:
        kr_state = {"bytes": kr_bytes()}
    kr_state.setdefault("seen", [])
    kr_state.setdefault("calls", 0)

    cfg = {"target_url": TARGET, "publisher_url": "http://pub",
           "pinned_root_sha256": "x",
           "pinned_public_keys": {KID: ISSUER_PRIV.public_key()}}
    if key_record:
        cfg["key_record_url"] = "http://pub/keys"
        cfg["pinned_key_record_roots"] = {ROOT_ID: ROOT_PRIV.public_key()}

    def kr_fetch(url, roots, now=None, last_seen_serial=None,
                 root_status_view=None, timeout=10, clock_skew=timedelta(0)):
        kr_state["calls"] += 1
        kr_state["seen"].append(last_seen_serial)
        return load_key_record_from_bytes(
            kr_state["bytes"], roots, now=now,
            last_seen_serial=last_seen_serial,
            root_status_view=kr_state.get("root_status_view"),
            clock_skew=clock_skew)

    app = build_reference_target_app(
        config_provider=lambda: cfg,
        fetch=lambda url, root: dict(PINS),
        replay_cache=InMemoryReplayCache(),
        key_record_fetch=kr_fetch)
    return TestClient(app), kr_state


def post(client, env):
    return client.post("/target", json=inter(),
                       headers={ENVELOPE_HEADER: json.dumps(env)})


def acted(client):
    return client.get("/received").json()["count"]


# --------------------------------------------------------------------------- #
# 1. Default off = byte-identical (the revert-safety anchor)
# --------------------------------------------------------------------------- #

def test_default_off_static_pin_path_unchanged():
    """No key-record config -> the static pin still decides: a valid envelope
    is honored, an unknown-key envelope is refused, and the key-record
    transport is NEVER consulted."""
    client, st = make_target(key_record=False)
    assert post(client, signed_env("d1")).status_code == 200
    assert acted(client) == 1
    stranger = Ed25519PrivateKey.generate()
    r = post(client, signed_env("d2", priv=stranger, kid="unpinned-key"))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_SIGNATURE_UNKNOWN_KEY
    assert acted(client) == 1
    assert st["calls"] == 0  # default-off never touches the key-record hop


def test_partial_env_trio_fails_closed(monkeypatch):
    """A partially-set ELYON_KEY_RECORD_* trio is a config error -> the target
    fails closed (REF_TARGET_NOT_CONFIGURED), never a silent downgrade to the
    static pin."""
    from IMPLEMENTATION.reference_target import config_from_env
    monkeypatch.setenv("ELYON_TARGET_URL", TARGET)
    monkeypatch.setenv("ELYON_PUBLISHER_URL", "http://pub")
    monkeypatch.setenv("ELYON_PINNED_ROOT_SHA256", "x")
    monkeypatch.setenv("ELYON_GATE_KEY_ID", KID)
    monkeypatch.setenv("ELYON_GATE_PUBLIC_KEY_HEX", _pub_hex(ISSUER_PRIV.public_key()))
    assert config_from_env() is not None            # base config resolves
    monkeypatch.setenv("ELYON_KEY_RECORD_URL", "http://pub/keys")
    assert config_from_env() is None                # URL without root pin
    monkeypatch.setenv("ELYON_KEY_RECORD_ROOT_ID", ROOT_ID)
    monkeypatch.setenv("ELYON_KEY_RECORD_ROOT_HEX", "zz-not-hex")
    assert config_from_env() is None                # malformed root key
    monkeypatch.setenv("ELYON_KEY_RECORD_ROOT_HEX", _pub_hex(ROOT_PRIV.public_key()))
    cfg = config_from_env()
    assert cfg is not None and ROOT_ID in cfg["pinned_key_record_roots"]


# --------------------------------------------------------------------------- #
# 2. Revoked gate key refused (the whole point) - REVERT-CATCHER
# --------------------------------------------------------------------------- #

def test_revoked_gate_key_refused_at_target():
    """A validly-signed, otherwise-honorable envelope from a key the signed
    record marks REVOKED is refused and the target does NOT act.

    REVERT-CATCHER: revert the SES-9a wiring (pass pinned_public_keys instead
    of the key_record_view) and the static pin - which has no revoked flag -
    honors this envelope -> RED."""
    client, _ = make_target(kr_state={"bytes": kr_bytes([_key_entry(revoked=True)])})
    r = post(client, signed_env("d-revoked"))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_KEY_REVOKED
    assert acted(client) == 0


# --------------------------------------------------------------------------- #
# 3. Out-of-window key refused, skew-aware
# --------------------------------------------------------------------------- #

def test_out_of_window_key_refused_at_target():
    expired = _key_entry(not_before=_now() - timedelta(days=30),
                         not_after=_now() - timedelta(minutes=2))
    client, _ = make_target(kr_state={"bytes": kr_bytes([expired])})
    r = post(client, signed_env("d-window"))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_KEY_OUT_OF_WINDOW
    assert acted(client) == 0


def test_out_of_window_is_clock_skew_aware_at_gate():
    """VL-075 symmetry holds on the new path: a key 30s past not_after is
    refused strict but honored under a 60s configured tolerance."""
    now = _now()
    entry = _key_entry(not_before=now - timedelta(days=1),
                       not_after=now - timedelta(seconds=30))
    view = load_key_record_from_bytes(
        kr_bytes([entry]), {ROOT_ID: ROOT_PRIV.public_key()}, now=now)["trust_view"]
    assert view is not None
    strict = ExecutorGate(pinned_public_keys={KID: ISSUER_PRIV.public_key()},
                          target_id=TARGET, record_source=dict(PINS),
                          key_record_view=view)
    assert strict.check(signed_env("d-s1"), inter(), now=now) == \
        (False, REF_VERIFY_KEY_OUT_OF_WINDOW)
    tolerant = ExecutorGate(pinned_public_keys={KID: ISSUER_PRIV.public_key()},
                            target_id=TARGET, record_source=dict(PINS),
                            key_record_view=view,
                            clock_skew=timedelta(seconds=60))
    assert tolerant.check(signed_env("d-s2"), inter(), now=now).honored is True


# --------------------------------------------------------------------------- #
# 4. Stale / invalid key record fails closed - no downgrade to the static pin
# --------------------------------------------------------------------------- #

def test_stale_key_record_fails_closed_no_downgrade():
    """The SAME envelope the static pin would honor is refused when the
    configured key record is stale: fail closed, never a downgrade."""
    stale = {"bytes": kr_bytes(record_not_after=_now() - timedelta(seconds=1))}
    client, _ = make_target(kr_state=stale)
    r = post(client, signed_env("d-stale"))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_KEY_RECORD_STALE
    assert acted(client) == 0
    # contrast: identical envelope honored with the mode off (the refusal above
    # came from the key-record hop, not the envelope)
    off_client, _ = make_target(key_record=False)
    assert post(off_client, signed_env("d-stale-2")).status_code == 200


def test_invalid_key_record_fails_closed():
    client, _ = make_target(kr_state={"bytes": kr_bytes(tamper=True)})
    r = post(client, signed_env("d-tampered"))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_KEY_RECORD_INVALID
    assert acted(client) == 0


def test_key_record_serial_rollback_refused_at_target():
    """SES-8 parity on the key record: a rolled-back (lower-serial) but
    still-fresh record - which could resurrect a since-revoked key - is
    refused; the target threads its serial high-water mark into the fetch."""
    st = {"bytes": kr_bytes(serial=5)}
    client, _ = make_target(kr_state=st)
    assert post(client, signed_env("d-hw1")).status_code == 200
    assert st["seen"][-1] is None                    # first fetch: no mark yet
    st["bytes"] = kr_bytes(serial=3)                 # rollback, still fresh
    r = post(client, signed_env("d-hw2"))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_KEY_RECORD_STALE
    assert st["seen"][-1] == 5                       # the mark was threaded
    assert acted(client) == 1


# --------------------------------------------------------------------------- #
# 5. Root revoked / retired propagates through the enforce path
# --------------------------------------------------------------------------- #

def test_root_revoked_propagates_to_refuse():
    st = {"bytes": kr_bytes(),
          "root_status_view": {ROOT_ID: {"status": "revoked",
                                         "public_key": ROOT_PRIV.public_key()}}}
    client, _ = make_target(kr_state=st)
    r = post(client, signed_env("d-root-rev"))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_ROOT_REVOKED
    assert acted(client) == 0


def test_root_retired_refuses_new_record():
    st = {"bytes": kr_bytes(),  # issued_at = now >= retired_at -> NEW record
          "root_status_view": {ROOT_ID: {
              "status": "retired",
              "retired_at": _now() - timedelta(days=1),
              "public_key": ROOT_PRIV.public_key()}}}
    client, _ = make_target(kr_state=st)
    r = post(client, signed_env("d-root-ret"))
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == REF_VERIFY_ROOT_RETIRED
    assert acted(client) == 0


# --------------------------------------------------------------------------- #
# 6. Positive: fresh, in-window, non-revoked key honors end-to-end
# --------------------------------------------------------------------------- #

def test_fresh_record_key_honored_end_to_end():
    """Signed key-record mode honors a valid envelope exactly as the static
    pin does (equivalence on the accept path), acting exactly once."""
    client, st = make_target()
    r = post(client, signed_env("d-ok"))
    assert r.status_code == 200
    assert r.json() == {"honored": True, "reason": ACCEPT_REASSERTED_AND_BOUND}
    assert acted(client) == 1
    assert st["calls"] == 1  # the key record was actually consulted


# --------------------------------------------------------------------------- #
# ExecutorGate surface (the SDK seam integrators wire)
# --------------------------------------------------------------------------- #

def test_gate_key_record_source_called_per_check_and_fails_closed():
    state = {"bytes": kr_bytes(), "calls": 0}

    def source():
        state["calls"] += 1
        return load_key_record_from_bytes(state["bytes"],
                                          {ROOT_ID: ROOT_PRIV.public_key()})

    gate = ExecutorGate(pinned_public_keys={KID: ISSUER_PRIV.public_key()},
                        target_id=TARGET, record_source=dict(PINS),
                        key_record_source=source)
    assert gate.check(signed_env("d-g1"), inter()).honored is True
    assert state["calls"] == 1
    # the record goes stale between checks -> the NEXT check re-validates and
    # fails closed with the reader's reason (no caching of a stale view)
    state["bytes"] = kr_bytes(record_not_after=_now() - timedelta(seconds=1))
    assert gate.check(signed_env("d-g2"), inter()) == \
        (False, REF_VERIFY_KEY_RECORD_STALE)
    assert state["calls"] == 2


def test_gate_revoked_key_refused_via_static_view():
    view = load_key_record_from_bytes(
        kr_bytes([_key_entry(revoked=True)]),
        {ROOT_ID: ROOT_PRIV.public_key()})["trust_view"]
    gate = ExecutorGate(pinned_public_keys={KID: ISSUER_PRIV.public_key()},
                        target_id=TARGET, record_source=dict(PINS),
                        key_record_view=view)
    assert gate.check(signed_env("d-g3"), inter()) == \
        (False, REF_VERIFY_KEY_REVOKED)


def test_gate_view_and_source_together_fail_loud():
    with pytest.raises(ValueError):
        ExecutorGate(pinned_public_keys={KID: ISSUER_PRIV.public_key()},
                     target_id=TARGET, record_source=dict(PINS),
                     key_record_view={}, key_record_source=lambda: {})


# --------------------------------------------------------------------------- #
# Sidecar surface (env-driven, LOCAL key-record file, per-request validation)
# --------------------------------------------------------------------------- #

def _sidecar_env(monkeypatch, tmp_path, kr_content=None, partial=False):
    record_bytes = json.dumps(PINS).encode("utf-8")
    record_path = tmp_path / "published_hashes.json"
    record_path.write_bytes(record_bytes)
    monkeypatch.setenv("ELYON_TARGET_URL", TARGET)
    monkeypatch.setenv("ELYON_RECORD_PATH", str(record_path))
    monkeypatch.setenv("ELYON_PINNED_ROOT_SHA256", anchor_sha256(record_bytes))
    monkeypatch.setenv("ELYON_GATE_KEY_ID", KID)
    monkeypatch.setenv("ELYON_GATE_PUBLIC_KEY_HEX", _pub_hex(ISSUER_PRIV.public_key()))
    kr_path = tmp_path / "published_keys.json"
    kr_path.write_bytes(kr_content if kr_content is not None else kr_bytes())
    monkeypatch.setenv("ELYON_KEY_RECORD_PATH", str(kr_path))
    monkeypatch.setenv("ELYON_KEY_RECORD_ROOT_ID", ROOT_ID)
    if not partial:
        monkeypatch.setenv("ELYON_KEY_RECORD_ROOT_HEX", _pub_hex(ROOT_PRIV.public_key()))
    return TestClient(build_authz_sidecar_app())


def _sidecar_post(client, env):
    return client.post("/authz", headers={
        SIDECAR_ENVELOPE_HEADER: canonical_json(env),
        INTERACTION_HEADER: canonical_json(inter()),
    })


def test_sidecar_revoked_key_denied(monkeypatch, tmp_path):
    client = _sidecar_env(monkeypatch, tmp_path,
                          kr_content=kr_bytes([_key_entry(revoked=True)]))
    r = _sidecar_post(client, signed_env("d-sc1"))
    assert r.status_code == 403
    assert r.headers[DECISION_HEADER] == DECISION_DENY
    assert r.headers[REASON_HEADER] == REF_VERIFY_KEY_REVOKED


def test_sidecar_fresh_key_record_allows(monkeypatch, tmp_path):
    client = _sidecar_env(monkeypatch, tmp_path)
    r = _sidecar_post(client, signed_env("d-sc2"))
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


def test_sidecar_partial_trio_fails_closed(monkeypatch, tmp_path):
    """Key-record path + root id WITHOUT the root hex -> config fails closed:
    every check is denied REF_TARGET_NOT_CONFIGURED, no static-pin downgrade."""
    client = _sidecar_env(monkeypatch, tmp_path, partial=True)
    r = _sidecar_post(client, signed_env("d-sc3"))
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_TARGET_NOT_CONFIGURED


def test_sidecar_stale_key_record_denies(monkeypatch, tmp_path):
    client = _sidecar_env(
        monkeypatch, tmp_path,
        kr_content=kr_bytes(record_not_after=_now() - timedelta(seconds=1)))
    r = _sidecar_post(client, signed_env("d-sc4"))
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_KEY_RECORD_STALE
