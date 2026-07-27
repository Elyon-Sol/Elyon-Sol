"""The domain re-determination loop, closed end to end.

An AUTHENTIC UNSAFE verdict means a human must re-determine. Previously that
produced a bare 202 that opened NO approval slot: no approval_request_id was
issued, nothing was bound into the pending set, and the existing signed-grant
path could not release the decision - the interaction was reported but stuck.

HOLD_FOR_HIL now routes into the EXISTING approval machinery (one release path,
not two): the gate issues the request id, records the hold with a distinguishing
hold_reason, and a human grant is verified for provenance/binding/SoD/freshness,
consumes the 202 slot, and claims grant_id single-use before any forward.
"""
import importlib
import json
import os
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.approval import build_grant, sign_grant
from IMPLEMENTATION.domain_verdict import build_verdict, sign_verdict, VERDICT_UNSAFE

SHA = manifest_sha256()
TARGET = "https://example.invalid/x"
GATE_KEY_ID = "ELYON_GATE_TEST"
AUTH_KEY_ID = "AUTH1"
APPROVER_KEY_ID = "APPROVER1"

_ENV = ("ELYON_DOMAIN_MANIFEST", "ELYON_SIGNING_KEY_HEX", "ELYON_SIGNING_KEY_ID",
        "ELYON_APPROVAL_LOG_PATH", "ELYON_GATE_READ_ENDPOINTS")


@pytest.fixture(autouse=True)
def _restore_pep():
    yield
    for k in _ENV:
        os.environ.pop(k, None)
    import IMPLEMENTATION.pep as pep
    importlib.reload(pep)


@pytest.fixture
def authority():
    sk = Ed25519PrivateKey.generate()
    return sk, sk.public_key()


@pytest.fixture
def approver():
    sk = Ed25519PrivateKey.generate()
    return sk, sk.public_key()


def _manifest(tmp_path):
    dm = {"version": "1.0", "require_pin": False, "domains": {"healthcare_admin": {
        "predicates": [], "interaction_types": ["chart_write"],
        "requires_verdict": True, "authority_key_id": AUTH_KEY_ID}}}
    p = tmp_path / "dm.json"
    p.write_text(json.dumps(dm), encoding="utf-8")
    return str(p)


def _client(monkeypatch, dm_path, authority_pk=None, approver_pk=None):
    monkeypatch.setenv("ELYON_DOMAIN_MANIFEST", dm_path)
    monkeypatch.setenv("ELYON_SIGNING_KEY_HEX", "11" * 32)
    monkeypatch.setenv("ELYON_SIGNING_KEY_ID", GATE_KEY_ID)
    import IMPLEMENTATION.pep as pep
    pep = importlib.reload(pep)
    # Inject the trust maps directly (the signed-record chain is exercised in
    # test_domain_authority / test_approver_signed_chain; here the subject is the
    # HOLD_FOR_HIL -> approval-slot -> grant-release loop).
    if authority_pk is not None:
        pep._domain_authority_keys = lambda: {AUTH_KEY_ID: authority_pk}
    if approver_pk is not None:
        pep._INJECTED_APPROVER_KEYS = {APPROVER_KEY_ID: approver_pk}
    return TestClient(pep.app, raise_server_exceptions=False), pep


def _body():
    return {"target_url": TARGET, "interaction": {
        "AP": ["identity", "role"], "OP": ["session", "request"],
        "context": {}, "domain": "healthcare_admin",
        "interaction_type": "chart_write",
        "expected_manifest_version": "1.0", "expected_manifest_sha256": SHA}}


def _unsafe_verdict(authority, decision_sha256):
    sk, _ = authority
    return sign_verdict(build_verdict(
        decision_sha256=decision_sha256, domain="healthcare_admin",
        verdict=VERDICT_UNSAFE, verdict_id="vd-unsafe",
        not_after=datetime.now(timezone.utc) + timedelta(seconds=300)), sk, AUTH_KEY_ID)


def _decision_sha(client):
    """Obtain the decision_sha256 for this interaction from the hold response."""
    r = client.post("/governed-call", json=_body())
    return r.json()["decision_sha256"]


# --- the loop: authentic UNSAFE opens a real approval slot -------------------

