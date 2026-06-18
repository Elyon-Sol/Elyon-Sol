"""
Governance layer, Feature 1, increment 1c: the pep approval wiring.

Drives pep.governed_call over HTTP (TestClient) to pin the 202 PENDING_APPROVAL
state machine and the approved/refused legs. requires_approval is monkeypatched
to force the high-impact branch (impact classification itself is unit-tested in
test_requires_approval.py); these tests are about the WIRING - the H6 placement,
the H4 request binding + pending set, and the H3 single-use claim - and that the
default (non-high-impact) path is untouched.

The gate signing key is the autouse conftest `gate_signing` fixture
(key_id = gate-test-ed25519-001). The approver key is injected separately, with
a DIFFERENT key_id, so separation of duties holds.
"""

import json

import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat,
)

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.pep import app
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.approval import (
    build_grant, sign_grant,
    REF_APPROVAL_BINDING_MISMATCH, REF_APPROVAL_SOD, REF_APPROVAL_EXPIRED,
    REF_APPROVAL_REPLAY, REF_APPROVAL_REQUEST_UNKNOWN, REF_APPROVAL_KEY_UNKNOWN,
)
from datetime import datetime, timedelta, timezone

client = TestClient(app)
SHA = manifest_sha256()
TARGET = "https://upstream.example/highimpact"
APPROVER_KEY_ID = "approver-test-ed25519-001"


def _body():
    return {
        "target_url": TARGET,
        "interaction": {
            "AP": ["identity", "role"],
            "OP": ["session", "request"],
            "context": {},
            "expected_manifest_version": "1.0",
            "expected_manifest_sha256": SHA,
        },
    }


@pytest.fixture
def force_high_impact(monkeypatch):
    """Force requires_approval -> True so the high-impact branch is exercised
    regardless of the (empty) default HIGH_IMPACT manifest."""
    monkeypatch.setattr(pep, "requires_approval", lambda ctx, manifest: True)


@pytest.fixture
def approver(monkeypatch):
    """Inject a SEPARATE approver keypair (distinct key_id from the gate)."""
    sk = Ed25519PrivateKey.generate()
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", {APPROVER_KEY_ID: sk.public_key()})
    return sk


@pytest.fixture
def fresh_state(monkeypatch):
    """Isolate the module-level pending set + grant replay cache per test."""
    from IMPLEMENTATION.pep import _PendingApprovals
    from IMPLEMENTATION.replay_cache import InMemoryReplayCache
    monkeypatch.setattr(pep, "_PENDING", _PendingApprovals())
    monkeypatch.setattr(pep, "_GRANT_REPLAY", InMemoryReplayCache())


def _spy_post(monkeypatch):
    calls = []

    class R:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        calls.append(url)
        return R()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)
    return calls


def _hold(monkeypatch):
    """POST a high-impact call with no grant -> 202; return (request_id, decision_sha256)."""
    calls = _spy_post(monkeypatch)
    r = client.post("/governed-call", json=_body())
    assert r.status_code == 202
    assert calls == []  # never forwarded
    j = r.json()
    return j["approval_request_id"], j["decision_sha256"], calls


def _signed_grant(sk, decision_sha256, request_id, grant_id="grant-1",
                  not_after=None, key_id=APPROVER_KEY_ID):
    g = build_grant(
        decision_sha256=decision_sha256,
        approval_request_id=request_id,
        grant_id=grant_id,
        not_after=not_after or (datetime.now(timezone.utc) + timedelta(seconds=300)),
    )
    return sign_grant(g, sk, key_id)


def _resubmit(grant, monkeypatch):
    calls = _spy_post(monkeypatch)
    r = client.post(
        "/governed-call",
        json=_body(),
        headers={"X-Elyon-Sol-Approval-Grant": json.dumps(grant)},
    )
    return r, calls


# ==========================================================================
# the core revert-catcher
# ==========================================================================

def test_high_impact_no_grant_holds_202_and_never_forwards_REVERT_CATCHER(
    force_high_impact, fresh_state, monkeypatch
):
    """star (the design's core catcher): a high-impact ELIGIBLE call with NO
    grant returns 202 PENDING_APPROVAL and requests.post is NEVER called.
    Reverting the hold (falling through to forward) makes this forward. [H6]"""
    calls = _spy_post(monkeypatch)
    r = client.post("/governed-call", json=_body())
    assert r.status_code == 202
    assert r.json()["terminal_state"] == "PENDING_APPROVAL"
    assert "approval_request_id" in r.json()
    assert calls == [], "a held high-impact call must NEVER reach requests.post"


# ==========================================================================
# the approved leg
# ==========================================================================

