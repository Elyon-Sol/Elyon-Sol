"""
Governance layer, Feature 1, increment 1d: the audit trail ([FIX H8]) + the
approver CLI.

Two layers:
  - reconcile_approvals() over synthetic logs (incl. the revert-catcher: a
    forwarded high-impact decision with no recorded grant must be a VIOLATION).
  - an end-to-end drive of pep with an injected approval log, then reconcile of
    the captured issuance + approval logs (clean).
  - approver_cli.make_grant() output is accepted by verify_grant.
"""

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.pep import app
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.approval import build_grant, sign_grant, verify_grant, ACCEPT_GRANT_VALID
from IMPLEMENTATION.approver_cli import make_grant
from IMPLEMENTATION.envelope_inspector import (
    reconcile_approvals,
    APPROVAL_FORWARDED_WITHOUT_GRANT,
    APPROVAL_ORPHAN_CONSUMPTION,
    APPROVAL_DUPLICATE_GRANT,
    APPROVAL_DUPLICATE_REQUEST_CONSUMPTION,
)

client = TestClient(app)
SHA = manifest_sha256()
TARGET = "https://upstream.example/highimpact"
APPROVER_KEY_ID = "approver-test-ed25519-001"


def _env(decision_sha256):
    """A minimal issued-envelope record (ELIGIBLE) carrying decision_sha256."""
    return {"decision": "ELIGIBLE", "decision_sha256": decision_sha256,
            "request_context": {}, "canon": {}, "evaluator": {},
            "evaluated_against": {}, "target_url": TARGET}


def _req(ds, rid):
    return {"type": "approval_request", "decision_sha256": ds, "approval_request_id": rid}


def _consumed(ds, rid, gid="g1", akid=APPROVER_KEY_ID):
    return {"type": "grant_consumed", "decision_sha256": ds, "approval_request_id": rid,
            "grant_id": gid, "approver_key_id": akid}


# ==========================================================================
# reconcile_approvals - synthetic logs
# ==========================================================================

def test_held_approved_forwarded_is_clean():
    issued = [_env("aa")]
    approvals = [_req("aa", "r1"), _consumed("aa", "r1")]
    rep = reconcile_approvals(issued, approvals)
    assert rep["summary"]["clean"] is True
    assert rep["violations"] == []


def test_forwarded_without_grant_is_a_violation_REVERT_CATCHER():
    """star ([FIX H8]): a decision that was HELD and FORWARDED but has NO
    grant_consumed -> FORWARDED_WITHOUT_GRANT. Reverting the predicate would
    report this clean - an executed high-impact action with no recorded human
    grant, undetected."""
    issued = [_env("bb")]                 # forwarded
    approvals = [_req("bb", "r1")]        # held, but never released
    rep = reconcile_approvals(issued, approvals)
    assert rep["summary"]["clean"] is False
    assert any(v["violation"] == APPROVAL_FORWARDED_WITHOUT_GRANT
               and v.get("decision_sha256") == "bb" for v in rep["violations"])


def test_held_but_not_forwarded_is_clean():
    """A pure hold (never approved, never forwarded) is fine - the action did
    not run."""
    issued = []                           # nothing forwarded
    approvals = [_req("cc", "r1")]        # held only
    assert reconcile_approvals(issued, approvals)["summary"]["clean"] is True


def test_orphan_consumption_is_a_violation():
    issued = [_env("dd")]
    approvals = [_consumed("dd", "r-never-held")]  # release with no hold
    rep = reconcile_approvals(issued, approvals)
    assert any(v["violation"] == APPROVAL_ORPHAN_CONSUMPTION for v in rep["violations"])


def test_duplicate_grant_id_is_a_violation():
    issued = [_env("ee")]
    approvals = [_req("ee", "r1"), _consumed("ee", "r1", gid="dup"),
                 _req("ee", "r2"), _consumed("ee", "r2", gid="dup")]
    rep = reconcile_approvals(issued, approvals)
    assert any(v["violation"] == APPROVAL_DUPLICATE_GRANT for v in rep["violations"])


def test_duplicate_request_consumption_is_a_violation():
    issued = [_env("ff")]
    approvals = [_req("ff", "r1"), _consumed("ff", "r1", gid="g1"),
                 _consumed("ff", "r1", gid="g2")]
    rep = reconcile_approvals(issued, approvals)
    assert any(v["violation"] == APPROVAL_DUPLICATE_REQUEST_CONSUMPTION
               for v in rep["violations"])


# ==========================================================================
# end-to-end: pep writes the records; reconcile is clean
# ==========================================================================