def test_authentic_unsafe_issues_an_approval_request_id(monkeypatch, tmp_path, authority):
    """PRE-FIX: a bare 202 with no approval_request_id - nothing a grant could
    fill, so the decision was permanently stuck."""
    _, pk = authority
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=pk)
    dsha = _decision_sha(client)
    r = client.post("/governed-call", json=_body(),
                    headers={"X-Elyon-Sol-Domain-Verdict":
                             json.dumps(_unsafe_verdict(authority, dsha))})
    assert r.status_code == 202
    body = r.json()
    assert body["terminal_state"] == "PENDING_APPROVAL"
    assert body["approval_request_id"], "no slot was opened - the loop is not closed"
    assert body["decision_sha256"] == dsha


def test_hold_reason_distinguishes_domain_from_high_impact(monkeypatch, tmp_path, authority):
    """An operator must be able to tell 'a human must re-determine a domain
    compliance failure' from 'this interaction type is HIGH_IMPACT'."""
    _, pk = authority
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=pk)
    dsha = _decision_sha(client)
    r = client.post("/governed-call", json=_body(),
                    headers={"X-Elyon-Sol-Domain-Verdict":
                             json.dumps(_unsafe_verdict(authority, dsha))})
    assert r.json()["hold_reason"] == "D_VERDICT_UNSAFE"


def test_the_hold_is_durably_recorded_and_listed_as_pending(monkeypatch, tmp_path, authority):
    """The hold must survive in the durable approval log - that is what makes it
    actionable by a human and visible on the read side after a restart."""
    _, pk = authority
    log_path = tmp_path / "approval.jsonl"
    monkeypatch.setenv("ELYON_APPROVAL_LOG_PATH", str(log_path))
    monkeypatch.setenv("ELYON_GATE_READ_ENDPOINTS", "1")
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=pk)
    dsha = _decision_sha(client)
    r = client.post("/governed-call", json=_body(),
                    headers={"X-Elyon-Sol-Domain-Verdict":
                             json.dumps(_unsafe_verdict(authority, dsha))})
    rid = r.json()["approval_request_id"]

    records = [json.loads(l) for l in
               log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    holds = [x for x in records if x.get("approval_request_id") == rid]
    assert holds, "the domain hold was not durably recorded"
    assert holds[0]["type"] == "approval_request"        # reconcile still keys on this
    assert holds[0]["hold_reason"] == "D_VERDICT_UNSAFE"  # ...and WHY is recorded

    pending = client.get("/pending").json()
    assert any(e.get("approval_request_id") == rid for e in pending)


# --- a human grant RELEASES the domain hold (the loop actually closes) -------

def test_valid_human_grant_releases_the_domain_hold(monkeypatch, tmp_path, authority, approver):
    """The whole point: after re-determination, a signed human grant must get the
    call past the domain hold. Anything other than a 202 proves the slot is
    fillable (the forward itself fails later - the target is unreachable)."""
    _, apk = authority
    ask, ppk = approver
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=apk, approver_pk=ppk)
    dsha = _decision_sha(client)
    hold = client.post("/governed-call", json=_body(),
                       headers={"X-Elyon-Sol-Domain-Verdict":
                                json.dumps(_unsafe_verdict(authority, dsha))})
    rid = hold.json()["approval_request_id"]

    grant = sign_grant(build_grant(
        decision_sha256=dsha, approval_request_id=rid, grant_id="g-1",
        not_after=datetime.now(timezone.utc) + timedelta(seconds=300),
        overrides_verdict_id="vd-unsafe"),
        ask, APPROVER_KEY_ID)
    r = client.post("/governed-call", json=_body(),
                    headers={"X-Elyon-Sol-Domain-Verdict":
                             json.dumps(_unsafe_verdict(authority, dsha)),
                             "X-Elyon-Sol-Approval-Grant": json.dumps(grant)})
    assert r.status_code != 202, "a valid grant did not release the hold"
    code = (r.json().get("detail") or {}).get("refusal_reason_code", "")
    assert not str(code).startswith("REF_APPROVAL"), f"grant rejected: {code}"


