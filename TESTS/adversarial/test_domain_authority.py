"""STAIRCASE S2 - domain-authority trust (role-distinctness from the signed chain).

resolve_domain_authority_keys mirrors approver_trust.resolve_approver_keys: only a
key whose signed record-role is exactly `domain_authority`, not revoked, in-window,
and != gate_key_id is eligible to sign a domain-verdict. Issuer/approver/role-less
keys are structurally excluded. Feeds domain_verdict/domain_control. Unwired.
"""
import inspect
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from IMPLEMENTATION.domain_authority import (
    resolve_domain_authority_keys, DOMAIN_AUTHORITY_ROLE,
)
from IMPLEMENTATION.approver_trust import APPROVER_ROLE, ISSUER_ROLE
from IMPLEMENTATION.domain_control import control, CONTROL_PASS
from IMPLEMENTATION.domain_verdict import build_verdict, sign_verdict, VERDICT_SAFE

GATE_KEY_ID = "ELYON_GATE_1"
AUTH_KEY_ID = "ELYON_DOMAIN_AUTH_1"


def _pk():
    return Ed25519PrivateKey.generate().public_key()


def _entry(role, *, revoked=False, before_s=-60, after_s=600, public_key=None):
    now = datetime.now(timezone.utc)
    return {
        "public_key": public_key if public_key is not None else _pk(),
        "role": role,
        "revoked": revoked,
        "not_before": now + timedelta(seconds=before_s),
        "not_after": now + timedelta(seconds=after_s),
    }


def test_only_domain_authority_role_is_eligible():
    pk = _pk()
    view = {
        AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, public_key=pk),
        "an_approver": _entry(APPROVER_ROLE),
        "an_issuer": _entry(ISSUER_ROLE),
        "role_less": _entry(None),
    }
    out = resolve_domain_authority_keys(view, gate_key_id=GATE_KEY_ID)
    assert out == {AUTH_KEY_ID: pk}   # approver/issuer/role-less all excluded


def test_role_tokens_are_mutually_distinct():
    assert len({DOMAIN_AUTHORITY_ROLE, APPROVER_ROLE, ISSUER_ROLE}) == 3


def test_revoked_excluded():
    view = {AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, revoked=True)}
    assert resolve_domain_authority_keys(view) == {}


def test_expired_and_not_yet_valid_excluded():
    assert resolve_domain_authority_keys({AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, after_s=-1)}) == {}
    assert resolve_domain_authority_keys({AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, before_s=60)}) == {}


def test_gate_key_id_excluded_belt_and_braces():
    view = {GATE_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE)}
    assert resolve_domain_authority_keys(view, gate_key_id=GATE_KEY_ID) == {}


def test_clock_skew_widens_window():
    view = {AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, after_s=-2)}
    assert resolve_domain_authority_keys(view, clock_skew=timedelta(seconds=10)) != {}


def test_non_dict_view_and_malformed_entries_yield_empty():
    assert resolve_domain_authority_keys("nope") == {}
    assert resolve_domain_authority_keys({AUTH_KEY_ID: "not-a-dict"}) == {}
    bad = {AUTH_KEY_ID: {"role": DOMAIN_AUTHORITY_ROLE, "revoked": False,
                         "not_before": "not-a-dt", "not_after": "not-a-dt", "public_key": _pk()}}
    assert resolve_domain_authority_keys(bad) == {}


def test_negative_clock_skew_raises():
    with pytest.raises(ValueError):
        resolve_domain_authority_keys({}, clock_skew=timedelta(seconds=-1))


def test_resolved_map_drives_domain_control_end_to_end():
    # S2 -> S4 integration: a role-vetted key from the signed chain lets a
    # verdict it signed pass domain_control (the trust map is NOT hand-built).
    sk = Ed25519PrivateKey.generate()
    view = {AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, public_key=sk.public_key())}
    trusted = resolve_domain_authority_keys(view, gate_key_id=GATE_KEY_ID)

    decision = "d" * 64
    manifest = {"version": "1.0", "domains": {"healthcare_admin": {
        "predicates": [{"path": "record_basis", "rule": "present"}],
        "requires_verdict": True, "authority_key_id": AUTH_KEY_ID}}}
    ctx = {"domain": "healthcare_admin", "context": {"record_basis": "chart-1"}}
    v = sign_verdict(build_verdict(decision_sha256=decision, domain="healthcare_admin",
                                   verdict=VERDICT_SAFE, verdict_id="vd-1",
                                   not_after=datetime.now(timezone.utc) + timedelta(seconds=300)),
                     sk, AUTH_KEY_ID)
    out, code, _ = control(ctx, manifest, verdict=v, expected_decision_sha256=decision,
                           authority_public_keys=trusted, gate_key_id=GATE_KEY_ID)
    assert out == CONTROL_PASS and code is None


def test_module_unwired():
    from IMPLEMENTATION import evaluator, pep
    for mod in (evaluator, pep):
        assert "domain_authority" not in inspect.getsource(mod)
