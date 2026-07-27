"""Wiring B - the domain gate enforcing at the PEP layer, end to end.

D is OPT-IN: ELYON_DOMAIN_MANIFEST unset -> the whole block is skipped and the
gate behaves exactly as it did before D existed. When enabled, a domain-invalid
interaction is REFUSED and a domain requiring an out-of-band verdict is HELD -
with the upstream never reached in either case.

Enabling is import-time (module-level env read), so these tests reload pep under
a patched environment, mirroring the existing governance-wiring test idiom.
"""
import importlib
import json
import os
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.domain_verdict import build_verdict, sign_verdict, VERDICT_SAFE, VERDICT_UNSAFE

SHA = manifest_sha256()
TARGET = "https://example.invalid/x"


def _armed_manifest(tmp_path, *, requires_verdict=False, authority_key_id=None):
    spec = {
        "predicates": [{"path": "patient_consent", "rule": "equals", "value": True}],
        "interaction_types": ["chart_write"],
    }
    if requires_verdict:
        spec["requires_verdict"] = True
        spec["authority_key_id"] = authority_key_id
    dm = {"version": "1.0", "domains": {"healthcare_admin": spec}}
    p = tmp_path / "dm.json"
    p.write_text(json.dumps(dm), encoding="utf-8")
    return str(p)


def _body(*, domain=None, itype=None, consent=True):
    interaction = {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {"patient_consent": consent},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": SHA,
    }
    if domain is not None:
        interaction["domain"] = domain
    if itype is not None:
        interaction["interaction_type"] = itype
    return {"target_url": TARGET, "interaction": interaction}


GATE_KEY_ID = "ELYON_GATE_TEST"

_ENV_KEYS = ("ELYON_DOMAIN_MANIFEST", "ELYON_SIGNING_KEY_HEX", "ELYON_SIGNING_KEY_ID")


@pytest.fixture(autouse=True)
def _restore_pep_module():
    """These tests reload pep to pick up its import-time env reads. Without an
    explicit restore the mutated module leaks into every later test in the
    session (pep would stay domain-enabled and key-bound). Reload once more with
    the env cleared so pep ends disabled and identical to a fresh import.
    Env is popped directly rather than via monkeypatch so this does not depend
    on fixture teardown ordering."""
    yield
    for k in _ENV_KEYS:
        os.environ.pop(k, None)
    import IMPLEMENTATION.pep as pep
    importlib.reload(pep)


def _client(monkeypatch, dm_path=None, *, gate_key=True):
    """Reload pep with the domain manifest env set (or cleared).

    gate_key=True configures a gate signing identity so the verdict path is
    exercised for real; without one the gate has no identity to run the SoD
    id-check against and every verdict-requiring domain correctly holds
    (asserted separately below)."""
    if dm_path is None:
        monkeypatch.delenv("ELYON_DOMAIN_MANIFEST", raising=False)
    else:
        monkeypatch.setenv("ELYON_DOMAIN_MANIFEST", dm_path)
    if gate_key:
        monkeypatch.setenv("ELYON_SIGNING_KEY_HEX", "11" * 32)
        monkeypatch.setenv("ELYON_SIGNING_KEY_ID", GATE_KEY_ID)
    else:
        monkeypatch.delenv("ELYON_SIGNING_KEY_HEX", raising=False)
        monkeypatch.delenv("ELYON_SIGNING_KEY_ID", raising=False)
    import IMPLEMENTATION.pep as pep
    pep = importlib.reload(pep)
    return TestClient(pep.app, raise_server_exceptions=False), pep


# --- default-off: the path is unchanged when D is not configured -------------

def test_disabled_when_env_unset(monkeypatch):
    _, pep = _client(monkeypatch, None)
    assert pep._DOMAIN_ENABLED is False


def test_disabled_gate_ignores_domain_fields(monkeypatch):
    """With D off, a would-be domain-invalid body is not refused BY THE DOMAIN
    GATE - it proceeds past it (and fails later for unrelated transport reasons,
    never with a D_ code)."""
    client, _ = _client(monkeypatch, None)
    r = client.post("/governed-call", json=_body(domain="healthcare_admin", consent=False))
    code = (r.json().get("detail") or {}).get("refusal_reason_code", "")
    assert not str(code).startswith("D_")


# --- enabled: structural domain refusal --------------------------------------

def test_enabled_refuses_domain_invalid_content(monkeypatch, tmp_path):
    client, pep = _client(monkeypatch, _armed_manifest(tmp_path))
    assert pep._DOMAIN_ENABLED is True
    r = client.post("/governed-call",
                    json=_body(domain="healthcare_admin", itype="chart_write", consent=False))
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "D_FIELD_INVALID"


def test_enabled_refuses_undeclared_domain(monkeypatch, tmp_path):
    client, _ = _client(monkeypatch, _armed_manifest(tmp_path))
    r = client.post("/governed-call", json=_body(consent=True))   # no domain declared
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "D_DOMAIN_UNDECLARED"


