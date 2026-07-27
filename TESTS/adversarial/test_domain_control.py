"""STAIRCASE S4 (+ S3 schema) - the domain-control state machine.

control() composes D-structural validity (domain_validity.assess) with the
out-of-band domain-verdict (domain_verdict.verify_verdict) and returns one of
PASS / HOLD_FOR_VERDICT / HOLD_FOR_HIL / REFUSE. It is PURE given its inputs -
the verdict is passed IN, never fetched (the determinism firewall). Build-then-
wire: no caller on the default path; frozen core untouched.
"""
import inspect
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from IMPLEMENTATION.domain_control import (
    control, CONTROL_PASS, CONTROL_HOLD_FOR_VERDICT, CONTROL_HOLD_FOR_HIL, CONTROL_REFUSE,
    D_VERDICT_REQUIRED, D_VERDICT_UNVERIFIED, D_VERDICT_UNSAFE,
)
from IMPLEMENTATION.domain_validity import safe_domain_manifest, D_FIELD_ABSENT
from IMPLEMENTATION.domain_verdict import build_verdict, sign_verdict, VERDICT_SAFE, VERDICT_UNSAFE

DECISION = "d" * 64
GATE_KEY_ID = "ELYON_GATE_1"
AUTH_KEY_ID = "ELYON_DOMAIN_AUTH_1"
DOMAIN = "healthcare_admin"


def _keypair():
    sk = Ed25519PrivateKey.generate()
    return sk, sk.public_key()


@pytest.fixture
def authority():
    return _keypair()


def _manifest(requires_verdict, authority_key_id=AUTH_KEY_ID):
    spec = {"bind_interaction_type": False, "predicates": [{"path": "record_basis", "rule": "present"}]}
    if requires_verdict:
        spec["requires_verdict"] = True
        spec["authority_key_id"] = authority_key_id
    return {"version": "1.0", "domains": {DOMAIN: spec}}


def _ctx(record=True):
    c = {"domain": DOMAIN, "context": {}}
    if record:
        c["context"]["record_basis"] = "chart-1"
    return c


def _verdict(authority, value, not_after_s=300):
    sk, _ = authority
    v = build_verdict(decision_sha256=DECISION, domain=DOMAIN, verdict=value,
                      verdict_id="vd-1",
                      not_after=datetime.now(timezone.utc) + timedelta(seconds=not_after_s))
    return sign_verdict(v, sk, AUTH_KEY_ID)


def _control(ctx, manifest, authority=None, verdict=None, **ov):
    _, pk = authority if authority else (None, None)
    keys = {AUTH_KEY_ID: pk} if pk is not None else {}
    return control(ctx, manifest, verdict=verdict,
                   expected_decision_sha256=ov.get("decision", DECISION),
                   authority_public_keys=ov.get("keys", keys),
                   gate_key_id=GATE_KEY_ID, now=ov.get("now"))


# --- structural REFUSE (the CAT-scan-not-approved class), no verdict needed ----

def test_structural_invalid_refuses_without_any_verdict(authority):
    # required attestation missing -> REFUSE, purely structural, no out-of-band call.
    out, code, detail = _control(_ctx(record=False), _manifest(requires_verdict=True), authority)
    assert out == CONTROL_REFUSE and code == D_FIELD_ABSENT


# --- domain that needs no verdict: structurally valid -> PASS -----------------

def test_no_verdict_required_passes():
    out, code, _ = _control(_ctx(), _manifest(requires_verdict=False))
    assert out == CONTROL_PASS and code is None


# --- requires_verdict, none supplied -> HOLD_FOR_VERDICT ----------------------

def test_requires_verdict_none_supplied_holds(authority):
    out, code, _ = _control(_ctx(), _manifest(requires_verdict=True), authority, verdict=None)
    assert out == CONTROL_HOLD_FOR_VERDICT and code == D_VERDICT_REQUIRED


# --- requires_verdict, authentic SAFE -> PASS ; authentic UNSAFE -> HIL --------

