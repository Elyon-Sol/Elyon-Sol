"""
SES-6 (VL-144) adversarial tests: the sidecar's inline-posture declare-or-fail.

The gap (VL-141, OPEN -> fixed here): authz_sidecar defaulted to the header-read
interaction extractor, which is unsafe INLINE in front of a body-carrying
upstream (B-01: the client-controllable X-Elyon-Sol-Interaction header need not
match the bytes the upstream executes). The process cannot see its own topology,
so the fix is the R-02 declare-or-fail pattern: an inline deployment declares
ELYON_EXT_AUTHZ_INLINE=1, under which the header-read default is REFUSED
(REF_TARGET_NOT_CONFIGURED) and the body-deriving extractor is resolved from the
ELYON_INLINE_* mapping instead. Standalone (flag unset) is byte-behavior-unchanged.

Revert-catchers:
  - test_inline_declared_without_mapping_denies_header_attested_request goes RED
    if the inline guard is removed (the header path would ALLOW).
  - test_inline_declared_refuses_explicitly_injected_header_default goes RED if
    the guard only checks the resolved-from-env path.
Direction/regression pins:
  - standalone (unset / falsy flag) header path must still ALLOW.
  - the env-wired body extractor must bind to the BODY (tampered body DENIES,
    benign header rebind is ignored) — the property the declaration buys.
"""
import json
from datetime import timedelta

from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.authz_sidecar import (
    build_authz_sidecar_app,
    default_interaction_extractor,
    ENVELOPE_HEADER,
    INTERACTION_HEADER,
    DECISION_HEADER,
    REASON_HEADER,
    DECISION_ALLOW,
    DECISION_DENY,
    ENV_EXT_AUTHZ_INLINE,
    ENV_INLINE_AP,
    ENV_INLINE_OP,
    ENV_INLINE_MANIFEST_VERSION,
    ENV_INLINE_MANIFEST_SHA256,
    ENV_INLINE_TOOL,
    body_extractor_from_env,
    inline_declared,
)
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.published_source import anchor_sha256
from IMPLEMENTATION.reference_target import REF_TARGET_NOT_CONFIGURED
from IMPLEMENTATION.verifier import REF_VERIFY_BINDING_MISMATCH

TARGET_ID = "mcp://elyon-sol/tool-server"
RECORD_PATH = "EVIDENCE/published_hashes.json"


# --------------------------------------------------------------------------- #
# Helpers (mirroring test_authz_sidecar_body_binding.py)
# --------------------------------------------------------------------------- #

def _record_bytes():
    with open(RECORD_PATH, "rb") as f:
        return f.read()


def _admit(tool, args):
    """Drive the REAL gate to mint a signed envelope for (tool, args)."""
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


def _config(gate_signing):
    record_bytes = _record_bytes()
    return {
        "target_url": TARGET_ID,
        "record_bytes": record_bytes,
        "pinned_root_sha256": anchor_sha256(record_bytes),
        "pinned_public_keys": {gate_signing["key_id"]: gate_signing["public_key"]},
        "clock_skew": timedelta(0),
    }


def _app(config, extractor=None):
    """Build the app the way the deployable module-level app is built:
    extractor=None -> resolved per request from the declared posture."""
    return build_authz_sidecar_app(
        config_provider=lambda: config, interaction_extractor=extractor
    )


def _header_attested_post(client, envelope, tool, args):
    """A gate-attested request as the standalone deployment sees it: envelope +
    gate-normalized interaction, both in headers."""
    return client.post(
        "/authz",
        headers={
            ENVELOPE_HEADER: canonical_json(envelope),
            INTERACTION_HEADER: canonical_json(interaction_for(tool, args)),
        },
    )


def _set_inline_mapping(monkeypatch, *, tool="transfer_funds"):
    monkeypatch.setenv(ENV_EXT_AUTHZ_INLINE, "1")
    monkeypatch.setenv(ENV_INLINE_AP, "identity,role")
    monkeypatch.setenv(ENV_INLINE_OP, "session,request")
    monkeypatch.setenv(ENV_INLINE_MANIFEST_VERSION, "1.0")
    monkeypatch.setenv(ENV_INLINE_MANIFEST_SHA256, manifest_sha256())
    monkeypatch.setenv(ENV_INLINE_TOOL, tool)


ARGS = {"amount": 100, "to": "acct-42"}


# --------------------------------------------------------------------------- #
# 1. The declare-or-fail guard (revert-catchers)
# --------------------------------------------------------------------------- #