def test_enabled_refuses_domain_shopping(monkeypatch, tmp_path):
    client, _ = _client(monkeypatch, _armed_manifest(tmp_path))
    r = client.post("/governed-call",
                    json=_body(domain="healthcare_admin", itype="wrong_type", consent=True))
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "D_DOMAIN_MISBOUND"


def test_enabled_refuses_unknown_domain(monkeypatch, tmp_path):
    client, _ = _client(monkeypatch, _armed_manifest(tmp_path))
    r = client.post("/governed-call",
                    json=_body(domain="no_such", itype="chart_write", consent=True))
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "D_DOMAIN_UNKNOWN"


# --- enabled: a malformed deployed ruleset fails CLOSED (S5b) ----------------

def test_malformed_deployed_manifest_fails_closed(monkeypatch, tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('{"version": "1.0", "domains": "broken"}', encoding="utf-8")
    client, _ = _client(monkeypatch, str(p))
    r = client.post("/governed-call", json=_body(domain="healthcare_admin", consent=True))
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "D_MANIFEST_MALFORMED"


def test_absent_deployed_manifest_is_inert_not_refuse_all(monkeypatch, tmp_path):
    """The anti-brick property at the HTTP layer: pointing at a missing file must
    not turn the gate into refuse-all."""
    client, _ = _client(monkeypatch, str(tmp_path / "nope.json"))
    r = client.post("/governed-call", json=_body(domain="anything", consent=False))
    code = (r.json().get("detail") or {}).get("refusal_reason_code", "")
    assert not str(code).startswith("D_")


# --- enabled: requires_verdict -> 202 hold, upstream never reached ------------

def test_requires_verdict_holds_202_without_verdict(monkeypatch, tmp_path):
    path = _armed_manifest(tmp_path, requires_verdict=True, authority_key_id="AUTH1")
    client, _ = _client(monkeypatch, path)
    r = client.post("/governed-call",
                    json=_body(domain="healthcare_admin", itype="chart_write", consent=True))
    assert r.status_code == 202
    body = r.json()
    assert body["terminal_state"] == "PENDING_DOMAIN_VERDICT"
    assert body["refusal_reason_code"] == "D_VERDICT_REQUIRED"
    assert body["decision_sha256"]


def test_unverifiable_verdict_holds_not_passes(monkeypatch, tmp_path):
    """No signed key record is configured, so the authority trust map is empty:
    even a well-formed verdict cannot verify -> HOLD, never PASS."""
    path = _armed_manifest(tmp_path, requires_verdict=True, authority_key_id="AUTH1")
    client, _ = _client(monkeypatch, path)
    sk = Ed25519PrivateKey.generate()
    v = sign_verdict(build_verdict(decision_sha256="d" * 64, domain="healthcare_admin",
                                   verdict=VERDICT_SAFE, verdict_id="v1",
                                   not_after=datetime.now(timezone.utc) + timedelta(seconds=300)),
                     sk, "AUTH1")
    r = client.post("/governed-call",
                    json=_body(domain="healthcare_admin", itype="chart_write", consent=True),
                    headers={"X-Elyon-Sol-Domain-Verdict": json.dumps(v)})
    assert r.status_code == 202
    assert r.json()["refusal_reason_code"] == "D_VERDICT_UNVERIFIED"


def test_junk_verdict_header_holds_closed(monkeypatch, tmp_path):
    path = _armed_manifest(tmp_path, requires_verdict=True, authority_key_id="AUTH1")
    client, _ = _client(monkeypatch, path)
    r = client.post("/governed-call",
                    json=_body(domain="healthcare_admin", itype="chart_write", consent=True),
                    headers={"X-Elyon-Sol-Domain-Verdict": "not-json"})
    assert r.status_code == 202
    assert r.json()["refusal_reason_code"] == "D_VERDICT_UNVERIFIED"


# --- structural refusal takes precedence over the verdict requirement --------

def test_no_gate_identity_holds_closed(monkeypatch, tmp_path):
    """A gate with no signing identity cannot run the SoD id-check, so a
    verdict-requiring domain must HOLD rather than release (DV-03 at the wiring
    layer: a load-bearing input missing -> oversight, never bypass)."""
    path = _armed_manifest(tmp_path, requires_verdict=True, authority_key_id="AUTH1")
    client, _ = _client(monkeypatch, path, gate_key=False)
    r = client.post("/governed-call",
                    json=_body(domain="healthcare_admin", itype="chart_write", consent=True))
    assert r.status_code == 202
    assert r.json()["refusal_reason_code"] == "D_VERDICT_CONTRACT"


def test_structural_refuse_precedes_verdict_hold(monkeypatch, tmp_path):
    """Invalid content must REFUSE outright, not consume a verdict/approval slot."""
    path = _armed_manifest(tmp_path, requires_verdict=True, authority_key_id="AUTH1")
    client, _ = _client(monkeypatch, path)
    r = client.post("/governed-call",
                    json=_body(domain="healthcare_admin", itype="chart_write", consent=False))
    assert r.status_code == 403
    assert r.json()["detail"]["refusal_reason_code"] == "D_FIELD_INVALID"
