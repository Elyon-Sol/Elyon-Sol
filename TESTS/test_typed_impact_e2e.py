"""
Typed-impact END-TO-END through the real pep.governed_call (VL-132 companion).

Where TESTS/adversarial/test_typed_impact.py unit-tests the evaluator/impact
layer, and TESTS/test_pep_approval.py MONKEYPATCHES requires_approval to force
the branch, THESE tests let the REAL requires_approval decide the branch against
a TYPED manifest driven through the actual gate: the same full-authority caller
is HELD (202) when the typed policy classifies it high-impact and FORWARDS (200)
when the policy is empty - proving the typed classifier, not a forced flag,
drives the gate. The approved leg (a separately-keyed human grant) forwards once.

Scope honesty (VL-132 is default-off): a BENIGN-type caller cannot go
end-to-end yet (the request schema drops interaction_type and interaction_for
returns fixed AP/OP - step 8.2), so the discrimination is shown here via the
policy (HIGH_IMPACT set vs empty) on a full-authority caller, not via a benign
subset. The gate signing key is the autouse conftest `gate_signing` fixture.
"""

import copy
import hashlib
import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import IMPLEMENTATION.pep as pep
import IMPLEMENTATION.evaluator as ev
import IMPLEMENTATION.envelope as envmod
from IMPLEMENTATION.pep import app
from IMPLEMENTATION.approval import build_grant, sign_grant

client = TestClient(app)
TARGET = "https://upstream.example/transfer"
APPROVER_KEY_ID = "approver-e2e-typed-001"


def _typed(high_impact):
    """A well-formed typed manifest; each type's high_impact flag is derived to
    satisfy safe_manifest's consistency check for the given HIGH_IMPACT set."""
    hi = set(high_impact)

    def t(ar, r):
        return {"AR": ar, "R": r, "high_impact": bool((set(ar) | set(r)) & hi)}

    return {
        "version": "1.1", "interaction_type": "default",
        "AR": ["identity", "role"], "R": ["session", "request"],
        "HIGH_IMPACT": list(high_impact),
        "interaction_types": {
            "read": t(["identity"], ["session"]),
            "transfer": t(["identity", "role"], ["session", "request"]),
        },
    }


def _body(sha):
    """A full-authority submission (AP/OP cover the top-level vocabulary)."""
    return {
        "target_url": TARGET,
        "interaction": {
            "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
            "expected_manifest_version": "1.1", "expected_manifest_sha256": sha,
        },
    }


@pytest.fixture
def install_manifest(monkeypatch):
    """Point the code paths governed_call touches at a supplied manifest, and
    return its (valid 64-hex) sha for the caller's expected_manifest_sha256."""
    def _install(manifest):
        sha = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        monkeypatch.setattr(pep, "load_manifest", lambda: copy.deepcopy(manifest))
        monkeypatch.setattr(ev, "load_manifest", lambda: copy.deepcopy(manifest))
        monkeypatch.setattr(ev, "manifest_sha256", lambda *a, **k: sha)
        if hasattr(envmod, "manifest_sha256"):
            monkeypatch.setattr(envmod, "manifest_sha256", lambda *a, **k: sha)
        return sha
    return _install


@pytest.fixture
def fresh_state(monkeypatch):
    from IMPLEMENTATION.pep import _PendingApprovals
    from IMPLEMENTATION.replay_cache import InMemoryReplayCache
    monkeypatch.setattr(pep, "_PENDING", _PendingApprovals())
    monkeypatch.setattr(pep, "_GRANT_REPLAY", InMemoryReplayCache())


@pytest.fixture
def approver(monkeypatch):
    sk = Ed25519PrivateKey.generate()
    monkeypatch.setattr(pep, "_INJECTED_APPROVER_KEYS", {APPROVER_KEY_ID: sk.public_key()})
    return sk


def _spy(monkeypatch):
    calls = []

    class R:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        calls.append(url)
        return R()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)
    return calls


def test_typed_high_impact_submission_holds_202(install_manifest, fresh_state, monkeypatch):
    """The REAL typed requires_approval (not a forced flag) holds a full-authority
    submission when the typed policy classifies it high-impact."""
    sha = install_manifest(_typed(["role", "request"]))
    calls = _spy(monkeypatch)
    r = client.post("/governed-call", json=_body(sha))
    assert r.status_code == 202
    assert r.json()["terminal_state"] == "PENDING_APPROVAL"
    assert calls == [], "a held high-impact submission must never forward"


def test_typed_empty_policy_forwards_same_caller_REVERT_CATCHER(install_manifest, fresh_state, monkeypatch):
    """star: the SAME full-authority caller, under an EXPLICIT-empty typed policy,
    FORWARDS (200) with no 202 - proving the classifier decides the branch, not a
    forced flag. If requires_approval were hard-wired True this goes RED."""
    sha = install_manifest(_typed([]))
    calls = _spy(monkeypatch)
    r = client.post("/governed-call", json=_body(sha))
    assert r.status_code == 200
    assert r.json()["decision"] == "ELIGIBLE"
    assert calls == [TARGET]


def test_typed_high_impact_approved_forwards_exactly_once(install_manifest, fresh_state, approver, monkeypatch):
    """The hold -> separately-keyed human grant -> single forward loop, end to end."""
    sha = install_manifest(_typed(["role", "request"]))
    _spy(monkeypatch)
    r = client.post("/governed-call", json=_body(sha))
    assert r.status_code == 202
    req_id = r.json()["approval_request_id"]
    dsha = r.json()["decision_sha256"]
    grant = sign_grant(
        build_grant(decision_sha256=dsha, approval_request_id=req_id, grant_id="g-e2e-1",
                    not_after=datetime.now(timezone.utc) + timedelta(seconds=300)),
        approver, APPROVER_KEY_ID)
    calls = _spy(monkeypatch)
    r2 = client.post("/governed-call", json=_body(sha),
                     headers={"X-Elyon-Sol-Approval-Grant": json.dumps(grant)})
    assert r2.status_code == 200
    assert r2.json()["decision"] == "ELIGIBLE"
    assert calls == [TARGET], "approved high-impact call forwards exactly once"



def test_typed_benign_read_forwards_end_to_end(install_manifest, fresh_state, monkeypatch):
    """CAPSTONE (what the test submission scoped for 8.2): under a typed manifest,
    a BENIGN read submission (reduced tokens + interaction_type) is ELIGIBLE and
    FORWARDS - no 202. The flat model could not express this; 8.1 (evaluator) +
    8.2 (schema interaction_type + governed_call per-type) wire it end to end."""
    sha = install_manifest(_typed(["role", "request"]))
    calls = _spy(monkeypatch)
    body = {
        "target_url": TARGET,
        "interaction": {
            "AP": ["identity"], "OP": ["session"], "context": {},
            "interaction_type": "read",
            "expected_manifest_version": "1.1", "expected_manifest_sha256": sha,
        },
    }
    r = client.post("/governed-call", json=body)
    assert r.status_code == 200
    assert r.json()["decision"] == "ELIGIBLE"
    assert calls == [TARGET], "a benign typed submission forwards without a hold"
