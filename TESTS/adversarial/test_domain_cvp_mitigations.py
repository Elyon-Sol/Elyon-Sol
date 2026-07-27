"""CVP mitigations for the D layer - findings DV-01..DV-08.

Each test is a REVERT-CATCHER: it asserts the mitigated behavior and fails if the
pre-fix (fail-open) behavior returns. Diagnosis referents are the empirical runs
recorded with the CVP finding list; the pre-fix outcome is named in each docstring.
"""
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from IMPLEMENTATION.domain_validity import (
    assess, safe_domain_manifest,
    D_DOMAIN_UNDECLARED, D_DOMAIN_MISBOUND, D_FIELD_INVALID,
)
from IMPLEMENTATION.domain_verdict import (
    build_verdict, sign_verdict, verify_verdict, claim_verdict_once,
    VERDICT_SAFE, ACCEPT_VERDICT_VALID,
    REF_VERDICT_CONTRACT_VIOLATION, REF_VERDICT_VERSION_UNSUPPORTED,
    REF_VERDICT_FINDINGS_TOO_LARGE, REF_VERDICT_REPLAY, REF_VERDICT_SOD,
)
from IMPLEMENTATION.domain_control import (
    control, CONTROL_PASS, CONTROL_HOLD_FOR_VERDICT, CONTROL_REFUSE,
    D_VERDICT_CONTRACT,
)
from IMPLEMENTATION.replay_cache import InMemoryReplayCache

DEC = "d" * 64
GATE = "ELYON_GATE_1"
AUTH = "ELYON_DOMAIN_AUTH_1"
FUT = lambda s=300: datetime.now(timezone.utc) + timedelta(seconds=s)


def _sk():
    return Ed25519PrivateKey.generate()


def _armed(**spec_extra):
    spec = {"predicates": [{"path": "patient_consent", "rule": "equals", "value": True}],
            "requires_verdict": True, "authority_key_id": AUTH}
    spec.update(spec_extra)
    return {"version": "1.0", "domains": {"healthcare_admin": spec}}


# --- DV-01: undeclared domain must NOT bypass an armed manifest ---------------

def test_DV01_undeclared_domain_fails_closed():
    """PRE-FIX: control(no-domain, armed) -> PASS (whole layer bypassed by omission)."""
    ctx = {"context": {"patient_consent": False}}
    out, code, _ = control(ctx, _armed(), verdict=None, expected_decision_sha256=DEC,
                           authority_public_keys={}, gate_key_id=GATE)
    assert out == CONTROL_REFUSE and code == D_DOMAIN_UNDECLARED


def test_DV01_explicit_opt_out_still_permitted():
    m = _armed(); m["require_domain"] = False          # eyes-open deployment choice
    assert assess({"context": {}}, m) == ("VALID", None, None)


# --- DV-02: domain-shopping blocked when the domain pins interaction types ----

def test_DV02_domain_shopping_blocked_by_type_binding():
    """PRE-FIX: declaring a weaker armed domain carried strict content past it."""
    m = {"version": "1.0", "domains": {
        "healthcare_admin": {"predicates": [], "interaction_types": ["chart_write"]},
        "misc": {"predicates": [], "interaction_types": ["misc_read"]}}}
    ctx = {"domain": "misc", "interaction_type": "chart_write", "context": {}}
    state, code, _ = assess(ctx, m)
    assert (state, code) == ("INVALID", D_DOMAIN_MISBOUND)


def test_DV02_correct_binding_passes():
    m = {"version": "1.0", "domains": {
        "healthcare_admin": {"predicates": [], "interaction_types": ["chart_write"]}}}
    ctx = {"domain": "healthcare_admin", "interaction_type": "chart_write", "context": {}}
    assert assess(ctx, m) == ("VALID", None, None)


def test_DV02_unbound_domain_backward_compatible():
    m = {"version": "1.0", "domains": {"d": {"predicates": []}}}   # no interaction_types pin
    assert assess({"domain": "d", "context": {}}, m) == ("VALID", None, None)


def test_DV02_malformed_type_binding_rejected():
    bad = {"version": "1.0", "domains": {"d": {"predicates": [], "interaction_types": [1, 2]}}}
    assert safe_domain_manifest(bad) is None


# --- DV-03: gate_key_id omitted must NOT disable SoD -------------------------

