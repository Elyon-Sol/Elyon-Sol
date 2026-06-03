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


@pytest.mark.xfail(
    reason="DEFAULT_SECURE: mandatory signing cutover not done; pep.py default "
    "forward is unsigned. RED by design until the cutover (canary "
    "test_unsigned_path_unchanged_forge_still_accepted still passes).",
    strict=False,
)
def test_default_forward_is_signed_and_verified():
    # ANCHOR 1 (needs pep.py): run pep.py's DEFAULT forward (no opt-in signing
    # flags) on a benign interaction, capture the emitted envelope, and assert it
    # carries an issuer_signature that verify_envelope() accepts on the default
    # path. When the cutover lands, replace the raise below with that exercise and
    # remove the xfail marker.
    raise AssertionError(
        "DEFAULT_SECURE not wired: pep.py default forward is unsigned "
        "(see blocked_by in EVIDENCE/readiness.json)"
    )


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