def test_gate_signed_grant_refused_sod(monkeypatch, tmp_path, authority):
    """The release path inherits SoD: the gate cannot approve its own domain hold."""
    _, apk = authority
    gate_sk = Ed25519PrivateKey.generate()
    client, pep = _client(monkeypatch, _manifest(tmp_path), authority_pk=apk,
                          approver_pk=gate_sk.public_key())
    pep._INJECTED_APPROVER_KEYS = {GATE_KEY_ID: gate_sk.public_key()}
    dsha = _decision_sha(client)
    hold = client.post("/governed-call", json=_body(),
                       headers={"X-Elyon-Sol-Domain-Verdict":
                                json.dumps(_unsafe_verdict(authority, dsha))})
    rid = hold.json()["approval_request_id"]
    grant = sign_grant(build_grant(
        decision_sha256=dsha, approval_request_id=rid, grant_id="g-2",
        not_after=datetime.now(timezone.utc) + timedelta(seconds=300),
        overrides_verdict_id="vd-unsafe"),
        gate_sk, GATE_KEY_ID)          # signed with the GATE's id
    r = client.post("/governed-call", json=_body(),
                    headers={"X-Elyon-Sol-Domain-Verdict":
                             json.dumps(_unsafe_verdict(authority, dsha)),
                             "X-Elyon-Sol-Approval-Grant": json.dumps(grant)})
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "REF_APPROVAL_SOD"


def test_grant_for_a_different_decision_refused(monkeypatch, tmp_path, authority, approver):
    """Binding survives the domain path: a grant for another decision cannot
    release this one."""
    _, apk = authority
    ask, ppk = approver
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=apk, approver_pk=ppk)
    dsha = _decision_sha(client)
    hold = client.post("/governed-call", json=_body(),
                       headers={"X-Elyon-Sol-Domain-Verdict":
                                json.dumps(_unsafe_verdict(authority, dsha))})
    rid = hold.json()["approval_request_id"]
    grant = sign_grant(build_grant(
        decision_sha256="f" * 64, approval_request_id=rid, grant_id="g-3",
        not_after=datetime.now(timezone.utc) + timedelta(seconds=300),
        overrides_verdict_id="vd-unsafe"),
        ask, APPROVER_KEY_ID)
    r = client.post("/governed-call", json=_body(),
                    headers={"X-Elyon-Sol-Domain-Verdict":
                             json.dumps(_unsafe_verdict(authority, dsha)),
                             "X-Elyon-Sol-Approval-Grant": json.dumps(grant)})
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "REF_APPROVAL_BINDING_MISMATCH"


# --- B: the override is EXPLICIT (F-1) and freshness-independent (F-6) -------

def _expired_unsafe(authority, dsha, vid="vd-unsafe"):
    sk, _ = authority
    return sign_verdict(build_verdict(
        decision_sha256=dsha, domain="healthcare_admin", verdict=VERDICT_UNSAFE,
        verdict_id=vid,
        not_after=datetime.now(timezone.utc) - timedelta(seconds=1)), sk, AUTH_KEY_ID)


def _open_hold(client, authority, dsha):
    r = client.post("/governed-call", json=_body(),
                    headers={"X-Elyon-Sol-Domain-Verdict":
                             json.dumps(_unsafe_verdict(authority, dsha))})
    return r.json()["approval_request_id"]


def _grant(ask, dsha, rid, gid, overrides):
    g = build_grant(decision_sha256=dsha, approval_request_id=rid, grant_id=gid,
                    not_after=datetime.now(timezone.utc) + timedelta(seconds=300),
                    overrides_verdict_id=overrides)
    return sign_grant(g, ask, APPROVER_KEY_ID)


def test_F1_plain_grant_cannot_discharge_a_domain_hold(monkeypatch, tmp_path, authority, approver):
    """ANTI-LAUNDERING. A grant with no overrides_verdict_id - e.g. one a human
    signed for a HIGH_IMPACT hold - must not discharge a safety finding it never
    referred to."""
    _, apk = authority; ask, ppk = approver
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=apk, approver_pk=ppk)
    dsha = _decision_sha(client); rid = _open_hold(client, authority, dsha)
    plain = sign_grant(build_grant(
        decision_sha256=dsha, approval_request_id=rid, grant_id="g-plain",
        not_after=datetime.now(timezone.utc) + timedelta(seconds=300)), ask, APPROVER_KEY_ID)
    r = client.post("/governed-call", json=_body(), headers={
        "X-Elyon-Sol-Domain-Verdict": json.dumps(_unsafe_verdict(authority, dsha)),
        "X-Elyon-Sol-Approval-Grant": json.dumps(plain)})
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "D_OVERRIDE_MISMATCH"