class _MemLog:
    def __init__(self): self.records = []
    def append(self, rec): self.records.append(rec)


@pytest.fixture
def approver(monkeypatch):
    sk = Ed25519PrivateKey.generate()
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", {APPROVER_KEY_ID: sk.public_key()})
    return sk


@pytest.fixture
def fresh(monkeypatch):
    from IMPLEMENTATION.pep import _PendingApprovals
    from IMPLEMENTATION.replay_cache import InMemoryReplayCache
    monkeypatch.setattr(pep, "_PENDING", _PendingApprovals())
    monkeypatch.setattr(pep, "_GRANT_REPLAY", InMemoryReplayCache())
    monkeypatch.setattr(pep, "requires_approval", lambda ctx, m: True)


def _body():
    return {"target_url": TARGET, "interaction": {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0", "expected_manifest_sha256": SHA}}


def test_pep_writes_request_and_consumption_then_reconciles_clean(approver, fresh, monkeypatch):
    approval_log = _MemLog()
    issuance_log = _MemLog()
    monkeypatch.setattr(pep, "_INJECTED_APPROVAL_LOG", approval_log)
    monkeypatch.setattr(pep, "_INJECTED_ISSUANCE_LOG", issuance_log)

    class R:
        status_code = 200
        text = "{}"
    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post",
                        lambda *a, **k: R())

    # 1) hold -> 202 + an approval_request record
    r = client.post("/governed-call", json=_body())
    assert r.status_code == 202
    rid = r.json()["approval_request_id"]
    dsha = r.json()["decision_sha256"]
    assert approval_log.records[0]["type"] == "approval_request"

    # 2) approve via the approver CLI core, resubmit -> 200 + grant_consumed record
    priv_hex = approver.private_bytes_raw().hex()
    grant = make_grant(approver_private_hex=priv_hex, approver_key_id=APPROVER_KEY_ID,
                       decision_sha256=dsha, approval_request_id=rid)
    r2 = client.post("/governed-call", json=_body(),
                     headers={"X-Elyon-Sol-Approval-Grant": json.dumps(grant)})
    assert r2.status_code == 200
    assert any(rec["type"] == "grant_consumed" for rec in approval_log.records)

    # 3) the captured logs reconcile clean
    rep = reconcile_approvals(issuance_log.records, approval_log.records)
    assert rep["summary"]["clean"] is True, rep


def test_pep_without_consumption_logging_would_be_caught(approver, fresh, monkeypatch):
    """If the gate forwarded a held high-impact decision but did NOT record the
    consumption, reconcile flags FORWARDED_WITHOUT_GRANT. Simulated by dropping
    only the grant_consumed records from the captured approval log."""
    approval_log = _MemLog()
    issuance_log = _MemLog()
    monkeypatch.setattr(pep, "_INJECTED_APPROVAL_LOG", approval_log)
    monkeypatch.setattr(pep, "_INJECTED_ISSUANCE_LOG", issuance_log)

    class R:
        status_code = 200
        text = "{}"
    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", lambda *a, **k: R())

    r = client.post("/governed-call", json=_body())
    rid, dsha = r.json()["approval_request_id"], r.json()["decision_sha256"]
    priv_hex = approver.private_bytes_raw().hex()
    grant = make_grant(approver_private_hex=priv_hex, approver_key_id=APPROVER_KEY_ID,
                       decision_sha256=dsha, approval_request_id=rid)
    client.post("/governed-call", json=_body(),
                headers={"X-Elyon-Sol-Approval-Grant": json.dumps(grant)})

    # drop the consumption records -> the audit MUST catch the gap
    held_only = [rec for rec in approval_log.records if rec["type"] != "grant_consumed"]
    rep = reconcile_approvals(issuance_log.records, held_only)
    assert rep["summary"]["clean"] is False
    assert any(v["violation"] == APPROVAL_FORWARDED_WITHOUT_GRANT for v in rep["violations"])


# ==========================================================================
# approver CLI core
# ==========================================================================

def test_approver_cli_grant_is_accepted_by_verify_grant():
    sk = Ed25519PrivateKey.generate()
    priv_hex = sk.private_bytes_raw().hex()
    grant = make_grant(approver_private_hex=priv_hex, approver_key_id=APPROVER_KEY_ID,
                       decision_sha256="d" * 64, approval_request_id="req-1")
    res = verify_grant(grant, expected_decision_sha256="d" * 64,
                       expected_approval_request_id="req-1",
                       approver_public_keys={APPROVER_KEY_ID: sk.public_key()},
                       gate_key_id="gate-x")
    assert res["accepted"] is True and res["reason"] == ACCEPT_GRANT_VALID
