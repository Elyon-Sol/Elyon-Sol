"""
Gate-side issuance-log tests (VL-099).

Derived from docs/restructure/28_issuance_log_spec.md and canon:
  - section 9 (fail-closed: a CONFIGURED gate that cannot record an
    issuance refuses and never calls the target)
  - section 14 (the log records; it does not decide or execute)

The property under test end-to-end: the gate's issuance log is exactly
the `--issued` input the VL-097 reconciler consumes, so "every executed
action maps to a signed, bound, single-use issued envelope" becomes a
checkable claim over a real gate's history.

Default-off discipline: with no injected log and no
ELYON_ISSUANCE_LOG_PATH, the ELIGIBLE path is byte-behavior-identical
to pre-VL-099 (asserted below).

Ledger: VL-099.
"""

import json

import pytest
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.issuance_log import (
    ISSUANCE_LOG_PATH_ENV,
    JsonlIssuanceLog,
    issuance_log_from_env,
)
from IMPLEMENTATION.envelope_inspector import (
    AUDIT_MATCHED,
    AUDIT_OUT_OF_SCOPE,
    reconcile,
)

client = TestClient(pep.app)

SHA = manifest_sha256()


def _request_body(context=None):
    return {
        "target_url": "https://upstream.example/act",
        "interaction": {
            "AP": ["identity", "role"],
            "OP": ["session", "request"],
            "context": context if context is not None else {"purpose": "issuance-log-test"},
            "expected_manifest_version": "1.0",
            "expected_manifest_sha256": SHA,
        },
    }


class FakeResponse:
    status_code = 200
    text = '{"ok": true}'


@pytest.fixture()
def upstream(monkeypatch):
    """Capture the ELIGIBLE push instead of performing real HTTP."""
    calls = []

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        calls.append({"url": url, "json": json, "headers": headers})
        return FakeResponse()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)
    return calls


@pytest.fixture()
def log_file(tmp_path, monkeypatch):
    """Inject a JsonlIssuanceLog over a tmp file into pep."""
    path = tmp_path / "issued.jsonl"
    monkeypatch.setattr(pep, "_INJECTED_ISSUANCE_LOG", JsonlIssuanceLog(str(path)))
    return path


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


# ---------------------------------------------------------------------------
# Unit: JsonlIssuanceLog + from_env
# ---------------------------------------------------------------------------


def test_jsonl_log_one_canonical_line_per_append(tmp_path):
    """Spec 28 section 2.1: one canonical_json line per envelope, in
    append order, round-tripping by json.loads."""
    path = tmp_path / "log.jsonl"
    log = JsonlIssuanceLog(str(path))
    first = {"decision": "ELIGIBLE", "decision_id": "d-1"}
    second = {"decision": "ELIGIBLE", "decision_id": "d-2"}
    log.append(first)
    log.append(second)
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    assert raw_lines == [canonical_json(first), canonical_json(second)]
    assert _read_jsonl(path) == [first, second]


def test_from_env_default_none(monkeypatch):
    """Spec 28: unset env -> None (the default-off seam)."""
    monkeypatch.delenv(ISSUANCE_LOG_PATH_ENV, raising=False)
    assert issuance_log_from_env() is None


def test_from_env_path_set(monkeypatch, tmp_path):
    """Spec 28: env path -> a JsonlIssuanceLog over that path."""
    target = str(tmp_path / "issued.jsonl")
    monkeypatch.setenv(ISSUANCE_LOG_PATH_ENV, target)
    log = issuance_log_from_env()
    assert isinstance(log, JsonlIssuanceLog)
    assert log.path == target


# ---------------------------------------------------------------------------
# pep wiring
# ---------------------------------------------------------------------------


def test_eligible_appends_the_signed_response_envelope(upstream, log_file):
    """Spec 28 section 2.2: an admitted call appends exactly ONE line,
    and it is the SIGNED envelope the caller received (issuer_signature
    and decision_id present) - the log records what was issued."""
    response = client.post("/governed-call", json=_request_body())
    assert response.status_code == 200, response.text
    returned = response.json()["envelope"]
    logged = _read_jsonl(log_file)
    assert logged == [returned]
    assert isinstance(logged[0]["issuer_signature"], str)
    assert isinstance(logged[0]["decision_id"], str)
    assert len(upstream) == 1


