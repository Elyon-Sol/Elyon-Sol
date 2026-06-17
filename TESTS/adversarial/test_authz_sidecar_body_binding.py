"""
B-01 step-4 tests: the CUSTOM body-deriving interaction extractor
(docs/design/opa_sidecar_design.md section 5 CUSTOM mode; finding B-01).

The DEFAULT extractor reads the interaction from a client-controllable header,
which is unsafe INLINE in front of a body-carrying upstream: the header need not
match the bytes the upstream executes (B-01, cross-model convergent / rated
High). build_request_body_extractor closes that gap by deriving the interaction
- specifically context.args_sha256 - from the ext_authz REQUEST BODY (the bytes
Envoy forwards to the upstream), so the gate's binding check covers what is
actually EXECUTED.

These tests prove: a body that equals the args the envelope was minted for is
honored; a tampered body is refused at binding; the inline rebind attack (benign
header, different executed body) is DEFEATED by the body extractor while the
default header-read extractor would ALLOW it (the gap, documented for contrast);
and every malformed input fails closed. Envelopes are minted by the REAL gate
(pep), signed by the autouse `gate_signing` conftest key.
"""

import json
from datetime import timedelta

from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.published_source import anchor_sha256
from IMPLEMENTATION.authz_sidecar import (
    build_authz_sidecar_app,
    build_request_body_extractor,
    default_interaction_extractor,
    ENVELOPE_HEADER,
    INTERACTION_HEADER,
    DECISION_HEADER,
    REASON_HEADER,
    DECISION_ALLOW,
    DECISION_DENY,
)
from IMPLEMENTATION.verifier import REF_VERIFY_BINDING_MISMATCH

TARGET_ID = "mcp://elyon-sol/tool-server"
RECORD_PATH = "EVIDENCE/published_hashes.json"

# The static interaction parts interaction_for emits, mirrored in the deployer's
# declarative mapping so a body equal to the minted args binds.
MAPPING_AP = ["identity", "role"]
MAPPING_OP = ["session", "request"]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _record_bytes() -> bytes:
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


def _config(gate_signing, *, target_url=TARGET_ID):
    record_bytes = _record_bytes()
    return {
        "target_url": target_url,
        "record_bytes": record_bytes,
        "pinned_root_sha256": anchor_sha256(record_bytes),
        "pinned_public_keys": {gate_signing["key_id"]: gate_signing["public_key"]},
        "clock_skew": timedelta(0),
    }


def _body_extractor(*, tool="transfer_funds", args_field=None):
    return build_request_body_extractor(
        ap=MAPPING_AP,
        op=MAPPING_OP,
        expected_manifest_version="1.0",
        expected_manifest_sha256=manifest_sha256(),
        tool=tool,
        args_field=args_field,
    )


def _app(config, extractor):
    return build_authz_sidecar_app(
        config_provider=lambda: config, interaction_extractor=extractor
    )


def _post_body(client, envelope, body_obj, *, extra_headers=None):
    headers = {ENVELOPE_HEADER: canonical_json(envelope)}
    if extra_headers:
        headers.update(extra_headers)
    return client.post("/authz", content=json.dumps(body_obj), headers=headers)


# --------------------------------------------------------------------------- #
# ALLOW: a body equal to the minted args binds
# --------------------------------------------------------------------------- #

def test_body_extractor_allow_matching_body(gate_signing):
    """An envelope minted for args X, presented with a body that parses to X,
    is ALLOWED: context.args_sha256 derived from the body equals the envelope's."""
    args = {"amount": 100, "to": "acct-42"}
    client = TestClient(_app(_config(gate_signing), _body_extractor()))
    env = _admit("transfer_funds", args)
    r = _post_body(client, env, args)
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW
    assert r.headers[REASON_HEADER] == "REASSERTED_AND_BOUND"


def test_body_extractor_allow_with_reordered_body_keys(gate_signing):
    """canonical_json normalizes key order, so a body with the same content but
    different key order still binds (the digest is over canonical bytes)."""
    client = TestClient(_app(_config(gate_signing), _body_extractor()))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    # Different serialization order; same JSON object.
    r = _post_body(client, env, {"to": "acct-42", "amount": 100})
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


# --------------------------------------------------------------------------- #
# DENY: a tampered body breaks the binding
# --------------------------------------------------------------------------- #

def test_body_extractor_deny_tampered_body(gate_signing):
    """Same tool, but a body whose content differs from the minted args ->
    context.args_sha256 differs -> BINDING_MISMATCH. This is the executed-body
    binding the default header extractor cannot provide."""
    client = TestClient(_app(_config(gate_signing), _body_extractor()))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = _post_body(client, env, {"amount": 1_000_000, "to": "acct-42"})
    assert r.status_code == 403
    assert r.headers[DECISION_HEADER] == DECISION_DENY
    assert r.headers[REASON_HEADER] == REF_VERIFY_BINDING_MISMATCH