def test_authentic_safe_verdict_passes(authority):
    out, code, _ = _control(_ctx(), _manifest(True), authority, verdict=_verdict(authority, VERDICT_SAFE))
    assert out == CONTROL_PASS and code is None


def test_authentic_unsafe_verdict_holds_for_hil(authority):
    # e.g. an allergic-reaction contraindication the policy agent detected.
    out, code, detail = _control(_ctx(), _manifest(True), authority, verdict=_verdict(authority, VERDICT_UNSAFE))
    assert out == CONTROL_HOLD_FOR_HIL and code == D_VERDICT_UNSAFE


# --- requires_verdict, bad verdict -> fail-closed HOLD_FOR_VERDICT -------------

def test_forged_verdict_fails_closed_to_hold(authority):
    v = _verdict(authority, VERDICT_SAFE)
    v["verdict"] = VERDICT_UNSAFE   # tamper after signing
    out, code, detail = _control(_ctx(), _manifest(True), authority, verdict=v)
    assert out == CONTROL_HOLD_FOR_VERDICT and code == D_VERDICT_UNVERIFIED
    assert detail["verify_reason"]   # the REF_VERDICT_ reason is carried for audit


def test_wrong_authority_not_the_pinned_one_fails_closed(authority):
    # a DIFFERENT trusted authority signs; the domain pins AUTH_KEY_ID only.
    other_sk, other_pk = _keypair()
    v = build_verdict(decision_sha256=DECISION, domain=DOMAIN, verdict=VERDICT_SAFE,
                      verdict_id="vd-2",
                      not_after=datetime.now(timezone.utc) + timedelta(seconds=300))
    v = sign_verdict(v, other_sk, "OTHER_AUTH")
    _, pinned_pk = authority
    # trust map contains BOTH, but the domain pins only AUTH_KEY_ID:
    out, code, _ = _control(_ctx(), _manifest(True), authority, verdict=v,
                            keys={AUTH_KEY_ID: pinned_pk, "OTHER_AUTH": other_pk})
    assert out == CONTROL_HOLD_FOR_VERDICT and code == D_VERDICT_UNVERIFIED


def test_stale_verdict_fails_closed(authority):
    v = _verdict(authority, VERDICT_SAFE, not_after_s=-1)
    out, code, _ = _control(_ctx(), _manifest(True), authority, verdict=v)
    assert out == CONTROL_HOLD_FOR_VERDICT and code == D_VERDICT_UNVERIFIED


# --- S3 schema: requires_verdict demands a pinned authority_key_id -------------

def test_schema_requires_verdict_without_authority_is_malformed():
    bad = {"version": "1.0", "domains": {DOMAIN: {
        "bind_interaction_type": False, "predicates": [], "requires_verdict": True}}}   # no authority_key_id
    assert safe_domain_manifest(bad) is None


def test_schema_requires_verdict_with_authority_is_valid():
    ok = {"version": "1.0", "domains": {DOMAIN: {
        "bind_interaction_type": False, "predicates": [], "requires_verdict": True, "authority_key_id": AUTH_KEY_ID}}}
    assert safe_domain_manifest(ok) is not None


def test_schema_non_bool_requires_verdict_rejected():
    bad = {"version": "1.0", "domains": {DOMAIN: {"bind_interaction_type": False, "predicates": [], "requires_verdict": "yes"}}}
    assert safe_domain_manifest(bad) is None


# --- determinism firewall: control does no I/O; repeated calls are identical ---

def test_control_is_deterministic(authority):
    args = (_ctx(), _manifest(True), authority)
    v = _verdict(authority, VERDICT_SAFE)
    first = _control(*args, verdict=v)
    for _ in range(20):
        assert _control(*args, verdict=v) == first


# --- module unwired from evaluator/pep ----------------------------------------

def test_control_modules_unwired():
    from IMPLEMENTATION import evaluator, pep
    for mod in (evaluator, pep):
        src = inspect.getsource(mod)
        assert "domain_control" not in src