def test_refuse_appends_nothing(upstream, log_file):
    """Canon section 9 ordering: an evaluator-layer REFUSE never reaches
    issuance; the log stays empty (as does upstream)."""
    body = _request_body()
    body["interaction"]["AP"] = []
    body["interaction"]["OP"] = []
    response = client.post("/governed-call", json=body)
    assert response.status_code == 403
    assert not log_file.exists() or _read_jsonl(log_file) == []
    assert upstream == []


def test_schema_refusal_appends_nothing(upstream, log_file):
    """Schema-layer refusals return before evaluation, hence before
    issuance; the log stays empty."""
    response = client.post("/governed-call", json={"target_url": "x", "AP": []})
    assert response.status_code == 403
    assert not log_file.exists() or _read_jsonl(log_file) == []
    assert upstream == []


def test_default_no_log_path_unchanged(upstream, monkeypatch):
    """Spec 28 default-off: with no injected log and no env var, the
    ELIGIBLE path behaves exactly as pre-VL-099 (admits and pushes)."""
    monkeypatch.delenv(ISSUANCE_LOG_PATH_ENV, raising=False)
    assert pep._INJECTED_ISSUANCE_LOG is None
    response = client.post("/governed-call", json=_request_body())
    assert response.status_code == 200, response.text
    assert len(upstream) == 1


def test_append_failure_fails_closed_and_blocks_upstream(upstream, monkeypatch):
    """Canon section 9 / spec 28: a CONFIGURED log whose append fails
    must refuse (REF_PEP_FAIL_CLOSED) and the target must NOT be called
    - do not issue what you cannot record."""

    class FailingLog:
        def append(self, envelope):
            raise IOError("disk full")

    monkeypatch.setattr(pep, "_INJECTED_ISSUANCE_LOG", FailingLog())
    response = client.post("/governed-call", json=_request_body())
    assert response.status_code == 403
    assert response.json()["detail"]["refusal_reason_code"] == "REF_PEP_FAIL_CLOSED"
    assert upstream == []


def test_env_var_wires_without_injection(upstream, monkeypatch, tmp_path):
    """Spec 28: the env seam alone (no injection) logs the issuance -
    the deployment-facing configuration path."""
    path = tmp_path / "env_issued.jsonl"
    monkeypatch.setenv(ISSUANCE_LOG_PATH_ENV, str(path))
    response = client.post("/governed-call", json=_request_body())
    assert response.status_code == 200, response.text
    assert _read_jsonl(path) == [response.json()["envelope"]]


# ---------------------------------------------------------------------------
# End-to-end: the gate's log IS the reconciler's input
# ---------------------------------------------------------------------------


def test_gate_log_reconciles_clean_against_executed_actions(
        upstream, log_file, gate_signing):
    """The VL-099 point, end-to-end: two admitted calls; executed
    actions reconstructed from the captured pushes (what a faithful
    target would log: the delivered interaction + its own identity +
    the envelope's decision_id); reconcile against the gate's issuance
    log with the gate's pinned public key -> clean, 2/2 MATCHED. A
    third, unlogged action -> OUT_OF_SCOPE flips clean to False."""
    for purpose in ("first-call", "second-call"):
        response = client.post(
            "/governed-call", json=_request_body(context={"purpose": purpose}))
        assert response.status_code == 200, response.text

    issued = _read_jsonl(log_file)
    assert len(issued) == 2

    executed = []
    for call in upstream:
        envelope = json.loads(call["headers"]["X-Elyon-Sol-Envelope"])
        executed.append({
            "target_url": call["url"],
            "interaction": call["json"],
            "decision_id": envelope["decision_id"],
        })

    keys = {gate_signing["key_id"]: gate_signing["public_key"]}
    report = reconcile(executed, issued, pinned_public_keys=keys)
    assert [a["verdict"] for a in report["actions"]] == [AUDIT_MATCHED] * 2
    assert report["summary"]["clean"] is True

    rogue = dict(executed[0])
    rogue["decision_id"] = "never-issued"
    report = reconcile(executed + [rogue], issued, pinned_public_keys=keys)
    assert report["actions"][2]["verdict"] == AUDIT_OUT_OF_SCOPE
    assert report["summary"]["clean"] is False