def test_DV03_none_gate_key_id_fails_closed():
    """PRE-FIX: gate_key_id=None accepted a GATE-SIGNED verdict (VERDICT_VALID)."""
    sk = _sk()
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v1", not_after=FUT()), sk, GATE)
    r = verify_verdict(v, expected_decision_sha256=DEC, expected_domain="d",
                       authority_public_keys={GATE: sk.public_key()}, gate_key_id=None)
    assert r["accepted"] is False and r["reason"] == REF_VERDICT_CONTRACT_VIOLATION


def test_DV03_gate_signed_verdict_still_sod_refused_when_contract_met():
    sk = _sk()
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v1", not_after=FUT()), sk, GATE)
    r = verify_verdict(v, expected_decision_sha256=DEC, expected_domain="d",
                       authority_public_keys={GATE: sk.public_key()}, gate_key_id=GATE)
    assert r["reason"] == REF_VERDICT_SOD


def test_DV03_control_without_gate_key_id_holds_not_passes():
    """PRE-FIX: control() with gate_key_id omitted -> PASS on a gate-signed verdict."""
    sk = _sk()
    m = {"version": "1.0", "domains": {"d": {"predicates": [], "requires_verdict": True,
                                             "authority_key_id": GATE}}}
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v1", not_after=FUT()), sk, GATE)
    out, code, _ = control({"domain": "d", "context": {}}, m, verdict=v,
                           expected_decision_sha256=DEC,
                           authority_public_keys={GATE: sk.public_key()})
    assert out == CONTROL_HOLD_FOR_VERDICT and code == D_VERDICT_CONTRACT


# --- DV-04: expected_decision_sha256 omitted must NOT satisfy binding ---------

