"""
Governance integration proof, standalone runner (design 3.3).

Asserts the two features COMPOSE - the only path to executing a high-impact
action is through-the-gate (Feature 2 mTLS) AND with-a-human-grant (Feature 1):

  A. direct bypass            -> refused at the TLS handshake (mTLS, real BIO);
  B. routed but unapproved    -> 202 PENDING_APPROVAL, target NOT called;
  C. routed + approved        -> executes EXACTLY once; reconciles clean;
  D. routed + replayed grant  -> 403, NO second execution.

Hermetic: a private dev CA + the real pep ASGI app (TestClient) with the
gate/approver keys injected in-process. Exit 0 iff A & B & C & D all hold.
"""

import json
import ssl
import sys

from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.pep import app, _PendingApprovals
from IMPLEMENTATION.replay_cache import InMemoryReplayCache
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.approver_cli import make_grant
from IMPLEMENTATION.envelope_inspector import reconcile_approvals

import deploy.tls.gen_certs as g
import TESTS.deploy.test_mtls_required as mtls

TARGET = "https://upstream.example/highimpact"
APPROVER_KEY_ID = "approver-int-ed25519-001"


class _MemLog:
    def __init__(self): self.records = []
    def append(self, rec): self.records.append(rec)


def _body(sha):
    return {"target_url": TARGET, "interaction": {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0", "expected_manifest_sha256": sha}}


def main():
    sha = manifest_sha256()
    gate_priv = Ed25519PrivateKey.generate()
    approver = Ed25519PrivateKey.generate()
    forwards = []

    # wire a high-impact gate end-to-end (in-process injection)
    pep._get_signing_key = lambda: (gate_priv, "gate-int-001")
    pep._INJECTED_APPROVER_KEYS = {APPROVER_KEY_ID: approver.public_key()}
    pep._PENDING = _PendingApprovals()
    pep._GRANT_REPLAY = InMemoryReplayCache()
    pep.requires_approval = lambda ctx, m: True
    issued, approvals = _MemLog(), _MemLog()
    pep._INJECTED_ISSUANCE_LOG = issued
    pep._INJECTED_APPROVAL_LOG = approvals

    class R:
        status_code = 200
        text = "{}"
    pep.requests.post = lambda url, **k: (forwards.append(url), R())[1]

    client = TestClient(app)

    # A. direct bypass refused at the TLS layer
    ca_key, ca_cert = g.gen_ca("Elyon-Sol Dev CA")
    ca_pem = g.cert_pem(ca_cert)
    tk, tc = g.gen_leaf(ca_key, ca_cert, mtls.TARGET_HOST, [mtls.TARGET_HOST])
    bypass_refused = False
    try:
        mtls._mtls_handshake(g.cert_pem(tc), g.key_pem(tk), ca_pem,
                             client_cert=None, require_client=True)
    except ssl.SSLError:
        bypass_refused = True

    # B. routed but unapproved -> 202, no execution
    r = client.post("/governed-call", json=_body(sha))
    held = (r.status_code == 202 and not forwards)
    rid, dsha = r.json()["approval_request_id"], r.json()["decision_sha256"]

    # C. routed + approved -> executes exactly once + reconciles clean
    grant = make_grant(approver_private_hex=approver.private_bytes_raw().hex(),
                       approver_key_id=APPROVER_KEY_ID, decision_sha256=dsha,
                       approval_request_id=rid)
    r2 = client.post("/governed-call", json=_body(sha),
                     headers={"X-Elyon-Sol-Approval-Grant": json.dumps(grant)})
    executed_once = (r2.status_code == 200 and forwards == [TARGET])
    rep = reconcile_approvals(issued.records, approvals.records)
    reconciled = rep["summary"]["clean"]

    # D. replay the same grant_id after a fresh hold -> refused, no 2nd execution
    r3 = client.post("/governed-call", json=_body(sha))
    rid2, dsha2 = r3.json()["approval_request_id"], r3.json()["decision_sha256"]
    replay = make_grant(approver_private_hex=approver.private_bytes_raw().hex(),
                        approver_key_id=APPROVER_KEY_ID, decision_sha256=dsha2,
                        approval_request_id=rid2, grant_id=grant["grant_id"])
    r4 = client.post("/governed-call", json=_body(sha),
                     headers={"X-Elyon-Sol-Approval-Grant": json.dumps(replay)})
    replay_refused = (r4.status_code == 403 and forwards == [TARGET])

    print("A. direct bypass refused at TLS      :", bypass_refused)
    print("B. routed+unapproved held (202,no-op):", held)
    print("C. routed+approved executed once     :", executed_once, "| reconciles clean:", reconciled)
    print("D. replayed grant refused (no 2nd run):", replay_refused)
    ok = bypass_refused and held and executed_once and reconciled and replay_refused
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
