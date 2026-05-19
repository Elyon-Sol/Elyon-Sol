from fastapi.testclient import TestClient
from IMPLEMENTATION.pep import app

client = TestClient(app)

SHA = "a21dea8b79d459bd700ca44a30c2ca4a6efbee1447708cbc12c0bbb322d823b8"


# ----------------------------------------------------------------------------
# These tests exercise PEP-layer behavior downstream of schema validation:
# evaluator-layer REFUSE, ELIGIBLE forwarding, upstream fail-closed, and
# manifest-integrity REFUSE. The wire shape is the post-VL-019 canonical
# envelope {target_url, interaction}; tests of the schema layer itself live
# in TESTS/adversarial/test_request_schema.py.
#
# Each test that exercises an evaluator-layer REFUSE asserts that
# requests.post was NOT called (canon section 9 fail-closed; upstream is
# never reached on REFUSE). This was implicit before VL-019 but is asserted
# explicitly here to prevent silent coverage loss if the wire-shape boundary
# changes again.
# ----------------------------------------------------------------------------


def test_governed_call_refuse_blocks_upstream(monkeypatch):
    """
    Evaluator-layer REFUSE: AP and OP are empty arrays; the request passes
    schema validation (envelope shape is valid) but fails AC^3 and T^26
    inside evaluate(). Upstream MUST NOT be reached.
    """
    calls = []

    class FakeResponse:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout):
        calls.append({"url": url, "json": json, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    response = client.post(
        "/governed-call",
        json={
            "target_url": "https://upstream.example/refuse",
            "interaction": {
                "AP": [],
                "OP": [],
                "context": {},
                "expected_manifest_version": "1.0",
                "expected_manifest_sha256": SHA
            }
        }
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["terminal_state"] == "REFUSE"
    assert calls == [], (
        f"evaluator-layer REFUSE must not forward to target_url; "
        f"upstream was called: {calls}"
    )


def test_governed_call_eligible_forwards_once(monkeypatch):
    """
    ELIGIBLE path: valid schema, valid AC^3/T^26, valid manifest pinning.
    Upstream MUST be called exactly once.
    """
    calls = []

    class FakeResponse:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout):
        calls.append({
            "url": url,
            "json": json,
            "timeout": timeout
        })
        return FakeResponse()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    response = client.post(
        "/governed-call",
        json={
            "target_url": "https://upstream.example/test",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": "1.0",
                "expected_manifest_sha256": SHA
            }
        }
    )

    assert response.status_code == 200
    assert len(calls) == 1


def test_governed_call_upstream_error_fails_closed(monkeypatch):
    """
    Fail-closed on upstream error: valid schema, valid evaluation, ELIGIBLE
    reached; the upstream call raises TimeoutError. The PEP MUST convert
    this to a 403 REFUSE with REF_PEP_FAIL_CLOSED.
    """
    def fake_post(url, json, timeout):
        raise TimeoutError("upstream timeout")

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    response = client.post(
        "/governed-call",
        json={
            "target_url": "https://upstream.example/timeout",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": "1.0",
                "expected_manifest_sha256": SHA
            }
        }
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["terminal_state"] == "REFUSE"


def test_governed_call_manifest_version_drift_refuses(monkeypatch):
    """
    Manifest-integrity REFUSE: valid schema (the version field is a valid
    string), but the asserted version "2.0" does not match the live manifest
    version "1.0". manifest_integrity_valid() returns False; evaluate()
    returns REFUSE; upstream MUST NOT be reached.
    """
    calls = []

    class FakeResponse:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout):
        calls.append({"url": url, "json": json, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    response = client.post(
        "/governed-call",
        json={
            "target_url": "https://upstream.example/drift",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": "2.0",
                "expected_manifest_sha256": SHA
            }
        }
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["terminal_state"] == "REFUSE"
    assert calls == [], (
        f"manifest-integrity REFUSE must not forward to target_url; "
        f"upstream was called: {calls}"
    )
