"""
Governance integration proof (design 3.3): the two features COMPOSE, so a
high-impact action cannot execute unless it BOTH

  (A) routes through the gate  - Feature 2, mTLS: a direct connection to the
      target without the gate client cert is refused at the TLS handshake; and
  (B/C) carries a valid human grant - Feature 1: routed-but-unapproved holds at
      202 with no execution; routed+approved executes EXACTLY ONCE and is
      reconcilable on the issuance + approval logs.

The only path to execution is through-the-gate AND with-a-grant. Leg A uses the
hermetic mTLS handshake (test_mtls_required); legs B/C drive the real pep ASGI
app via TestClient with the gate/approver keys injected.
"""

import json
import ssl

import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.pep import app
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.approver_cli import make_grant
from IMPLEMENTATION.envelope_inspector import reconcile_approvals

import deploy.tls.gen_certs as g
import TESTS.deploy.test_mtls_required as mtls

client = TestClient(app)
SHA = manifest_sha256()
TARGET = "https://upstream.example/highimpact"
APPROVER_KEY_ID = "approver-int-ed25519-001"


class _MemLog:
    def __init__(self): self.records = []
    def append(self, rec): self.records.append(rec)


def _body():
    return {"target_url": TARGET, "interaction": {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0", "expected_manifest_sha256": SHA}}


@pytest.fixture
def gov(monkeypatch):
    """Wire a high-impact gate end-to-end: gate signing key, a separate approver
    key, fresh state, capturing logs, force the high-impact branch, spy forward."""
    from IMPLEMENTATION.pep import _PendingApprovals
    from IMPLEMENTATION.replay_cache import InMemoryReplayCache
    gate_priv = Ed25519PrivateKey.generate()
    monkeypatch.setattr(pep, "_get_signing_key", lambda: (gate_priv, "gate-int-001"))
    approver = Ed25519PrivateKey.generate()
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", {APPROVER_KEY_ID: approver.public_key()})
    monkeypatch.setattr(pep, "_PENDING", _PendingApprovals())
    monkeypatch.setattr(pep, "_GRANT_REPLAY", InMemoryReplayCache())
    monkeypatch.setattr(pep, "requires_approval", lambda ctx, m: True)
    issued, approvals = _MemLog(), _MemLog()
    monkeypatch.setattr(pep, "_INJECTED_ISSUANCE_LOG", issued)
    monkeypatch.setattr(pep, "_INJECTED_APPROVAL_LOG", approvals)
    forwards = []

    class R:
        status_code = 200
        text = "{}"
    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post",
                        lambda url, **k: (forwards.append(url), R())[1])
    return {"approver": approver, "issued": issued, "approvals": approvals, "forwards": forwards}


def test_integration_all_three_legs(gov):
    # ---- Leg A: direct bypass is refused at the TLS layer (Feature 2) ----
    ca_key, ca_cert = g.gen_ca("Elyon-Sol Dev CA")
    ca_pem = g.cert_pem(ca_cert)
    tk, tc = g.gen_leaf(ca_key, ca_cert, mtls.TARGET_HOST, [mtls.TARGET_HOST])
    with pytest.raises(ssl.SSLError):
        mtls._mtls_handshake(g.cert_pem(tc), g.key_pem(tk), ca_pem,
                             client_cert=None, require_client=True)

    # ---- Leg B: routed but UNAPPROVED holds at 202, no execution (Feature 1) ----
    r = client.post("/governed-call", json=_body())
    assert r.status_code == 202
    assert r.json()["terminal_state"] == "PENDING_APPROVAL"
    assert gov["forwards"] == [], "an unapproved high-impact call must not execute"
    rid, dsha = r.json()["approval_request_id"], r.json()["decision_sha256"]

    # ---- Leg C: routed + APPROVED executes exactly once, reconcilable ----
    grant = make_grant(approver_private_hex=gov["approver"].private_bytes_raw().hex(),
                       approver_key_id=APPROVER_KEY_ID,
                       decision_sha256=dsha, approval_request_id=rid)
    r2 = client.post("/governed-call", json=_body(),
                     headers={"X-Elyon-Sol-Approval-Grant": json.dumps(grant)})
    assert r2.status_code == 200
    assert gov["forwards"] == [TARGET], "approved high-impact call executes EXACTLY once"

    # the lifecycle reconciles clean (no FORWARDED_WITHOUT_GRANT)
    rep = reconcile_approvals(gov["issued"].records, gov["approvals"].records)
    assert rep["summary"]["clean"] is True, rep

    # and a REPLAY of the same grant after a fresh hold is refused (no 2nd exec)
    r3 = client.post("/governed-call", json=_body())          # fresh 202
    rid2, dsha2 = r3.json()["approval_request_id"], r3.json()["decision_sha256"]
    replay = make_grant(approver_private_hex=gov["approver"].private_bytes_raw().hex(),
                        approver_key_id=APPROVER_KEY_ID, decision_sha256=dsha2,
                        approval_request_id=rid2, grant_id=grant["grant_id"])  # same grant_id
    r4 = client.post("/governed-call", json=_body(),
                     headers={"X-Elyon-Sol-Approval-Grant": json.dumps(replay)})
    assert r4.status_code == 403
    assert gov["forwards"] == [TARGET], "a replayed grant must not cause a second execution"