def test_inline_declared_without_mapping_denies_header_attested_request(
    gate_signing, monkeypatch
):
    """REVERT-CATCHER. Inline declared, no ELYON_INLINE_* mapping: a valid
    gate-attested request that the header-read default WOULD allow must be
    DENIED (REF_TARGET_NOT_CONFIGURED). If the SES-6 guard is removed, the
    resolver silently falls back to the header default and this ALLOWS -> RED."""
    monkeypatch.setenv(ENV_EXT_AUTHZ_INLINE, "1")
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", ARGS)
    r = _header_attested_post(client, env, "transfer_funds", ARGS)
    assert r.status_code == 403
    assert r.headers[DECISION_HEADER] == DECISION_DENY
    assert r.headers[REASON_HEADER] == REF_TARGET_NOT_CONFIGURED


def test_inline_declared_refuses_explicitly_injected_header_default(
    gate_signing, monkeypatch
):
    """REVERT-CATCHER. Under an inline declaration even an EXPLICITLY injected
    header-read default is refused: the client-controllable header must never
    be the binding source in front of a body-carrying upstream."""
    monkeypatch.setenv(ENV_EXT_AUTHZ_INLINE, "1")
    client = TestClient(_app(_config(gate_signing), default_interaction_extractor))
    env = _admit("transfer_funds", ARGS)
    r = _header_attested_post(client, env, "transfer_funds", ARGS)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_TARGET_NOT_CONFIGURED


def test_inline_with_partial_mapping_fails_closed(gate_signing, monkeypatch):
    """An INCOMPLETE inline mapping (missing manifest sha) resolves to None and
    every check DENIES — never a silent fallback to the header default."""
    _set_inline_mapping(monkeypatch)
    monkeypatch.delenv(ENV_INLINE_MANIFEST_SHA256)
    assert body_extractor_from_env() is None
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", ARGS)
    r = _header_attested_post(client, env, "transfer_funds", ARGS)
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_TARGET_NOT_CONFIGURED


# --------------------------------------------------------------------------- #
# 2. Standalone (undeclared) regression: byte-behavior-unchanged
# --------------------------------------------------------------------------- #

def test_standalone_header_path_unchanged(gate_signing, monkeypatch):
    """No declaration -> the deployable default resolves to the header-read
    extractor and a gate-attested request ALLOWs (the live standalone sidecar's
    behavior is unchanged by SES-6)."""
    monkeypatch.delenv(ENV_EXT_AUTHZ_INLINE, raising=False)
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", ARGS)
    r = _header_attested_post(client, env, "transfer_funds", ARGS)
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


def test_falsy_inline_flag_is_standalone(gate_signing, monkeypatch):
    """'0' does not declare inline (same truthy convention as the R-02 guard)."""
    monkeypatch.setenv(ENV_EXT_AUTHZ_INLINE, "0")
    assert inline_declared() is False
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", ARGS)
    r = _header_attested_post(client, env, "transfer_funds", ARGS)
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


# --------------------------------------------------------------------------- #
# 3. The declared-inline path binds to the BODY (what the declaration buys)
# --------------------------------------------------------------------------- #

def test_inline_mapping_allows_matching_body(gate_signing, monkeypatch):
    """Inline + full mapping: an envelope minted for args X presented with a
    body that parses to X is ALLOWED — no interaction header involved."""
    _set_inline_mapping(monkeypatch)
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", ARGS)
    r = client.post(
        "/authz",
        content=json.dumps(ARGS),
        headers={ENVELOPE_HEADER: canonical_json(env)},
    )
    assert r.status_code == 200, r.headers.get(REASON_HEADER)
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


def test_inline_mapping_denies_tampered_body_despite_benign_header(
    gate_signing, monkeypatch
):
    """The B-01 rebind is DEFEATED under the declared-inline default: a valid
    envelope for benign args + a benign interaction HEADER, but a TAMPERED body,
    is refused at binding — the header is not consulted."""
    _set_inline_mapping(monkeypatch)
    client = TestClient(_app(_config(gate_signing)))
    env = _admit("transfer_funds", ARGS)
    tampered = {"amount": 1000000, "to": "acct-evil"}
    r = client.post(
        "/authz",
        content=json.dumps(tampered),
        headers={
            ENVELOPE_HEADER: canonical_json(env),
            # the attacker still presents the benign interaction in the header
            INTERACTION_HEADER: canonical_json(interaction_for("transfer_funds", ARGS)),
        },
    )
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_BINDING_MISMATCH


def test_inline_tool_from_header_form(monkeypatch):
    """ELYON_INLINE_TOOL='header:<Name>' resolves the declarative header form;
    'path' resolves the path form; a bare name is a literal."""
    _set_inline_mapping(monkeypatch, tool="header:X-Tool")
    assert body_extractor_from_env() is not None
    _set_inline_mapping(monkeypatch, tool="path")
    assert body_extractor_from_env() is not None
    monkeypatch.setenv(ENV_INLINE_TOOL, "header:")   # malformed -> fail closed
    assert body_extractor_from_env() is None
