"""
ext-authz admissibility sidecar tests
(docs/design/opa_sidecar_design.md sections 4/5/8/11 step 2).

Exercise IMPLEMENTATION/authz_sidecar.py - the HTTP ext_authz adapter that wraps
the PRODUCTION ExecutorGate and surfaces ALLOW(200)/DENY(403 + REF_*) over the
X-Elyon-Sol-Envelope + X-Elyon-Sol-Interaction header contract. These prove the
sidecar reproduces the executor refusal matrix faithfully (it composes the
verifier, adding no decision of its own), fails closed on bad/absent config, and
honors the VL-076 replay seam ACROSS sidecar instances.

Envelopes are produced by the REAL gate (pep), signed by the autouse `gate_signing`
conftest key; interactions are the canonical `interaction_for` from the MCP server,
delivered to the sidecar in the structured header the default extractor reads.
"""

import json
import time
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.published_source import anchor_sha256
from IMPLEMENTATION.replay_cache import InMemoryReplayCache
from IMPLEMENTATION.authz_sidecar import (
    build_authz_sidecar_app,
    ENVELOPE_HEADER,
    INTERACTION_HEADER,
    DECISION_HEADER,
    REASON_HEADER,
    DECISION_ALLOW,
    DECISION_DENY,
)
from IMPLEMENTATION.reference_target import (
    REF_TARGET_ANCHOR_MISMATCH,
    REF_TARGET_NOT_CONFIGURED,
)
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ENVELOPE_ABSENT,
    REF_VERIFY_BINDING_MISMATCH,
    REF_VERIFY_SIGNATURE_INVALID,
    REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED,
    REF_VERIFY_SIGNATURE_EXPIRED,
    REF_VERIFY_REPLAY,
)

TARGET_ID = "mcp://elyon-sol/tool-server"
RECORD_PATH = "EVIDENCE/published_hashes.json"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _record_bytes() -> bytes:
    with open(RECORD_PATH, "rb") as f:
        return f.read()


def _admit(tool, args):
    """Drive the REAL gate to mint a signed envelope for (tool, args), exactly the
    executor-SDK test pattern (the gate's upstream push is faked so no socket is
    needed)."""
    class _R:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        return _R()

    orig = pep.requests.post
    pep.requests.post = fake_post
    try:
        r = TestClient(pep.app).post(
            "/governed-call",
            json={"target_url": TARGET_ID, "interaction": interaction_for(tool, args)},
        )
        assert r.status_code == 200, r.text
        return r.json()["envelope"]
    finally:
        pep.requests.post = orig


def _config(gate_signing, *, target_url=TARGET_ID, record_bytes=None,
            pinned_root=None, clock_skew=timedelta(0)):
    if record_bytes is None:
        record_bytes = _record_bytes()
    if pinned_root is None:
        pinned_root = anchor_sha256(record_bytes)
    return {
        "target_url": target_url,
        "record_bytes": record_bytes,
        "pinned_root_sha256": pinned_root,
        "pinned_public_keys": {gate_signing["key_id"]: gate_signing["public_key"]},
        "clock_skew": clock_skew,
    }


def _app(config, replay_cache=None):
    return build_authz_sidecar_app(
        config_provider=lambda: config, replay_cache=replay_cache
    )


def _post(client, envelope=None, interaction=None, *, omit_envelope=False,
          raw_envelope=None, raw_interaction=None):
    headers = {}
    if raw_envelope is not None:
        headers[ENVELOPE_HEADER] = raw_envelope
    elif not omit_envelope and envelope is not None:
        headers[ENVELOPE_HEADER] = canonical_json(envelope)
    if raw_interaction is not None:
        headers[INTERACTION_HEADER] = raw_interaction
    elif interaction is not None:
        headers[INTERACTION_HEADER] = canonical_json(interaction)
    return client.post("/authz", headers=headers)


def _check(client, tool, args, envelope, **kw):
    return _post(client, envelope=envelope, interaction=interaction_for(tool, args), **kw)


# --------------------------------------------------------------------------- #
# ALLOW
# --------------------------------------------------------------------------- #

def test_allow_on_valid_attested_request(gate_signing):
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW
    assert r.headers[REASON_HEADER] == "REASSERTED_AND_BOUND"


# --------------------------------------------------------------------------- #
# DENY - one per REF_* class
# --------------------------------------------------------------------------- #

def test_deny_absent_unattested(gate_signing):
    """A1: a direct caller presents no envelope header -> ABSENT."""
    client = TestClient(_app(_config(gate_signing)))
    r = _post(client, omit_envelope=True,
              interaction=interaction_for("transfer_funds", {"amount": 100, "to": "acct-42"}))
    assert r.status_code == 403
    assert r.headers[DECISION_HEADER] == DECISION_DENY
    assert r.headers[REASON_HEADER] == REF_VERIFY_ENVELOPE_ABSENT


def test_deny_unparseable_envelope_header_is_absent(gate_signing):
    """An unparseable attestation header is treated as no envelope (A1)."""
    client = TestClient(_app(_config(gate_signing)))
    r = _post(client, raw_envelope="{not json",
              interaction=interaction_for("transfer_funds", {"amount": 1, "to": "x"}))
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_ENVELOPE_ABSENT


def test_deny_forged_signature(gate_signing):
    """Tampering any field in the signed region breaks the issuer signature ->
    SIGNATURE_INVALID, refused on provenance before currency/binding."""
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    env["request_context"]["AP"] = env["request_context"]["AP"] + ["smuggled-authority"]
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_SIGNATURE_INVALID


