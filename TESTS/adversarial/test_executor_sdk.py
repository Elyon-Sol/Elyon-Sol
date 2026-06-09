"""
Executor SDK tests (docs/restructure/18_latency_budget_and_sdk_spec.md, increment VL-078, B5).

Exercise IMPLEMENTATION/executor_sdk.py - the thin ExecutorGate that factors the executor
sequence (load + anchor-verify record -> verify_envelope -> replay de-dup) into one component.
These prove the SDK reproduces the executor refusal matrix faithfully (it composes the production
verifier, adding no decision of its own) and honors the VL-076 replay seam across instances.

Envelopes are produced by the REAL gate (pep), signed by the autouse `gate_signing` conftest
fixture's key; interactions are built with the canonical interaction_for from the MCP server.
"""

import json
import time

import pytest
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.executor_sdk import ExecutorGate, Decision
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.replay_cache import InMemoryReplayCache
from IMPLEMENTATION.reference_target import REF_TARGET_ANCHOR_MISMATCH
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ENVELOPE_ABSENT,
    REF_VERIFY_BINDING_MISMATCH,
    REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED,
    REF_VERIFY_SIGNATURE_EXPIRED,
    REF_VERIFY_REPLAY,
)

TARGET_ID = "mcp://elyon-sol/tool-server"


def _admit(tool, args):
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


def _gate(gate_signing, record_bytes=None, replay_cache=None):
    if record_bytes is None:
        record_bytes = open("EVIDENCE/published_hashes.json", "rb").read()
    return ExecutorGate(
        pinned_public_keys={gate_signing["key_id"]: gate_signing["public_key"]},
        target_id=TARGET_ID,
        record_bytes=record_bytes,
        replay_cache=replay_cache,
    )


def _check(gate, tool, args, envelope):
    return gate.check(envelope, interaction_for(tool, args))


def test_few_line_construction_and_honor(gate_signing):
    gate = _gate(gate_signing)  # record_bytes path - the documented few-line construction
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    d = _check(gate, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert isinstance(d, Decision)
    assert d.honored is True and d.reason == "REASSERTED_AND_BOUND"


def test_unattested_refused(gate_signing):
    d = _check(_gate(gate_signing), "transfer_funds", {"amount": 100, "to": "acct-42"}, None)
    assert d == Decision(False, REF_VERIFY_ENVELOPE_ABSENT)


def test_rebind_tool_refused(gate_signing):
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    d = _check(_gate(gate_signing), "delete_database", {"db": "prod"}, env)
    assert d == Decision(False, REF_VERIFY_BINDING_MISMATCH)


def test_rebind_args_refused(gate_signing):
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    d = _check(_gate(gate_signing), "transfer_funds", {"amount": 999999, "to": "acct-42"}, env)
    assert d == Decision(False, REF_VERIFY_BINDING_MISMATCH)


def test_replay_refused(gate_signing):
    gate = _gate(gate_signing)
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    assert _check(gate, "transfer_funds", {"amount": 100, "to": "acct-42"}, env).honored is True
    d = _check(gate, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert d == Decision(False, REF_VERIFY_REPLAY)


def test_drift_refused(gate_signing):
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    authentic = open("EVIDENCE/published_hashes.json", "rb").read()
    drifted = json.dumps(
        {**json.loads(authentic), "evaluator_sha256": "0" * 64}, sort_keys=True
    ).encode("utf-8")
    d = _check(_gate(gate_signing, record_bytes=drifted),
               "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert d == Decision(False, REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED)


def test_stale_refused(gate_signing):
    pep.DECISION_MAX_AGE_SECONDS = 1
    try:
        env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    finally:
        pep.DECISION_MAX_AGE_SECONDS = 300
    time.sleep(2)
    d = _check(_gate(gate_signing), "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert d == Decision(False, REF_VERIFY_SIGNATURE_EXPIRED)


def test_anchor_mismatch_fails_closed(gate_signing):
    rec = open("EVIDENCE/published_hashes.json", "rb").read()
    gate = ExecutorGate(
        pinned_public_keys={gate_signing["key_id"]: gate_signing["public_key"]},
        target_id=TARGET_ID,
        record_bytes=rec,
        pinned_root="0" * 64,  # wrong anchor -> fail closed before trusting currency
    )
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    d = _check(gate, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert d == Decision(False, REF_TARGET_ANCHOR_MISMATCH)


def test_shared_replay_cache_catches_cross_instance_replay(gate_signing):
    shared = InMemoryReplayCache()
    gate_a = _gate(gate_signing, replay_cache=shared)
    gate_b = _gate(gate_signing, replay_cache=shared)
    env = _admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    assert _check(gate_a, "transfer_funds", {"amount": 100, "to": "acct-42"}, env).honored is True
    d = _check(gate_b, "transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert d == Decision(False, REF_VERIFY_REPLAY)


def test_missing_record_args_raises():
    with pytest.raises(ValueError):
        ExecutorGate(pinned_public_keys={}, target_id=TARGET_ID)
