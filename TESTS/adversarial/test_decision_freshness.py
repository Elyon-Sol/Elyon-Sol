"""
Decision-freshness (A3b close) tests — the wedge's defining property.

A captured, validly-signed ELIGIBLE decision must NOT be honored arbitrarily later.
This pins the acceptance criterion: a default-path decision, verified beyond its
freshness window, is REFUSED. Mechanism: the gate stamps a signed `not_after`
(decision max-age) on the default ELIGIBLE forward; verify_envelope enforces it
(step 1.5b, the proven key-expiry primitive applied to the decision). Canon-safe:
verification-layer policy, no new CCS invariant, no reassert() change.

Ledger: VL-065 (T-G5-continuity; decision freshness / A3b close).
"""

from datetime import datetime, timezone, timedelta

from fastapi.testclient import TestClient

from IMPLEMENTATION.pep import app as pep_app
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.verifier import (
    verify_envelope,
    ACCEPT_REASSERTED_AND_BOUND,
    REF_VERIFY_SIGNATURE_EXPIRED,
)

TARGET = "http://127.0.0.1:9000/target"


def _interaction():
    return {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }


def _drive_gate(monkeypatch):
    """Drive the real default ELIGIBLE path; capture the signed envelope it returns."""
    class _R:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        return _R()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)
    c = TestClient(pep_app)
    r = c.post("/governed-call", json={"target_url": TARGET, "interaction": _interaction()})
    assert r.status_code == 200, r.text
    return r.json()["envelope"]


def test_default_decision_honored_when_fresh(gate_signing, monkeypatch):
    env = _drive_gate(monkeypatch)
    pinned = {gate_signing["key_id"]: gate_signing["public_key"]}
    res = verify_envelope(env, _interaction(), TARGET, pinned_public_keys=pinned,
                          now=datetime.now(timezone.utc))
    assert res["accepted"] is True
    assert res["reason"] == ACCEPT_REASSERTED_AND_BOUND


def test_default_decision_refused_when_stale(gate_signing, monkeypatch):
    """A3b: the SAME signed decision, presented far beyond its freshness window,
    must be refused — not honored as it is today."""
    env = _drive_gate(monkeypatch)
    pinned = {gate_signing["key_id"]: gate_signing["public_key"]}
    later = datetime.now(timezone.utc) + timedelta(days=3650)
    res = verify_envelope(env, _interaction(), TARGET, pinned_public_keys=pinned, now=later)
    assert res["accepted"] is False, "A3b OPEN: a stale signed decision is still honored"
    assert res["reason"] == REF_VERIFY_SIGNATURE_EXPIRED