def test_deny_replay(gate_signing):
    """The same decision_id honored once is refused on re-presentation (the shared
    cache lives on the app, so it persists across requests)."""
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    first = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert first.status_code == 200
    second = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert second.status_code == 403
    assert second.headers[REASON_HEADER] == REF_VERIFY_REPLAY


def test_deny_rebind_interaction(gate_signing):
    """An envelope minted for one tool presented against another -> BINDING_MISMATCH."""
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "delete_database", {"db": "prod"}, env)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_BINDING_MISMATCH


def test_deny_target_swap(gate_signing):
    """A sidecar configured for a DIFFERENT target_url than the envelope binds to
    refuses the binding (the target-identity half of the binding check)."""
    config = _config(gate_signing, target_url="https://other-target.example/act")
    client = TestClient(_app(config))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_BINDING_MISMATCH


def test_deny_stale(gate_signing):
    """A decision past its not_after -> SIGNATURE_EXPIRED (freshness)."""
    client = TestClient(_app(_config(gate_signing)))
    pep.DECISION_MAX_AGE_SECONDS = 1
    try:
        env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    finally:
        pep.DECISION_MAX_AGE_SECONDS = 300
    time.sleep(2)
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_SIGNATURE_EXPIRED


def test_deny_record_drift(gate_signing):
    """A published record whose pinned state hash drifted from live state ->
    RE_EVALUATE_REQUIRED. The pin matches the drifted bytes (so the anchor passes
    and the drift is caught at reassert, not at the anchor)."""
    authentic = _record_bytes()
    drifted = json.dumps(
        {**json.loads(authentic), "evaluator_sha256": "0" * 64}, sort_keys=True
    ).encode("utf-8")
    config = _config(gate_signing, record_bytes=drifted, pinned_root=anchor_sha256(drifted))
    client = TestClient(_app(config))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED


# --------------------------------------------------------------------------- #
# Fail-closed on configuration
# --------------------------------------------------------------------------- #

def test_fail_closed_unconfigured(gate_signing):
    """config_provider -> None (missing trust base) -> REF_TARGET_NOT_CONFIGURED,
    per request, never an ALLOW."""
    client = TestClient(_app(None))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_TARGET_NOT_CONFIGURED


def test_fail_closed_wrong_anchor(gate_signing):
    """A record whose bytes do not hash to the pinned anchor -> ANCHOR_MISMATCH
    before any currency claim is trusted."""
    config = _config(gate_signing, pinned_root="0" * 64)
    client = TestClient(_app(config))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _check(client, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_TARGET_ANCHOR_MISMATCH


def test_config_from_env_missing_returns_none(monkeypatch):
    """config_from_env with no ELYON_* set -> None (the fail-closed signal)."""
    import IMPLEMENTATION.authz_sidecar as sidecar
    for var in (
        sidecar.ENV_TARGET_URL, sidecar.ENV_RECORD_PATH, sidecar.ENV_PINNED_ROOT,
        sidecar.ENV_GATE_KEY_ID, sidecar.ENV_GATE_PUBLIC_KEY_HEX,
    ):
        monkeypatch.delenv(var, raising=False)
    assert sidecar.config_from_env() is None


# --------------------------------------------------------------------------- #
# Replay seam across instances (the VL-076 cross-instance property)
# --------------------------------------------------------------------------- #

def test_replay_shared_across_two_sidecar_instances(gate_signing):
    """Two sidecar apps sharing one ReplayCache: honored on instance A, refused as
    a replay on instance B - exactly-once across instances (design section 7)."""
    shared = InMemoryReplayCache()
    config = _config(gate_signing)
    client_a = TestClient(_app(config, replay_cache=shared))
    client_b = TestClient(_app(config, replay_cache=shared))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    a = _check(client_a, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert a.status_code == 200
    b = _check(client_b, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert b.status_code == 403
    assert b.headers[REASON_HEADER] == REF_VERIFY_REPLAY


# --------------------------------------------------------------------------- #
# Liveness (not a trust surface)
# --------------------------------------------------------------------------- #

def test_allow_on_envoy_forwarded_suffix_path(gate_signing):
    """Envoy's HTTP ext_authz appends the original request path to the path_prefix
    (/authz + /api/transfer -> /authz/api/transfer); the sidecar answers any path
    under /authz, reading the decision from headers only."""
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    headers = {
        ENVELOPE_HEADER: canonical_json(env),
        INTERACTION_HEADER: canonical_json(
            interaction_for("transfer_funds", {"amount": 100, "to": "acct-42"})
        ),
    }
    r = client.post("/authz/api/transfer", headers=headers)
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


def test_healthz_is_live_even_when_unconfigured():
    client = TestClient(_app(None))
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_p01_duplicate_envelope_header_denied(gate_signing):
    """P-01: a VALID envelope presented as a DUPLICATE header is DENIED (treated
    absent), not first-wins ALLOWED. Fails if the envelope guard is reverted."""
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    body = canonical_json(env)
    inter = canonical_json(interaction_for("transfer_funds", {"amount": 100, "to": "acct-42"}))
    r = client.post("/authz", headers=[(ENVELOPE_HEADER, body), (ENVELOPE_HEADER, body),
                                       (INTERACTION_HEADER, inter)])
    assert r.status_code == 403


def test_p01_folded_envelope_header_fails_closed(gate_signing):
    """A comma-folded duplicate (one header, two JSON blobs) bypasses the duplicate
    detector but must still fail closed (unparseable -> absent -> DENY)."""
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    body = canonical_json(env)
    inter = canonical_json(interaction_for("transfer_funds", {"amount": 100, "to": "acct-42"}))
    r = client.post("/authz", headers=[(ENVELOPE_HEADER, body + "," + body),
                                       (INTERACTION_HEADER, inter)])
    assert r.status_code == 403
