from fastapi.testclient import TestClient
from IMPLEMENTATION.pep import app

client = TestClient(app)


def test_governed_call_refuse_blocks_upstream():
    response = client.post(
        "/governed-call",
        json={
            "target_url": "https://example.invalid/should-not-be-called",
            "context": {
                "AP": [],
                "OP": [],
                "ccs_valid": False,
                "expected_manifest_version": "1.0"
            }
        }
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["terminal_state"] == "REFUSE"


def test_governed_call_eligible_forwards_once(monkeypatch):
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
            "context": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "ccs_valid": True,
                "expected_manifest_version": "1.0"
            }
        }
    )

    assert response.status_code == 200
    body = response.json()

    assert body["terminal_state"] == "ELIGIBLE"
    assert body["upstream_status"] == 200
    assert len(calls) == 1


def test_governed_call_upstream_error_fails_closed(monkeypatch):
    def fake_post(url, json, timeout):
        raise TimeoutError("upstream timeout")

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    response = client.post(
        "/governed-call",
        json={
            "target_url": "https://upstream.example/timeout",
            "context": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "ccs_valid": True,
                "expected_manifest_version": "1.0"
            }
        }
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["terminal_state"] == "REFUSE"
    assert body["detail"]["refusal_reason_code"] == "REF_PEP_FAIL_CLOSED"


def test_governed_call_manifest_version_drift_refuses(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append(url)
        raise AssertionError("should not be called")

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    response = client.post(
        "/governed-call",
        json={
            "target_url": "https://upstream.example/should-not-run",
            "context": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "ccs_valid": True,
                "expected_manifest_version": "0.9"
            }
        }
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["terminal_state"] == "REFUSE"
    assert calls == []
