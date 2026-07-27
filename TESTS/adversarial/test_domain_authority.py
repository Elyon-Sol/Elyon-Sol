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
    PROVENANCE_SIGNED_KEY_RECORD,
)


def _resolve(view, **kw):
    """Resolve with the provenance assertion supplied (H1). Tests that exercise
    the assertion itself call resolve_domain_authority_keys directly."""
    kw.setdefault("provenance", PROVENANCE_SIGNED_KEY_RECORD)
    return resolve_domain_authority_keys(view, **kw)
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
    out = _resolve(view, gate_key_id=GATE_KEY_ID)
    assert out == {AUTH_KEY_ID: pk}   # approver/issuer/role-less all excluded


def test_role_tokens_are_mutually_distinct():
    assert len({DOMAIN_AUTHORITY_ROLE, APPROVER_ROLE, ISSUER_ROLE}) == 3


def test_revoked_excluded():
    view = {AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, revoked=True)}
    assert _resolve(view) == {}


def test_expired_and_not_yet_valid_excluded():
    assert _resolve({AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, after_s=-1)}) == {}
    assert _resolve({AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, before_s=60)}) == {}


def test_gate_key_id_excluded_belt_and_braces():
    view = {GATE_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE)}
    assert _resolve(view, gate_key_id=GATE_KEY_ID) == {}


def test_clock_skew_widens_window():
    view = {AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, after_s=-2)}
    assert _resolve(view, clock_skew=timedelta(seconds=10)) != {}


def test_non_dict_view_and_malformed_entries_yield_empty():
    assert _resolve("nope") == {}
    assert _resolve({AUTH_KEY_ID: "not-a-dict"}) == {}
    bad = {AUTH_KEY_ID: {"role": DOMAIN_AUTHORITY_ROLE, "revoked": False,
                         "not_before": "not-a-dt", "not_after": "not-a-dt", "public_key": _pk()}}
    assert _resolve(bad) == {}


def test_negative_clock_skew_raises():
    with pytest.raises(ValueError):
        _resolve({}, clock_skew=timedelta(seconds=-1))


def test_resolved_map_drives_domain_control_end_to_end():
    # S2 -> S4 integration: a role-vetted key from the signed chain lets a
    # verdict it signed pass domain_control (the trust map is NOT hand-built).
    sk = Ed25519PrivateKey.generate()
    view = {AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, public_key=sk.public_key())}
    trusted = _resolve(view, gate_key_id=GATE_KEY_ID)

    decision = "d" * 64
    manifest = {"version": "1.0", "domains": {"healthcare_admin": {
        "predicates": [{"path": "record_basis", "rule": "present"}],
        "interaction_types": ["chart_write"],
        "requires_verdict": True, "authority_key_id": AUTH_KEY_ID}}}
    ctx = {"domain": "healthcare_admin", "interaction_type": "chart_write",
           "context": {"record_basis": "chart-1"}}
    v = sign_verdict(build_verdict(decision_sha256=decision, domain="healthcare_admin",
                                   verdict=VERDICT_SAFE, verdict_id="vd-1",
                                   not_after=datetime.now(timezone.utc) + timedelta(seconds=300)),
                     sk, AUTH_KEY_ID)
    out, code, _ = control(ctx, manifest, verdict=v, expected_decision_sha256=decision,
                           authority_public_keys=trusted, gate_key_id=GATE_KEY_ID)
    assert out == CONTROL_PASS and code is None


# --- H1 (cross-model review): provenance assertion is mandatory --------------

def test_H1_missing_provenance_yields_no_keys():
    """A hand-built dict that was never validated must not become a trust map
    just because it is shaped like one. Omitting the assertion returns {}."""
    view = {AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE)}
    assert resolve_domain_authority_keys(view, gate_key_id=GATE_KEY_ID) == {}


@pytest.mark.parametrize("bad", [None, "", "validated", "signed", "SIGNED_KEY_RECORD"])
def test_H1_wrong_provenance_token_yields_no_keys(bad):
    view = {AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE)}
    assert resolve_domain_authority_keys(view, provenance=bad) == {}


def test_H1_correct_provenance_resolves():
    pk = _pk()
    view = {AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, public_key=pk)}
    out = resolve_domain_authority_keys(view, provenance=PROVENANCE_SIGNED_KEY_RECORD)
    assert out == {AUTH_KEY_ID: pk}


# --- H1b: `revoked` must be explicitly False (stricter than approver_trust) ---

@pytest.mark.parametrize("revoked_value", [None, "no", "false", 0, "yes", 1])
def test_H1b_non_bool_revoked_is_malformed_and_excluded(revoked_value):
    """A view carrying revoked: "yes" (or a missing key) must not resolve to an
    ACTIVE key via an `is True` test that only catches the literal True."""
    e = _entry(DOMAIN_AUTHORITY_ROLE)
    if revoked_value is None:
        del e["revoked"]
    else:
        e["revoked"] = revoked_value
    assert _resolve({AUTH_KEY_ID: e}) == {}


def test_H1b_revoked_false_resolves():
    assert _resolve({AUTH_KEY_ID: _entry(DOMAIN_AUTHORITY_ROLE, revoked=False)}) != {}


def test_not_wired_into_evaluator_canon_boundary():
    from IMPLEMENTATION import evaluator
    assert "domain_authority" not in inspect.getsource(evaluator)
