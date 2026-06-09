"""
Real MCP server tests (docs/restructure/17_mcp_server_spec.md, increment VL-077, B4).

Exercise IMPLEMENTATION/mcp_server.py - the MCP `tools/call` server with the production
admissibility gate on tool execution. These drive handle_message directly (the JSON-RPC
dispatch) through the initialize handshake and the full refusal matrix; the genuinely-two-
process real-stdio demonstration is EVIDENCE/proofs/mcp_server_001_runner.py.

The wedge property on the MCP surface: the side-effecting tool fires exactly once (the admitted
call) and is refused - unfired - when the call is un-attested, rebound (different tool or args),
drifted, stale, or replayed. Envelopes are produced by the REAL gate (pep) and ride in the
tools/call params _meta block, mirroring the production header push.
"""

import json
import time

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.published_source import anchor_sha256
from IMPLEMENTATION.mcp_server import (
    ServerState,
    handle_message,
    interaction_for,
    ENVELOPE_META_KEY,
    EXECUTED_META_KEY,
    REASON_META_KEY,
    JSONRPC_NOT_INITIALIZED,
    PROTOCOL_VERSION,
)
from IMPLEMENTATION.reference_target import REF_TARGET_NOT_CONFIGURED
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ENVELOPE_ABSENT,
    REF_VERIFY_BINDING_MISMATCH,
    REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED,
    REF_VERIFY_SIGNATURE_EXPIRED,
    REF_VERIFY_REPLAY,
)

TARGET_ID = "mcp://elyon-sol/tool-server"
GATE_KID = "gate-mcp-test-001"


@pytest.fixture
def gate_signing():
    priv = Ed25519PrivateKey.generate()
    pep._INJECTED_SIGNING_KEY = (priv, GATE_KID)
    yield priv
    pep._INJECTED_SIGNING_KEY = None
    pep.DECISION_MAX_AGE_SECONDS = 300


def _admit(tool, args):
    """Drive the REAL gate (pep) to admit a tool call; return the signed envelope."""
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