def test_DV04_none_expected_decision_fails_closed():
    """PRE-FIX: decision_sha256=None vs expected=None -> VERDICT_VALID (None==None)."""
    sk = _sk()
    v = sign_verdict(build_verdict(decision_sha256=None, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v2", not_after=FUT()), sk, AUTH)
    r = verify_verdict(v, expected_decision_sha256=None, expected_domain="d",
                       authority_public_keys={AUTH: sk.public_key()}, gate_key_id=GATE)
    assert r["reason"] == REF_VERDICT_CONTRACT_VIOLATION


def test_DV04_control_without_expected_decision_holds():
    """PRE-FIX: control() with no expected_decision_sha256 -> PASS."""
    sk = _sk()
    m = {"version": "1.0", "domains": {"d": {"predicates": [], "requires_verdict": True,
                                             "authority_key_id": AUTH}}}
    v = sign_verdict(build_verdict(decision_sha256=None, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v2", not_after=FUT()), sk, AUTH)
    out, code, _ = control({"domain": "d", "context": {}}, m, verdict=v,
                           authority_public_keys={AUTH: sk.public_key()}, gate_key_id=GATE)
    assert out == CONTROL_HOLD_FOR_VERDICT and code == D_VERDICT_CONTRACT


@pytest.mark.parametrize("kw", [
    {"expected_domain": ""},
    {"authority_public_keys": "not-a-dict"},
])
def test_DV04_other_contract_omissions_fail_closed(kw):
    sk = _sk()
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v3", not_after=FUT()), sk, AUTH)
    base = dict(expected_decision_sha256=DEC, expected_domain="d",
                authority_public_keys={AUTH: sk.public_key()}, gate_key_id=GATE)
    base.update(kw)
    assert verify_verdict(v, **base)["reason"] == REF_VERDICT_CONTRACT_VIOLATION


# --- DV-05: single-use now enforceable via the ReplayCache seam ---------------

def test_DV05_verdict_single_use_claimed_once():
    """PRE-FIX: the same verdict verified unlimited times; no claim existed."""
    sk = _sk()
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v-once", not_after=FUT()), sk, AUTH)
    cache = InMemoryReplayCache()
    first = claim_verdict_once(v, cache)
    second = claim_verdict_once(v, cache)
    assert first["accepted"] is True and first["reason"] == ACCEPT_VERDICT_VALID
    assert second["accepted"] is False and second["reason"] == REF_VERDICT_REPLAY


def test_DV05_no_cache_fails_closed():
    sk = _sk()
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v-nc", not_after=FUT()), sk, AUTH)
    assert claim_verdict_once(v, None)["reason"] == REF_VERDICT_CONTRACT_VIOLATION


def test_DV05_cache_error_fails_closed():
    class Boom:
        def check_and_claim(self, *a, **k):
            raise RuntimeError("store down")
    sk = _sk()
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v-boom", not_after=FUT()), sk, AUTH)
    assert claim_verdict_once(v, Boom())["reason"] == REF_VERDICT_REPLAY


# --- DV-06: bool/int type confusion in equals/in/not_in ----------------------

def test_DV06_int_one_does_not_satisfy_equals_true():
    """PRE-FIX: consent=1 satisfied equals:true (Python True == 1)."""
    m = {"version": "1.0", "domains": {"d": {"predicates": [
        {"path": "consent", "rule": "equals", "value": True}]}}}
    assert assess({"domain": "d", "context": {"consent": 1}}, m)[:2] == ("INVALID", D_FIELD_INVALID)
    assert assess({"domain": "d", "context": {"consent": True}}, m) == ("VALID", None, None)


def test_DV06_false_does_not_match_numeric_membership():
    """PRE-FIX: level=False satisfied in:[0,1,2]."""
    m = {"version": "1.0", "domains": {"d": {"predicates": [
        {"path": "level", "rule": "in", "value": [0, 1, 2]}]}}}
    assert assess({"domain": "d", "context": {"level": False}}, m)[:2] == ("INVALID", D_FIELD_INVALID)
    assert assess({"domain": "d", "context": {"level": 1}}, m) == ("VALID", None, None)


def test_DV06_not_in_is_type_strict_too():
    m = {"version": "1.0", "domains": {"d": {"predicates": [
        {"path": "flag", "rule": "not_in", "value": [1]}]}}}
    # True must NOT be treated as the excluded 1 -> not_in holds -> VALID
    assert assess({"domain": "d", "context": {"flag": True}}, m) == ("VALID", None, None)


# --- DV-07 / DV-08: version gate + findings bound ----------------------------

def test_DV07_unsupported_verdict_version_refused():
    """PRE-FIX: verdict_version 999.0 accepted as VERDICT_VALID."""
    sk = _sk()
    raw = {"verdict_version": "999.0", "decision_sha256": DEC, "domain": "d",
           "verdict": VERDICT_SAFE, "verdict_id": "v9", "not_after": FUT().isoformat()}
    v = sign_verdict(raw, sk, AUTH)
    r = verify_verdict(v, expected_decision_sha256=DEC, expected_domain="d",
                       authority_public_keys={AUTH: sk.public_key()}, gate_key_id=GATE)
    assert r["reason"] == REF_VERDICT_VERSION_UNSUPPORTED


def test_DV08_oversized_findings_refused():
    """PRE-FIX: a 100KB findings blob verified fine."""
    sk = _sk()
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v8", not_after=FUT(),
                                   findings={"x": "A" * 100000}), sk, AUTH)
    r = verify_verdict(v, expected_decision_sha256=DEC, expected_domain="d",
                       authority_public_keys={AUTH: sk.public_key()}, gate_key_id=GATE)
    assert r["reason"] == REF_VERDICT_FINDINGS_TOO_LARGE


def test_DV08_small_findings_still_accepted():
    sk = _sk()
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE,
                                   verdict_id="v8b", not_after=FUT(),
                                   findings={"rule": "contraindication"}), sk, AUTH)
    r = verify_verdict(v, expected_decision_sha256=DEC, expected_domain="d",
                       authority_public_keys={AUTH: sk.public_key()}, gate_key_id=GATE)
    assert r["accepted"] is True


# --- end-to-end: the mitigated happy path still works ------------------------

def test_mitigated_happy_path_still_passes():
    sk = _sk()
    m = {"version": "1.0", "domains": {"healthcare_admin": {
        "predicates": [{"path": "patient_consent", "rule": "equals", "value": True}],
        "requires_verdict": True, "authority_key_id": AUTH,
        "interaction_types": ["chart_write"]}}}
    ctx = {"domain": "healthcare_admin", "interaction_type": "chart_write",
           "context": {"patient_consent": True}}
    v = sign_verdict(build_verdict(decision_sha256=DEC, domain="healthcare_admin",
                                   verdict=VERDICT_SAFE, verdict_id="v-ok",
                                   not_after=FUT()), sk, AUTH)
    out, code, _ = control(ctx, m, verdict=v, expected_decision_sha256=DEC,
                           authority_public_keys={AUTH: sk.public_key()}, gate_key_id=GATE)
    assert out == CONTROL_PASS and code is None
    assert claim_verdict_once(v, InMemoryReplayCache())["accepted"] is True
