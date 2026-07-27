"""STAIRCASE S1 - the signed domain-compliance verdict.

build_verdict/sign_verdict/verify_verdict against REAL Ed25519 keypairs, mirroring
the approval-grant tests. The verdict is bound to decision_sha256 + domain, fresh,
single-use-keyed, and carries a SAFE/UNSAFE attestation the gate verifies
deterministically. verify_verdict emits the REF_VERDICT_* boundary vocabulary
(disjoint from G_* and D_*). Build-then-wire: no caller on the default path.
"""
import inspect
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from IMPLEMENTATION.domain_verdict import (
    build_verdict, sign_verdict, verify_verdict,
    VERDICT_SAFE, VERDICT_UNSAFE, ACCEPT_VERDICT_VALID,
    REF_VERDICT_MALFORMED, REF_VERDICT_MISSING_ID, REF_VERDICT_SIGNATURE_INVALID,
    REF_VERDICT_KEY_UNKNOWN, REF_VERDICT_SOD, REF_VERDICT_BINDING_MISMATCH,
    REF_VERDICT_DOMAIN_MISMATCH, REF_VERDICT_VALUE_INVALID, REF_VERDICT_EXPIRED,
)

DECISION = "d" * 64
DOMAIN = "healthcare_admin"
GATE_KEY_ID = "ELYON_GATE_1"
AUTH_KEY_ID = "ELYON_DOMAIN_AUTH_1"


def _keypair():
    sk = Ed25519PrivateKey.generate()
    return sk, sk.public_key()


@pytest.fixture
def authority():
    return _keypair()


@pytest.fixture
def trust(authority):
    _, pk = authority
    return {AUTH_KEY_ID: pk}


def _future(seconds=300):
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)


def _signed(authority, value=VERDICT_SAFE, not_after=None, key_id=AUTH_KEY_ID, **ov):
    sk, _ = authority
    v = build_verdict(
        decision_sha256=ov.get("decision_sha256", DECISION),
        domain=ov.get("domain", DOMAIN),
        verdict=value,
        verdict_id=ov.get("verdict_id", "vd-abc"),
        not_after=not_after or _future(),
    )
    return sign_verdict(v, sk, key_id)


def _verify(v, trust, **ov):
    return verify_verdict(
        v,
        expected_decision_sha256=ov.get("expected_decision_sha256", DECISION),
        expected_domain=ov.get("expected_domain", DOMAIN),
        authority_public_keys=trust,
        gate_key_id=ov.get("gate_key_id", GATE_KEY_ID),
        now=ov.get("now"),
    )


# --- happy paths: SAFE and UNSAFE both authenticate and surface the value ------

def test_valid_safe_verdict_accepted(authority, trust):
    r = _verify(_signed(authority, VERDICT_SAFE), trust)
    assert r == {"accepted": True, "reason": ACCEPT_VERDICT_VALID, "verdict": VERDICT_SAFE}


def test_valid_unsafe_verdict_accepted_and_surfaced(authority, trust):
    r = _verify(_signed(authority, VERDICT_UNSAFE), trust)
    assert r["accepted"] is True and r["verdict"] == VERDICT_UNSAFE


# --- SoD: a gate-minted verdict is not an independent attestation --------------

def test_sod_authority_equals_gate_key_refused(authority):
    # sign with a key whose id IS the gate id -> SoD refuse, even if well-signed.
    _, pk = authority
    v = _signed(authority, key_id=GATE_KEY_ID)
    r = _verify(v, {GATE_KEY_ID: pk})
    assert r["accepted"] is False and r["reason"] == REF_VERDICT_SOD


# --- provenance / signature ---------------------------------------------------

def test_unknown_authority_key_refused(authority):
    r = _verify(_signed(authority), {})   # empty trust map
    assert r["reason"] == REF_VERDICT_KEY_UNKNOWN


def test_forged_signature_refused(authority, trust):
    v = _signed(authority)
    v["verdict"] = VERDICT_UNSAFE if v["verdict"] == VERDICT_SAFE else VERDICT_SAFE  # tamper post-sign
    assert _verify(v, trust)["reason"] == REF_VERDICT_SIGNATURE_INVALID


@pytest.mark.parametrize("bad", ["not-a-dict", 42, None, {}, {"verdict_version": "1.0"}])
def test_malformed_refused(bad, trust):
    assert _verify(bad, trust)["reason"] == REF_VERDICT_MALFORMED


def test_missing_verdict_id_refused(authority, trust):
    v = _signed(authority, verdict_id="x")
    v["verdict_id"] = ""      # present but empty
    assert _verify(v, trust)["reason"] == REF_VERDICT_MISSING_ID


# --- binding: action, domain, value, freshness --------------------------------

def test_binding_mismatch_wrong_decision_refused(authority, trust):
    v = _signed(authority)
    assert _verify(v, trust, expected_decision_sha256="e" * 64)["reason"] == REF_VERDICT_BINDING_MISMATCH


def test_domain_mismatch_refused(authority, trust):
    v = _signed(authority, domain="finance_transfer")   # verdict says finance...
    assert _verify(v, trust, expected_domain=DOMAIN)["reason"] == REF_VERDICT_DOMAIN_MISMATCH  # ...gate expects healthcare


def test_value_invalid_refused(authority, trust):
    # hand-build a well-signed verdict carrying an out-of-set value.
    sk, _ = authority
    raw = {
        "verdict_version": "1.0", "decision_sha256": DECISION, "domain": DOMAIN,
        "verdict": "MAYBE", "verdict_id": "vd-x", "not_after": _future().isoformat(),
    }
    assert _verify(sign_verdict(raw, sk, AUTH_KEY_ID), trust)["reason"] == REF_VERDICT_VALUE_INVALID


def test_expired_verdict_refused(authority, trust):
    v = _signed(authority, not_after=datetime.now(timezone.utc) - timedelta(seconds=1))
    assert _verify(v, trust)["reason"] == REF_VERDICT_EXPIRED


def test_clock_skew_tolerates_small_lateness(authority, trust):
    v = _signed(authority, not_after=datetime.now(timezone.utc) - timedelta(seconds=2))
    r = verify_verdict(v, expected_decision_sha256=DECISION, expected_domain=DOMAIN,
                       authority_public_keys=trust, gate_key_id=GATE_KEY_ID,
                       clock_skew=timedelta(seconds=10))
    assert r["accepted"] is True


# --- build_verdict guards -----------------------------------------------------

def test_build_verdict_rejects_bad_inputs():
    with pytest.raises(ValueError):
        build_verdict(decision_sha256=DECISION, domain=DOMAIN, verdict="MAYBE",
                      verdict_id="x", not_after=_future())
    with pytest.raises(ValueError):
        build_verdict(decision_sha256=DECISION, domain=DOMAIN, verdict=VERDICT_SAFE,
                      verdict_id="", not_after=_future())
    with pytest.raises(ValueError):  # naive datetime
        build_verdict(decision_sha256=DECISION, domain=DOMAIN, verdict=VERDICT_SAFE,
                      verdict_id="x", not_after=datetime.now())


# --- REF_VERDICT_ disjoint from G_ / D_ ; module unwired ----------------------

def test_ref_verdict_namespace_and_unwired():
    import IMPLEMENTATION.domain_verdict as dv
    codes = {v for k, v in vars(dv).items() if k.startswith("REF_VERDICT_") and isinstance(v, str)}
    assert codes and all(c.startswith("REF_VERDICT_") for c in codes)
    from IMPLEMENTATION import evaluator
    assert "domain_verdict" not in inspect.getsource(evaluator)