# --------------------------------------------------------------------------- #
# The headline B-01 inline rebind: benign header, different executed body
# --------------------------------------------------------------------------- #

def test_b01_inline_body_rebind_defeated_by_body_extractor(gate_signing):
    """B-01: an attacker presents a VALID envelope + a benign interaction HEADER
    (matching the envelope) but a DIFFERENT body for the upstream to execute. The
    body extractor binds to the EXECUTED body and REFUSES."""
    benign_args = {"amount": 100, "to": "acct-42"}
    env = _admit("transfer_funds", benign_args)
    benign_header = canonical_json(interaction_for("transfer_funds", benign_args))

    client = TestClient(_app(_config(gate_signing), _body_extractor()))
    r = _post_body(
        client, env, {"amount": 1_000_000, "to": "attacker"},
        extra_headers={INTERACTION_HEADER: benign_header},
    )
    assert r.status_code == 403
    assert r.headers[REASON_HEADER] == REF_VERIFY_BINDING_MISMATCH


def test_b01_default_header_extractor_allows_the_rebind_contrast(gate_signing):
    """Contrast (documents the gap B-01 step 4 closes): the DEFAULT header-read
    extractor trusts the benign interaction header and ALLOWs the same request
    whose body would execute a different action. This is why the default must NOT
    be placed inline in front of a body-carrying upstream."""
    benign_args = {"amount": 100, "to": "acct-42"}
    env = _admit("transfer_funds", benign_args)
    benign_header = canonical_json(interaction_for("transfer_funds", benign_args))

    client = TestClient(_app(_config(gate_signing), default_interaction_extractor))
    r = _post_body(
        client, env, {"amount": 1_000_000, "to": "attacker"},
        extra_headers={INTERACTION_HEADER: benign_header},
    )
    # The header matches the envelope, so the default extractor ALLOWs - it never
    # looked at the body. The body extractor (test above) is what closes this.
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


# --------------------------------------------------------------------------- #
# Declarative mapping variants: tool from path, args from a sub-field
# --------------------------------------------------------------------------- #

def test_body_extractor_tool_from_path(gate_signing):
    """tool={"from": "path"} derives the tool identity from the request path.
    The envelope is minted for that exact path-as-tool so it binds."""
    args = {"amount": 5, "to": "acct-9"}
    tool_path = "/authz/transfer_funds"
    env = _admit(tool_path, args)
    client = TestClient(
        _app(_config(gate_signing), _body_extractor(tool={"from": "path"}))
    )
    r = client.post(
        tool_path, content=json.dumps(args),
        headers={ENVELOPE_HEADER: canonical_json(env)},
    )
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


def test_body_extractor_args_from_body_field(gate_signing):
    """args_field='params' digests body['params'] as the args object (an
    enveloping request shape), so the envelope minted for those params binds."""
    params = {"amount": 7, "to": "acct-7"}
    env = _admit("transfer_funds", params)
    client = TestClient(
        _app(_config(gate_signing), _body_extractor(args_field="params"))
    )
    r = _post_body(client, env, {"jsonrpc": "2.0", "params": params})
    assert r.status_code == 200
    assert r.headers[DECISION_HEADER] == DECISION_ALLOW


# --------------------------------------------------------------------------- #
# Fail-closed on malformed input (every path -> DENY, never an exception)
# --------------------------------------------------------------------------- #

def test_body_extractor_unparseable_body_fail_closed(gate_signing):
    """A body that is not JSON -> extractor returns None -> the gate refuses
    (binding mismatch), never a 5xx and never an ALLOW."""
    client = TestClient(_app(_config(gate_signing), _body_extractor()))
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    r = client.post(
        "/authz", content="{not json",
        headers={ENVELOPE_HEADER: canonical_json(env)},
    )
    assert r.status_code == 403
    assert r.headers[DECISION_HEADER] == DECISION_DENY


def test_body_extractor_missing_args_field_fail_closed(gate_signing):
    """args_field set but absent from the body -> None -> fail closed."""
    env = _admit("transfer_funds", {"amount": 1, "to": "x"})
    client = TestClient(
        _app(_config(gate_signing), _body_extractor(args_field="params"))
    )
    r = _post_body(client, env, {"jsonrpc": "2.0"})  # no "params"
    assert r.status_code == 403
    assert r.headers[DECISION_HEADER] == DECISION_DENY


def test_body_extractor_tool_header_absent_fail_closed(gate_signing):
    """tool={"from": "header", "name": ...} with the header absent -> None ->
    fail closed."""
    env = _admit("transfer_funds", {"amount": 1, "to": "x"})
    extractor = _body_extractor(tool={"from": "header", "name": "X-Tool-Name"})
    client = TestClient(_app(_config(gate_signing), extractor))
    r = _post_body(client, env, {"amount": 1, "to": "x"})
    assert r.status_code == 403
    assert r.headers[DECISION_HEADER] == DECISION_DENY
