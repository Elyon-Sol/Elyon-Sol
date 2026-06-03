"""The deployment predicates (T-readiness). RED today, by design.

Each is a DECLARED xfail whose reason names its blocker, so the suite stays
green-with-declared-xfail (the red is visible and named, never hidden by a skip).
When the underlying work lands, wire the marked ANCHOR to the real path and REMOVE
the xfail marker, turning the predicate into a true regression gate, and flip the
matching flags in EVIDENCE/readiness.json to value/green true with this test as
the proof.

The bodies fail closed (raise AssertionError) until wired, so an accidental green
cannot slip through. See docs/restructure/10_readiness_spec.md sections 4 and 8.

NOTE: the two ANCHORs below are the only parts of T-readiness that couple to repo
internals (pep.py's default forward and the real transport). They are written
against the envelope/verifier API shapes known from VL-040/041/042 but MUST be
confirmed against pep.py before they exercise the real chain. Until then they are
honest reds, not fiction.
"""

import pytest


def test_default_forward_is_signed_and_verified(gate_signing, monkeypatch):
    # ANCHOR 1 WIRED (VL-047 cutover): pep.py's DEFAULT forward (no opt-in flags)
    # signs the emitted envelope; a co-located target pinning the gate's public
    # key ACCEPTS the signed envelope and REFUSES an unsigned forge. No xfail:
    # this is now a real regression gate. Cross-host transport is NOT asserted
    # here (that is END_TO_END_NO_SHORTCUT / G5); the verifying target is
    # co-located and uses verify_envelope's pinned-key + local-disk reassert
    # path. The gate_signing fixture (TESTS/conftest.py) injects the ephemeral
    # key into pep._get_signing_key.
    import json
    from fastapi.testclient import TestClient

    from IMPLEMENTATION.pep import app as pep_app
    from IMPLEMENTATION.evaluator import manifest_sha256
    from IMPLEMENTATION.verifier import (
        verify_envelope,
        ACCEPT_REASSERTED_AND_BOUND,
    )

    pub = gate_signing["public_key"]
    key_id = gate_signing["key_id"]
    pinned = {key_id: pub}
    target = "https://upstream.example/default-secure-predicate"

    captured = {}

    class _Resp:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None):
        captured["headers"] = headers or {}
        return _Resp()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    interaction = {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }
    resp = TestClient(pep_app).post(
        "/governed-call",
        json={"target_url": target, "interaction": interaction},
    )
    assert resp.status_code == 200

    signed = json.loads(captured["headers"]["X-Elyon-Sol-Envelope"])
    assert signed["issuer_key_id"] == key_id
    assert isinstance(signed["issuer_signature"], str)

    accepted = verify_envelope(signed, interaction, target, pinned_public_keys=pinned)
    assert accepted["accepted"] is True
    assert accepted["reason"] == ACCEPT_REASSERTED_AND_BOUND

    forge = {k: v for k, v in signed.items() if k != "issuer_signature"}
    refused = verify_envelope(forge, interaction, target, pinned_public_keys=pinned)
    assert refused["accepted"] is False


@pytest.mark.xfail(
    reason="END_TO_END_NO_SHORTCUT: transport is a loopback wrapper (G5 open); "
    "no full chain runs without a test-only shortcut. RED by design until real "
    "cross-host transport replaces the stub.",
    strict=False,
)
def test_end_to_end_no_shortcut():
    # ANCHOR 2 (needs pep.py + real transport): drive the whole chain with NO
    # test-only shortcut - caller -> gate -> signed envelope -> TRANSPORT -> target
    # verifies the TRANSPORTED artifact against the published record -> admit/refuse.
    # Forbidden here: hand-built envelopes, in-process key injection bypassing the
    # real key path, a loopback stub for transport, or a target importing gate
    # internals. When real transport lands, implement the exercise and remove xfail.
    raise AssertionError(
        "END_TO_END_NO_SHORTCUT not wired: transport is a loopback stub "
        "(see blocked_by in EVIDENCE/readiness.json)"
    )


@pytest.mark.xfail(
    reason="ROOT_RECOVERY: the planned-rotation + per-root-status mechanism is "
    "BUILT (capability root_rotation.built, proof "
    "TESTS/adversarial/test_root_record.py) but is NOT on pep.py's default path "
    "and NOT transported (G5 open). RED by design until rotation is wired and "
    "transported. Narrowed scope: planned in-band rotation + per-root status only; "
    "root-key COMPROMISE recovery is out-of-band and out of scope.",
    strict=False,
)
def test_root_recovery_wired():
    # ANCHOR 3 (needs pep.py default path + real transport): drive a deployment
    # that consults a validated root_status_view on the DEFAULT path and survives a
    # planned in-band rotation R1 -> R2 over real cross-host transport, with no
    # test-only shortcut. Forbidden here (mirrors ANCHOR 2): hand-built records,
    # in-process key injection, a loopback transport stub, or a target importing
    # reader internals. The mechanism itself is proven by
    # TESTS/adversarial/test_root_record.py and EVIDENCE/proofs/root_record_001_runner.py
    # (the capability proof); this ANCHOR is the WIRING gate, red until the default
    # path and transport land. When they do, implement the exercise and remove xfail.
    raise AssertionError(
        "ROOT_RECOVERY not wired: root-status consultation is target-side posture, "
        "not on pep.py's default path, and transport is a loopback stub "
        "(see blocked_by in EVIDENCE/readiness.json)"
    )