def test_F1_grant_naming_the_wrong_verdict_refused(monkeypatch, tmp_path, authority, approver):
    _, apk = authority; ask, ppk = approver
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=apk, approver_pk=ppk)
    dsha = _decision_sha(client); rid = _open_hold(client, authority, dsha)
    r = client.post("/governed-call", json=_body(), headers={
        "X-Elyon-Sol-Domain-Verdict": json.dumps(_unsafe_verdict(authority, dsha)),
        "X-Elyon-Sol-Approval-Grant": json.dumps(_grant(ask, dsha, rid, "g-w", "vd-SOMETHING-ELSE"))})
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "D_OVERRIDE_MISMATCH"


def test_F6_override_releases_even_though_the_verdict_expired(monkeypatch, tmp_path, authority, approver):
    """PRE-FIX: the grant was unusable unless a STILL-FRESH UNSAFE verdict was
    re-presented alongside it. Since a verdict lives minutes and human
    re-determination does not, the triggering verdict always expired first and the
    signed grant became worthless."""
    _, apk = authority; ask, ppk = approver
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=apk, approver_pk=ppk)
    dsha = _decision_sha(client); rid = _open_hold(client, authority, dsha)
    r = client.post("/governed-call", json=_body(), headers={
        "X-Elyon-Sol-Domain-Verdict": json.dumps(_expired_unsafe(authority, dsha)),
        "X-Elyon-Sol-Approval-Grant": json.dumps(_grant(ask, dsha, rid, "g-x", "vd-unsafe"))})
    assert r.status_code != 202, "an expired-but-overridden verdict still blocked the release"
    code = (r.json().get("detail") or {}).get("refusal_reason_code", "")
    assert not str(code).startswith(("D_", "REF_APPROVAL")), f"released path refused: {code}"


def test_F6_waiver_is_scoped_to_the_named_verdict_only(monkeypatch, tmp_path, authority, approver):
    """The waiver must not become a general expiry bypass: an expired verdict the
    grant does NOT name stays expired."""
    _, apk = authority; ask, ppk = approver
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=apk, approver_pk=ppk)
    dsha = _decision_sha(client); rid = _open_hold(client, authority, dsha)
    r = client.post("/governed-call", json=_body(), headers={
        # grant names vd-unsafe; the presented expired verdict is a DIFFERENT id
        "X-Elyon-Sol-Domain-Verdict": json.dumps(_expired_unsafe(authority, dsha, "vd-other")),
        "X-Elyon-Sol-Approval-Grant": json.dumps(_grant(ask, dsha, rid, "g-s", "vd-unsafe"))})
    assert r.status_code == 202
    assert r.json()["refusal_reason_code"] == "D_VERDICT_UNVERIFIED"


def test_F1_consumption_record_names_what_was_overridden(monkeypatch, tmp_path, authority, approver):
    """The audit half of F-1: the trail must prove WHICH safety finding a named
    approver overruled, not merely that a grant released a decision hash."""
    _, apk = authority; ask, ppk = approver
    log_path = tmp_path / "approval.jsonl"
    monkeypatch.setenv("ELYON_APPROVAL_LOG_PATH", str(log_path))
    client, _ = _client(monkeypatch, _manifest(tmp_path), authority_pk=apk, approver_pk=ppk)
    dsha = _decision_sha(client); rid = _open_hold(client, authority, dsha)
    client.post("/governed-call", json=_body(), headers={
        "X-Elyon-Sol-Domain-Verdict": json.dumps(_expired_unsafe(authority, dsha)),
        "X-Elyon-Sol-Approval-Grant": json.dumps(_grant(ask, dsha, rid, "g-a", "vd-unsafe"))})
    recs = [json.loads(l) for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    holds = [r for r in recs if r.get("type") == "approval_request"]
    used = [r for r in recs if r.get("type") == "grant_consumed"]
    assert holds and holds[0].get("overridden_verdict_id") == "vd-unsafe"
    assert used, "no consumption record"
    assert used[0]["hold_reason"] == "D_VERDICT_UNSAFE"
    assert used[0]["overridden_verdict_id"] == "vd-unsafe"
    assert used[0]["approver_key_id"] == APPROVER_KEY_ID
