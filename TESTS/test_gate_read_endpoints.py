"""Gate read-only observability endpoints (/pending, /audit) - DEFAULT OFF.

Wire-level pins: (1) with ELYON_GATE_READ_ENDPOINTS unset the endpoints are 404 and the
gate is behavior-unchanged (revert-catcher for the default-off law); (2) enabled, /pending
lists exactly the held-not-consumed requests WITH public context and drains on consume;
(3) /audit tails the durable logs; (4) neither endpoint ever emits key material.
"""

import json

import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.pep import app
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.approval import build_grant, sign_grant
from IMPLEMENTATION.issuance_log import JsonlIssuanceLog, JsonlApprovalLog
from datetime import datetime, timedelta, timezone

client = TestClient(app)
SHA = manifest_sha256()
TARGET = "https://upstream.example/highimpact"
APPROVER_KEY_ID = "approver-test-ed25519-001"


def _body():
    return {"target_url": TARGET, "interaction": {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0", "expected_manifest_sha256": SHA}}


@pytest.fixture
def approver(monkeypatch):
    sk = Ed25519PrivateKey.generate()
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", {APPROVER_KEY_ID: sk.public_key()})
    return sk


@pytest.fixture
def governed(tmp_path, monkeypatch):
    """High-impact branch + fresh state + real JSONL logs in tmp_path."""
    from IMPLEMENTATION.pep import _PendingApprovals
    from IMPLEMENTATION.replay_cache import InMemoryReplayCache
    monkeypatch.setattr(pep, "requires_approval", lambda ctx, manifest: True)
    monkeypatch.setattr(pep, "_PENDING", _PendingApprovals())
    monkeypatch.setattr(pep, "_GRANT_REPLAY", InMemoryReplayCache())
    iss, appr = str(tmp_path / "iss.jsonl"), str(tmp_path / "appr.jsonl")
    monkeypatch.setattr(pep, "_INJECTED_ISSUANCE_LOG", JsonlIssuanceLog(iss))
    monkeypatch.setattr(pep, "_INJECTED_APPROVAL_LOG", JsonlApprovalLog(appr))

    class R:
        status_code = 200
        text = '{"ok": true}'

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post",
                        lambda url, json, timeout, headers=None, verify=None, cert=None: R())
    return iss, appr


def test_endpoints_are_404_by_default_REVERT_CATCHER(governed, monkeypatch):
    """DEFAULT OFF is the law: without the env flag the read endpoints do not exist.
    If the gate ever serves them unconditionally, this goes RED."""
    monkeypatch.delenv(pep.READ_ENDPOINTS_ENV, raising=False)
    assert client.get("/pending").status_code == 404
    assert client.get("/audit").status_code == 404


def test_pending_lists_held_with_context_and_drains_on_consume(governed, approver, monkeypatch):
    monkeypatch.setenv(pep.READ_ENDPOINTS_ENV, "1")
    r = client.post("/governed-call", json=_body())
    assert r.status_code == 202
    rid, dsha = r.json()["approval_request_id"], r.json()["decision_sha256"]

    held = client.get("/pending").json()
    assert [h["approval_request_id"] for h in held] == [rid]
    h = held[0]
    assert h["decision_sha256"] == dsha and h["target_url"] == TARGET
    assert "requested_at" in h                             # public context for a human
    # a HELD decision is deliberately unsigned - not_after only exists after
    # sign_envelope on the approved leg, so it must NOT be claimed here
    assert "not_after" not in h

    grant = sign_grant(build_grant(decision_sha256=dsha, approval_request_id=rid,
                                   grant_id="g-read-endpoint-test",
                                   not_after=datetime.now(timezone.utc) + timedelta(seconds=60)),
                       approver, APPROVER_KEY_ID)
    r2 = client.post("/governed-call", json=_body(),
                     headers={"X-Elyon-Sol-Approval-Grant": json.dumps(grant)})
    assert r2.status_code == 200
    assert client.get("/pending").json() == []             # consumed -> drained


def test_audit_tails_both_logs_and_leaks_no_key_material(governed, approver, monkeypatch):
    monkeypatch.setenv(pep.READ_ENDPOINTS_ENV, "1")
    r = client.post("/governed-call", json=_body())
    rid, dsha = r.json()["approval_request_id"], r.json()["decision_sha256"]
    grant = sign_grant(build_grant(decision_sha256=dsha, approval_request_id=rid,
                                   grant_id="g-audit-test",
                                   not_after=datetime.now(timezone.utc) + timedelta(seconds=60)),
                       approver, APPROVER_KEY_ID)
    client.post("/governed-call", json=_body(),
                headers={"X-Elyon-Sol-Approval-Grant": json.dumps(grant)})

    d = client.get("/audit?tail=10").json()
    assert [rec["type"] for rec in d["approval"]] == ["approval_request", "grant_consumed"]
    assert len(d["issuance"]) == 1 and d["issuance"][0]["decision_sha256"] == dsha
    body = json.dumps(d)
    # public material only: the approver PRIVATE key hex must never appear anywhere
    assert approver.private_bytes_raw().hex() not in body
    assert client.get("/audit?tail=1").json()["approval"][-1]["type"] == "grant_consumed"