def _state(gate_priv, record_bytes=None):
    if record_bytes is None:
        record_bytes = open("EVIDENCE/published_hashes.json", "rb").read()
    config = {
        "pinned_public_keys": {GATE_KID: gate_priv.public_key()},
        "record_bytes": record_bytes,
        "pinned_root": anchor_sha256(record_bytes),
        "target_id": TARGET_ID,
    }
    s = ServerState(config)
    # Complete the handshake.
    handle_message(s, {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}})
    handle_message(s, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    return s


def _call(state, tool, args, envelope, msg_id=1):
    params = {"name": tool, "arguments": args}
    if envelope is not None:
        params["_meta"] = {ENVELOPE_META_KEY: envelope}
    resp = handle_message(
        state, {"jsonrpc": "2.0", "id": msg_id, "method": "tools/call", "params": params}
    )
    meta = resp["result"]["_meta"]
    return meta[EXECUTED_META_KEY], meta[REASON_META_KEY]


# --------------------------------------------------------------------------
# Protocol handshake
# --------------------------------------------------------------------------

def test_initialize_returns_protocol_and_capabilities(gate_signing):
    s = ServerState(None)
    resp = handle_message(s, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    r = resp["result"]
    assert r["protocolVersion"] == PROTOCOL_VERSION
    assert "tools" in r["capabilities"]
    assert r["serverInfo"]["name"] == "elyon-sol-gated-tools"


def test_tools_call_before_initialize_is_protocol_error(gate_signing):
    s = ServerState(None)  # not initialized, no handshake
    resp = handle_message(
        s,
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
         "params": {"name": "transfer_funds", "arguments": {}}},
    )
    assert resp["error"]["code"] == JSONRPC_NOT_INITIALIZED
    assert s.executed == []


def test_initialized_notification_produces_no_response(gate_signing):
    s = ServerState(None)
    assert handle_message(s, {"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert s.initialized is True


def test_tools_list_after_handshake(gate_signing):
    s = _state(gate_signing)
    resp = handle_message(s, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = [t["name"] for t in resp["result"]["tools"]]
    assert "transfer_funds" in names


# --------------------------------------------------------------------------
# The wedge matrix
# --------------------------------------------------------------------------

def test_admitted_call_executes_the_tool(gate_signing):
    s = _state(gate_signing)
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    executed, reason = _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert executed is True
    assert reason == "REASSERTED_AND_BOUND"
    assert s.executed == [{"tool": "transfer_funds", "args": {"amount": 100, "to": "acct-42"}}]


def test_replay_of_admitted_call_refused(gate_signing):
    s = _state(gate_signing)
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    executed, reason = _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, env, msg_id=2)
    assert executed is False
    assert reason == REF_VERIFY_REPLAY
    assert len(s.executed) == 1  # did not fire again


def test_unattested_call_refused(gate_signing):
    s = _state(gate_signing)
    executed, reason = _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, None)
    assert executed is False
    assert reason == REF_VERIFY_ENVELOPE_ABSENT
    assert s.executed == []


def test_rebind_to_different_tool_refused(gate_signing):
    s = _state(gate_signing)
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    executed, reason = _call(s, "delete_database", {"db": "prod"}, env)
    assert executed is False
    assert reason == REF_VERIFY_BINDING_MISMATCH
    assert s.executed == []


def test_rebind_to_different_args_refused(gate_signing):
    s = _state(gate_signing)
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    executed, reason = _call(s, "transfer_funds", {"amount": 999999, "to": "acct-42"}, env)
    assert executed is False
    assert reason == REF_VERIFY_BINDING_MISMATCH
    assert s.executed == []


def test_drifted_state_invalidates_admission(gate_signing):
    s = _state(gate_signing)
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    # The evaluator/policy state moved: a re-published record with a different
    # evaluator hash, anchored on its own bytes.
    authentic = open("EVIDENCE/published_hashes.json", "rb").read()
    drifted = json.dumps(
        {**json.loads(authentic), "evaluator_sha256": "0" * 64}, sort_keys=True
    ).encode("utf-8")
    s.config["record_bytes"] = drifted
    s.config["pinned_root"] = anchor_sha256(drifted)
    executed, reason = _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert executed is False
    assert reason == REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED
    assert s.executed == []


def test_stale_admission_refused(gate_signing):
    pep.DECISION_MAX_AGE_SECONDS = 1
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    pep.DECISION_MAX_AGE_SECONDS = 300
    s = _state(gate_signing)
    time.sleep(2)
    executed, reason = _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert executed is False
    assert reason == REF_VERIFY_SIGNATURE_EXPIRED
    assert s.executed == []


def test_unconfigured_server_fails_closed(gate_signing):
    s = ServerState(None)
    handle_message(s, {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}})
    handle_message(s, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    executed, reason = _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert executed is False
    assert reason == REF_TARGET_NOT_CONFIGURED
    assert s.executed == []


def test_executed_count_observability(gate_signing):
    s = _state(gate_signing)
    assert handle_message(s, {"jsonrpc": "2.0", "id": 9, "method": "elyon-sol/executed_count"})["result"]["count"] == 0
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert handle_message(s, {"jsonrpc": "2.0", "id": 10, "method": "elyon-sol/executed_count"})["result"]["count"] == 1


def test_tool_fires_exactly_once_across_matrix(gate_signing):
    """The observable: across one admitted call + every adversarial variant, the tool server's
    executed list contains exactly the one admitted action."""
    s = _state(gate_signing)
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)          # fires
    _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, env, 2)       # replay
    _call(s, "transfer_funds", {"amount": 100, "to": "acct-42"}, None, 3)      # un-attested
    _call(s, "delete_database", {"db": "prod"}, env, 4)                        # rebind tool
    _call(s, "transfer_funds", {"amount": 1, "to": "x"}, env, 5)              # rebind args
    assert s.executed == [{"tool": "transfer_funds", "args": {"amount": 100, "to": "acct-42"}}]
