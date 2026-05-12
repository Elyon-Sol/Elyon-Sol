from fastapi.testclient import TestClient
from IMPLEMENTATION.pep import app

client = TestClient(app)

SHA = "a21dea8b79d459bd700ca44a30c2ca4a6efbee1447708cbc12c0bbb322d823b8"


def test_governed_call_refuse_blocks_upstream():
    response = client.post(
        "/governed-call",
        json={
            "target_url": "https://upstream.example/refuse",
            "context": {
                "AP": [],
                "OP": [],
                "ccs_valid": False,
                "expected_manifest_version": "1.0",
                "expected_manifest_sha256": SHA
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
                "expected_manifest_version": "1.0",
                "expected_manifest_sha256": SHA
            }
        }
    )

    assert response.status_code == 200
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
                "expected_manifest_version": "1.0",
                "expected_manifest_sha256": SHA
            }
        }
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["terminal_state"] == "REFUSE"


def test_governed_call_manifest_version_drift_refuses():
    response = client.post(
        "/governed-call",
        json={
            "target_url": "https://upstream.example/drift",
            "context": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "ccs_valid": True,
                "expected_manifest_version": "2.0",
                "expected_manifest_sha256": SHA
            }
        }
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["terminal_state"] == "REFUSE"
