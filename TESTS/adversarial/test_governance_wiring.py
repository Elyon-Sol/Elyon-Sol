"""
Tests for the high-impact deployment-wiring guard (white-box review findings
G-01/G-03/G-04/G-06). Repo path: TESTS/adversarial/test_governance_wiring.py.

assert_high_impact_wiring fails the gate CLOSED at startup when the SHA-pinned
manifest declares HIGH_IMPACT actions but oversight is not safely wired; it is a
NO-OP for the default HIGH_IMPACT:[] manifest. Each Gxx test is a revert-catcher:
remove the corresponding check in governance_wiring.py and that test goes RED.
"""

import pytest

from IMPLEMENTATION.governance_wiring import (
    assert_high_impact_wiring,
    high_impact_declared,
    APPROVER_PROV_SIGNED_CHAIN,
    APPROVER_PROV_INJECTED,
    APPROVER_PROV_STATIC_PIN,
    APPROVER_PROV_NONE,
)

# A manifest that DECLARES a high-impact action (token in AR u R, so safe_high_impact
# returns a non-empty set per [FIX H2]).
HI = {"version": "1.0", "AR": ["identity", "role"], "R": ["session", "request"],
      "HIGH_IMPACT": ["role"]}
# The default/live manifest: an explicit empty opt-out.
EMPTY = {"version": "1.0", "AR": ["identity", "role"], "R": ["session", "request"],
         "HIGH_IMPACT": []}

KEYS = {"approver-1": object()}   # a non-empty approver map (values not inspected)


def _ok_kwargs(**over):
    base = dict(
        manifest=HI,
        approver_keys=KEYS,
        approver_provenance=APPROVER_PROV_SIGNED_CHAIN,  # the only provenance that passes G-01
        approval_log_configured=True,
        pending_redis_url=None,
        replay_redis_url=None,
    )
    base.update(over)
    return base


# --------------------------------------------------------------------------
# high_impact_declared
# --------------------------------------------------------------------------

def test_declared_true_for_nonempty():
    assert high_impact_declared(HI) is True

def test_declared_false_for_explicit_empty():
    assert high_impact_declared(EMPTY) is False

def test_declared_true_for_missing_or_malformed():
    assert high_impact_declared({"version": "1.0", "AR": ["a"], "R": ["b"]}) is True   # missing
    assert high_impact_declared({"HIGH_IMPACT": "not-a-list"}) is True                  # malformed
    assert high_impact_declared("not-a-dict") is True


# --------------------------------------------------------------------------
# The default path is unconstrained (byte-behavior-unchanged)
# --------------------------------------------------------------------------

def test_empty_high_impact_is_noop_even_with_all_bad_wiring():
    # Every wiring input is "unsafe", but with no high-impact action declared the
    # guard must NOT fire - the default deployment is unaffected.
    assert_high_impact_wiring(
        manifest=EMPTY,
        approver_keys={},
        approver_provenance=APPROVER_PROV_NONE,
        approval_log_configured=False,
        pending_redis_url="redis://x",
        replay_redis_url=None,
    )  # no raise


# --------------------------------------------------------------------------
# Safe high-impact wiring passes
# --------------------------------------------------------------------------

def test_safe_wiring_ok():
    assert_high_impact_wiring(**_ok_kwargs())                       # neither redis
    assert_high_impact_wiring(**_ok_kwargs(pending_redis_url="redis://x",
                                           replay_redis_url="redis://x"))  # both redis


# --------------------------------------------------------------------------
# Revert-catchers, one per finding
# --------------------------------------------------------------------------

def test_G01_static_pin_refused():
    with pytest.raises(RuntimeError) as e:
        assert_high_impact_wiring(**_ok_kwargs(approver_provenance=APPROVER_PROV_STATIC_PIN))
    assert "G-01" in str(e.value)

def test_G01_injected_refused_GL01_refine():
    # THE load-bearing GL-01-refine (VL-124) catcher. Before this increment the
    # guard accepted an INJECTED map (approver_from_injected=True). Injectedness is
    # not provenance: a process that can set the injection seam can supply any
    # gate-controlled keys under a different key_id. Only SIGNED_CHAIN passes now.
    # Revert = accept 'injected' at G-01 -> this goes RED.
    with pytest.raises(RuntimeError) as e:
        assert_high_impact_wiring(**_ok_kwargs(approver_provenance=APPROVER_PROV_INJECTED))
    assert "G-01" in str(e.value)

def test_G01_none_provenance_refused():
    with pytest.raises(RuntimeError) as e:
        assert_high_impact_wiring(**_ok_kwargs(approver_provenance=APPROVER_PROV_NONE))
    assert "G-01" in str(e.value)

def test_G01_signed_chain_is_the_only_pass():
    # Positive: signed-chain provenance with the rest wired is accepted.
    assert_high_impact_wiring(**_ok_kwargs(approver_provenance=APPROVER_PROV_SIGNED_CHAIN))

def test_G06_empty_approver_map_refused():
    with pytest.raises(RuntimeError) as e:
        assert_high_impact_wiring(**_ok_kwargs(approver_keys={}))
    assert "G-06" in str(e.value)

def test_G04_no_approval_log_refused():
    with pytest.raises(RuntimeError) as e:
        assert_high_impact_wiring(**_ok_kwargs(approval_log_configured=False))
    assert "G-04" in str(e.value)

def test_G03_pending_without_replay_refused():
    with pytest.raises(RuntimeError) as e:
        assert_high_impact_wiring(**_ok_kwargs(pending_redis_url="redis://x",
                                               replay_redis_url=None))
    assert "G-03" in str(e.value)

def test_G03_replay_without_pending_refused():
    with pytest.raises(RuntimeError) as e:
        assert_high_impact_wiring(**_ok_kwargs(pending_redis_url=None,
                                               replay_redis_url="redis://x"))
    assert "G-03" in str(e.value)

def test_malformed_high_impact_fails_closed():
    # missing HIGH_IMPACT -> declared True -> bad wiring must raise (fail-closed)
    with pytest.raises(RuntimeError):
        assert_high_impact_wiring(
            manifest={"version": "1.0", "AR": ["identity"], "R": ["session"]},
            approver_keys={}, approver_provenance=APPROVER_PROV_STATIC_PIN,
            approval_log_configured=False, pending_redis_url=None, replay_redis_url=None,
        )

def test_multiple_problems_reported_together():
    with pytest.raises(RuntimeError) as e:
        assert_high_impact_wiring(
            manifest=HI, approver_keys={}, approver_provenance=APPROVER_PROV_STATIC_PIN,
            approval_log_configured=False, pending_redis_url="redis://x", replay_redis_url=None,
        )
    msg = str(e.value)
    assert all(g in msg for g in ("G-01", "G-06", "G-04", "G-03"))


def test_default_app_startup_hook_does_not_raise():
    # Firing the REAL pep startup hook on the default app (repo manifest is
    # HIGH_IMPACT:[]) must not raise - proves the guard does not break the
    # default/live deployment.
    from fastapi.testclient import TestClient
    import IMPLEMENTATION.pep as pep
    with TestClient(pep.app):
        pass