def test_valid_grant_forwards_exactly_once(force_high_impact, fresh_state, approver, monkeypatch):
    req_id, dsha, _ = _hold(monkeypatch)
    grant = _signed_grant(approver, dsha, req_id)
    r, calls = _resubmit(grant, monkeypatch)
    assert r.status_code == 200
    assert r.json()["decision"] == "ELIGIBLE"
    assert calls == [TARGET]  # forwarded exactly once


# ==========================================================================
# refusals (REF_APPROVAL_*) - the grant never forwards
# ==========================================================================

def test_grant_for_different_action_refused(force_high_impact, fresh_state, approver, monkeypatch):
    """[H4] a grant bound to a different decision_sha256 -> REFUSE, no forward."""
    req_id, dsha, _ = _hold(monkeypatch)
    grant = _signed_grant(approver, "f" * 64, req_id)  # wrong decision hash
    r, calls = _resubmit(grant, monkeypatch)
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == REF_APPROVAL_BINDING_MISMATCH
    assert calls == []


def test_sod_grant_signed_by_gate_key_refused(force_high_impact, fresh_state, monkeypatch):
    """[H5] a grant signed by the GATE key id -> SoD REFUSE, no forward."""
    # the gate signing key is the conftest fixture; sign a grant with it.
    gate_priv, gate_key_id = pep._get_signing_key()
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", {gate_key_id: gate_priv.public_key()})
    req_id, dsha, _ = _hold(monkeypatch)
    grant = _signed_grant(gate_priv, dsha, req_id, key_id=gate_key_id)
    r, calls = _resubmit(grant, monkeypatch)
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == REF_APPROVAL_SOD
    assert calls == []


def test_expired_grant_refused(force_high_impact, fresh_state, approver, monkeypatch):
    """[H7] an expired grant -> REFUSE, no forward."""
    req_id, dsha, _ = _hold(monkeypatch)
    grant = _signed_grant(approver, dsha, req_id,
                          not_after=datetime.now(timezone.utc) - timedelta(seconds=1))
    r, calls = _resubmit(grant, monkeypatch)
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == REF_APPROVAL_EXPIRED
    assert calls == []


def test_replayed_grant_refused_second_use(force_high_impact, fresh_state, approver, monkeypatch):
    """[H3] a grant honored once cannot be honored again. The second use needs a
    fresh 202 slot; the same grant_id is REFUSED as a replay, no second forward."""
    req_id, dsha, _ = _hold(monkeypatch)
    grant = _signed_grant(approver, dsha, req_id, grant_id="grant-single")
    r1, calls1 = _resubmit(grant, monkeypatch)
    assert r1.status_code == 200 and calls1 == [TARGET]
    # obtain a fresh 202 slot for the same decision, then replay the SAME grant_id
    req_id2, dsha2, _ = _hold(monkeypatch)
    grant2 = _signed_grant(approver, dsha2, req_id2, grant_id="grant-single")  # same grant_id
    r2, calls2 = _resubmit(grant2, monkeypatch)
    assert r2.status_code == 403
    assert r2.json()["detail"]["refusal_reason_code"] == REF_APPROVAL_REPLAY
    assert calls2 == []


def test_unknown_or_unissued_request_id_refused(force_high_impact, fresh_state, approver, monkeypatch):
    """[H4] a well-signed grant whose approval_request_id was never issued (or
    already consumed) -> REFUSE, no forward."""
    _, dsha, _ = _hold(monkeypatch)
    grant = _signed_grant(approver, dsha, "req-never-issued")
    r, calls = _resubmit(grant, monkeypatch)
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == REF_APPROVAL_REQUEST_UNKNOWN
    assert calls == []


def test_no_approver_configured_means_grant_unknown(force_high_impact, fresh_state, monkeypatch):
    """With no approver key configured, any grant is KEY_UNKNOWN (fail closed)."""
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", {})
    sk = Ed25519PrivateKey.generate()
    req_id, dsha, _ = _hold(monkeypatch)
    grant = _signed_grant(sk, dsha, req_id)
    r, calls = _resubmit(grant, monkeypatch)
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == REF_APPROVAL_KEY_UNKNOWN
    assert calls == []


# ==========================================================================
# no-regression: the non-high-impact default path is untouched
# ==========================================================================

def test_non_high_impact_forwards_without_202(fresh_state, monkeypatch):
    """The real default manifest has HIGH_IMPACT: [] -> requires_approval False
    -> no 202, forwards as before (no grant needed)."""
    calls = _spy_post(monkeypatch)
    r = client.post("/governed-call", json=_body())
    assert r.status_code == 200
    assert r.json()["decision"] == "ELIGIBLE"
    assert calls == [TARGET]
