"""Local governance demo - drive the REAL 202 -> approve -> consume flow and write the
issuance + approval JSONL decision logs, on one machine, no Redis/mTLS/hosts required.

This is a DEV helper: it exercises the production governance code (pep.governed_call, the
Ed25519 approval grant, the JSONL issuance/approval logs) in-process, so you get real
decision logs to read and reconcile without standing up the full multi-host deployment.

WHAT IT IS NOT: the [FIX H5] custody boundary is COLLAPSED here for convenience - the approver
private key lives in this one process. In a real deployment the approver key lives ONLY in a
separate approver-CLI process/host (deploy/governance.env.example: ELYON_APPROVER_KEY_HEX), never
on the gate. This demo signs the grant in a clearly-marked "APPROVER (separate in prod)" block to
keep the shape honest.

Run from the repo root:
    python deploy/governance/local_demo/run_local_governance.py
Then read the logs it prints (e.g. with the operator tooling, or `cat`).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.pep import app
from IMPLEMENTATION.evaluator import load_manifest, manifest_sha256
from IMPLEMENTATION.approver_cli import make_grant
from IMPLEMENTATION.issuance_log import JsonlIssuanceLog, JsonlApprovalLog
from IMPLEMENTATION.pep import _PendingApprovals
from IMPLEMENTATION.replay_cache import InMemoryReplayCache

RUNTIME = os.path.join(HERE, "runtime")
ISSUANCE_LOG = os.path.join(RUNTIME, "issuance.log")
APPROVAL_LOG = os.path.join(RUNTIME, "approval.log")
TARGET = "https://upstream.local/highimpact"
GATE_KEY_ID = "gate-local-001"
APPROVER_KEY_ID = "approver-local-001"


def _body(tag=""):
    m = load_manifest()
    return {"target_url": TARGET, "interaction": {
        "AP": ["identity", "role"], "OP": ["session", "request"],
        "context": {"demo": tag} if tag else {},
        "expected_manifest_version": m["version"],
        "expected_manifest_sha256": manifest_sha256()}}


def main():
    os.makedirs(RUNTIME, exist_ok=True)
    for p in (ISSUANCE_LOG, APPROVAL_LOG):
        open(p, "w").close()  # fresh run

    # --- GATE wiring (this host): issuer key, approver PUBLIC key, fresh state, real logs ---
    gate_priv = Ed25519PrivateKey.generate()
    approver_priv = Ed25519PrivateKey.generate()          # (in prod: lives on the approver host)
    pep._get_signing_key = lambda: (gate_priv, GATE_KEY_ID)
    pep._INJECTED_APPROVER_KEYS = {APPROVER_KEY_ID: approver_priv.public_key()}  # PUBLIC only
    pep._PENDING = _PendingApprovals()
    pep._GRANT_REPLAY = InMemoryReplayCache()
    pep.requires_approval = lambda ctx, m: True            # declare this action high-impact
    pep._INJECTED_ISSUANCE_LOG = JsonlIssuanceLog(ISSUANCE_LOG)
    pep._INJECTED_APPROVAL_LOG = JsonlApprovalLog(APPROVAL_LOG)

    forwards = []

    class _R:
        status_code = 200
        text = "{}"
    pep.requests.post = lambda url, **k: (forwards.append(url), _R())[1]

    client = TestClient(app)

    # ================= Scenario 1: an APPROVED high-impact action =================
    r = client.post("/governed-call", json=_body("s1-approved"))
    assert r.status_code == 202, r.text
    rid = r.json()["approval_request_id"]
    dsha = r.json()["decision_sha256"]
    print(f"[hold ] 202 PENDING_APPROVAL  request={rid}  decision={dsha[:16]}...")

    # ---- APPROVER (a separate process/host in prod; the private key never reaches the gate) ----
    grant = make_grant(approver_private_hex=approver_priv.private_bytes_raw().hex(),
                       approver_key_id=APPROVER_KEY_ID,
                       decision_sha256=dsha, approval_request_id=rid)
    # ---- back on the GATE: present the human grant; it executes exactly once ----
    r2 = client.post("/governed-call", json=_body("s1-approved"),
                     headers={"X-Elyon-Sol-Approval-Grant": json.dumps(grant)})
    assert r2.status_code == 200, r2.text
    print(f"[grant] approved + forwarded once  grant_id={grant['grant_id'][:12]}...  forwards={len(forwards)}")
    approved_decision = dsha

    # ================= Scenario 2: a still-PENDING high-impact action =================
    r3 = client.post("/governed-call", json=_body("s2-pending"))
    assert r3.status_code == 202
    print(f"[hold ] 202 PENDING_APPROVAL  request={r3.json()['approval_request_id']}  (left un-approved)")

    print("\n--- decision logs written (real records from the governance path) ---")
    print("issuance:", ISSUANCE_LOG, f"({sum(1 for _ in open(ISSUANCE_LOG))} lines)")
    print("approval:", APPROVAL_LOG, f"({sum(1 for _ in open(APPROVAL_LOG))} lines)")
    print("\nPoint an operator console at those two files. Trace this decision end-to-end:")
    print("  decision_sha256 =", approved_decision)


if __name__ == "__main__":
    main()
