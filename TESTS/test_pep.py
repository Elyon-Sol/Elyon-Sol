import json

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
#
# VL-038: the ELIGIBLE forward now PUSHES the envelope as the out-of-band
# attestation header X-Elyon-Sol-Envelope (canonical_json of the envelope);
# the forwarded body is unchanged (normalized_interaction). The fake_post
# stubs below therefore accept a `headers` kwarg, and the ELIGIBLE tests
# assert the envelope rides in that header. End-to-end target-side
# enforcement (an enforcing target refusing direct / forged / replayed /
# mismatched calls, verified against EVIDENCE/published_hashes.json) lives
# in TESTS/adversarial/test_enforcement.py.
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

    def fake_post(url, json, timeout, headers=None):
        calls.append({"url": url, "json": json, "timeout": timeout, "headers": headers})
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

    VL-038: the forward MUST carry the envelope in the X-Elyon-Sol-Envelope
    header, and the body MUST remain the bare normalized_interaction (so a
    routed call and a direct call differ only by the header).
    """
    calls = []

    class FakeResponse:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout, headers=None):
        calls.append({
            "url": url,
            "json": json,
            "timeout": timeout,
            "headers": headers,
        })
        return FakeResponse()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    target = "https://upstream.example/test"
    response = client.post(
        "/governed-call",
        json={
            "target_url": target,
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

    # VL-038: the forwarded body is unchanged (the bare interaction), and
    # the envelope rides in the attestation header.
    forwarded = calls[0]
    assert "envelope" not in forwarded["json"], (
        "forwarded body must remain the bare interaction; the envelope "
        "rides in the X-Elyon-Sol-Envelope header, not the body"
    )
    assert forwarded["headers"] is not None
    assert "X-Elyon-Sol-Envelope" in forwarded["headers"]
    pushed_envelope = json.loads(forwarded["headers"]["X-Elyon-Sol-Envelope"])
    assert pushed_envelope["decision"] == "ELIGIBLE"
    assert pushed_envelope["target_url"] == target


def test_governed_call_upstream_error_fails_closed(monkeypatch):
    """
    Fail-closed on upstream error: valid schema, valid evaluation, ELIGIBLE
    reached; the upstream call raises TimeoutError. The PEP MUST convert
    this to a 403 REFUSE with REF_PEP_FAIL_CLOSED.
    """
    def fake_post(url, json, timeout, headers=None):
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

    def fake_post(url, json, timeout, headers=None):
        calls.append({"url": url, "json": json, "timeout": timeout, "headers": headers})
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


# ----------------------------------------------------------------------------
# VL-029: envelope emitted on ELIGIBLE per artifact 05 build-order step 5.
# Test verifies the response shape locked by Decision E SD-3-a:
# {"decision": "ELIGIBLE", "envelope": <envelope>}. The envelope's
# structural invariants (10 top-level keys; condition_results.ccs is None
# on first issuance per VL-028 spec; ac3/t26/manifest_integrity all True
# on the ELIGIBLE path per Decision C1) are asserted here.
#
# Per VL-028 opener constraint (i) carried forward: no hash-value pinning
# (decision_sha256 and the various sha256 fields are verified for shape
# only, not value).
#
# VL-038: extended to assert the envelope returned to the caller is the
# same envelope pushed to the target in the X-Elyon-Sol-Envelope header.
# ----------------------------------------------------------------------------


# Duplicated locally from TESTS/adversarial/test_envelope.py per the
# established "self-contained adversarial test files" precedent. The
# single source of truth is docs/restructure/05_admissibility_envelope_spec.md.
EXPECTED_ENVELOPE_TOP_KEYS = {
    "envelope_version",
    "decision",
    "target_url",
    "canon",
    "evaluated_against",
    "request_context",
    "evaluator",
    "condition_results",
    "decision_sha256",
    "timestamp_utc",
}


def test_pep_eligible_response_contains_envelope(monkeypatch):
    """
    Post-VL-029: ELIGIBLE response carries an envelope per artifact 05
    build-order step 5 + Decision E SD-3-a. Verifies the response shape
    ({"decision": "ELIGIBLE", "envelope": <envelope>}) and the envelope's
    structural invariants; does NOT pin specific hash values per the
    inherited constraint (i).

    VL-038: also verifies the response envelope is byte-identical (via
    canonical_json) to the envelope pushed to the target in the
    X-Elyon-Sol-Envelope header.
    """
    calls = []

    class FakeResponse:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout, headers=None):
        calls.append({"url": url, "json": json, "timeout": timeout, "headers": headers})
        return FakeResponse()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    target = "https://upstream.example/envelope-test"
    response = client.post(
        "/governed-call",
        json={
            "target_url": target,
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": "1.0",
                "expected_manifest_sha256": SHA
            }
        }
    )

    # Upstream still called exactly once (no regression vs
    # test_governed_call_eligible_forwards_once).
    assert response.status_code == 200
    assert len(calls) == 1

    body = response.json()

    # Top-level response shape per Decision E SD-3-a.
    assert body["decision"] == "ELIGIBLE"
    assert "envelope" in body

    env = body["envelope"]

    # Envelope structure (artifact 05 "Envelope structure" JSON block).
    assert set(env.keys()) == EXPECTED_ENVELOPE_TOP_KEYS, (
        f"envelope top-level keys diverge; "
        f"missing={EXPECTED_ENVELOPE_TOP_KEYS - set(env.keys())}, "
        f"extra={set(env.keys()) - EXPECTED_ENVELOPE_TOP_KEYS}"
    )

    # Envelope-level values determined by the test input.
    assert env["decision"] == "ELIGIBLE"
    assert env["target_url"] == target

    # condition_results: ELIGIBLE path means ac3/t26/manifest_integrity
    # all True per Decision C1 invariant; ccs is None on first issuance
    # per VL-028 spec (post-VL-026 Open question 1 resolution).
    cr = env["condition_results"]
    assert cr["ac3"] is True
    assert cr["t26"] is True
    assert cr["manifest_integrity"] is True
    assert cr["ccs"] is None

    # decision_sha256 shape (no value pinning per constraint (i)).
    assert isinstance(env["decision_sha256"], str)
    assert len(env["decision_sha256"]) == 64
    assert all(c in "0123456789abcdef" for c in env["decision_sha256"])

    # VL-038: the envelope pushed to the target equals the envelope
    # returned to the caller (same decision artifact on both paths).
    from IMPLEMENTATION.envelope import canonical_json
    pushed = json.loads(calls[0]["headers"]["X-Elyon-Sol-Envelope"])
    assert canonical_json(pushed) == canonical_json(env)
