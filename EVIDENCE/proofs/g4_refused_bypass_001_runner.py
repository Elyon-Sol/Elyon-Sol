"""
Evidence-run generator for G4 refused-bypass (VL-038).

Produces EVIDENCE/proofs/g4_refused_bypass_001.log. Drives the full
two-hop path through the real FastAPI request/response cycle (in-process
TestClient): a valid call routed through the PEP is HONORED by an
enforcing target; direct / forged / replayed / target_url-mismatched /
published-record-mismatched calls are REFUSED (non-200) and the target
does not act. Verification is anchored to the committed
EVIDENCE/published_hashes.json (the published record), so the verdicts
are reproducible by anyone who clones the repo and re-runs this script.

This differs from g3 (VL-030), whose third-party observation was an
external webhook: g4's defensibility is the committed, hash-locked
published record, reproducible offline. Cross-host real-HTTP TRANSPORT of
that record is named, not built (after VL-038).

Run from repo root:  PYTHONPATH=. python3 EVIDENCE/proofs/g4_refused_bypass_001_runner.py
"""

import json

import IMPLEMENTATION.pep as pep_module
from fastapi.testclient import TestClient

from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.evaluator import manifest_sha256
from TESTS.adversarial.test_enforcement import (
    TARGET_URL,
    REF_TARGET_PUBLISHED_RECORD_MISMATCH,
    build_enforcing_target_app,
    load_published_hashes,
    _build_valid_envelope,
    _normalized_interaction,
)


def _route_through_pep_capture_push(interaction_body, target_url):
    """POST a valid call to the PEP; capture the pushed forward (the PEP's
    requests.post is replaced so nothing leaves the process)."""
    captured = {}

    class _Resp:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout, headers=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers or {}
        return _Resp()

    original = pep_module.requests.post
    pep_module.requests.post = fake_post
    try:
        client = TestClient(pep_module.app)
        resp = client.post(
            "/governed-call",
            json={"target_url": target_url, "interaction": interaction_body},
        )
    finally:
        pep_module.requests.post = original
    return resp, captured


def _deliver(target_client, interaction, envelope_header=None):
    headers = {}
    if envelope_header is not None:
        headers["X-Elyon-Sol-Envelope"] = envelope_header
    return target_client.post("/act", json=interaction, headers=headers)


def main():
    published = load_published_hashes()

    print("=" * 70)
    print("Elyon-Sol G4 refused-bypass evidence run (VL-038)")
    print("=" * 70)
    print("Published record anchor (EVIDENCE/published_hashes.json):")
    print("  canon_sha256     = " + published["canon_sha256"])
    print("  evaluator_sha256 = " + published["evaluator_sha256"])
    print("  manifest_sha256  = " + published["manifest_sha256"])
    print("Verification is against this committed record, not target-local disk.")
    print("-" * 70)

    target_app, received = build_enforcing_target_app(published, TARGET_URL)
    target_client = TestClient(target_app)

    results = []

    def record(case, status, acted, reason):
        results.append((case, status, acted, reason))
        print(
            "{:38s} status={:3d}  acted={:5s}  reason={}".format(
                case, status, str(acted), reason
            )
        )

    # ----- ACCEPT: valid call routed through the gate -----
    valid_interaction = {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }
    pep_resp, captured = _route_through_pep_capture_push(valid_interaction, TARGET_URL)
    before = len(received)
    tr = _deliver(
        target_client,
        captured["json"],
        captured["headers"]["X-Elyon-Sol-Envelope"],
    )
    acted = len(received) > before
    record(
        "ACCEPT routed valid (end-to-end)",
        tr.status_code,
        acted,
        tr.json().get("reason"),
    )

    # ----- REFUSE A1: direct call, no envelope header -----
    before = len(received)
    tr = _deliver(target_client, _normalized_interaction(), None)
    acted = len(received) > before
    record("REFUSE A1 direct (no envelope)", tr.status_code, acted,
           tr.json()["detail"]["reason"])

    # ----- REFUSE A2: forged envelope (tampered, no rehash) -----
    env = _build_valid_envelope()
    env["request_context"]["AP"] = ["identity", "role", "admin"]
    before = len(received)
    tr = _deliver(target_client, _normalized_interaction(), canonical_json(env))
    acted = len(received) > before
    record("REFUSE A2 forged (tamper)", tr.status_code, acted,
           tr.json()["detail"]["reason"])

    # ----- REFUSE A3: replayed envelope, binding mismatch -----
    env_x = _build_valid_envelope(interaction=_normalized_interaction(ap=["identity", "role"]))
    interaction_y = _normalized_interaction(ap=["identity", "role", "admin"])
    before = len(received)
    tr = _deliver(target_client, interaction_y, canonical_json(env_x))
    acted = len(received) > before
    record("REFUSE A3 replay (binding mismatch)", tr.status_code, acted,
           tr.json()["detail"]["reason"])

    # ----- REFUSE: target_url mismatch -----
    other_app, other_received = build_enforcing_target_app(
        published, expected_target_url="http://127.0.0.1:9000/other"
    )
    other_client = TestClient(other_app)
    interaction = _normalized_interaction()
    env = _build_valid_envelope(interaction=interaction, target_url=TARGET_URL)
    before = len(other_received)
    tr = _deliver(other_client, interaction, canonical_json(env))
    acted = len(other_received) > before
    record("REFUSE target_url mismatch", tr.status_code, acted,
           tr.json()["detail"]["reason"])

    # ----- REFUSE: envelope pins do not match the published record -----
    # (passes local-disk reassert + binding; refused by the published check)
    divergent = dict(published)
    divergent["canon_sha256"] = "0" * 64
    div_app, div_received = build_enforcing_target_app(divergent, TARGET_URL)
    div_client = TestClient(div_app)
    interaction = _normalized_interaction()
    env = _build_valid_envelope(interaction=interaction)
    before = len(div_received)
    tr = _deliver(div_client, interaction, canonical_json(env))
    acted = len(div_received) > before
    record("REFUSE published-record mismatch", tr.status_code, acted,
           tr.json()["detail"]["reason"])

    print("-" * 70)
    honored = [r for r in results if r[1] == 200]
    refused = [r for r in results if r[1] != 200]
    acted_count = sum(1 for r in results if r[2])
    print(
        "Summary: {} honored (200, acted), {} refused (non-200, not acted), "
        "{} total target actions.".format(len(honored), len(refused), acted_count)
    )
    # Invariants the run asserts:
    assert len(honored) == 1, "exactly one honored call expected"
    assert acted_count == 1, "the target must act exactly once (the honored call)"
    assert all(r[1] == 403 and r[2] is False for r in refused), (
        "every refused call must be 403 and must not act"
    )
    print("Invariants hold: 1 honored+acted; 5 refused (403) with 0 target actions.")


if __name__ == "__main__":
    main()
